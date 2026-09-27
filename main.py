"""FastAPI 服务：JD-简历匹配助手（支持批量 JD 对比）。"""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from matcher import JDMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

matcher: Optional[JDMatcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global matcher
    matcher = JDMatcher(llm_model=os.getenv("LLM_MODEL", "qwen-plus"))
    yield
    matcher = None


app = FastAPI(title="JD-简历匹配助手", version="0.2.0", lifespan=lifespan)


# ---------------- 数据模型 ----------------
class MatchRequest(BaseModel):
    jd: str = Field(..., min_length=10)
    resume: str = Field(..., min_length=10)


class MatchResponse(BaseModel):
    report: Dict[str, Any]


class CompareItem(BaseModel):
    name: str
    jd: str = Field(..., min_length=10)


class CompareRequest(BaseModel):
    items: List[CompareItem] = Field(..., min_length=1, max_length=20)
    resume: str = Field(..., min_length=10)


# ---------------- 接口 ----------------
@app.get("/health")
async def health():
    return {"status": "ok", "matcher_ready": matcher is not None}


@app.post("/match", response_model=MatchResponse)
async def match(req: MatchRequest):
    if matcher is None:
        raise HTTPException(status_code=503, detail="匹配器未就绪")
    try:
        report = await run_in_threadpool(matcher.match, req.jd, req.resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"匹配失败: {exc}") from exc
    return MatchResponse(report=report)


@app.post("/compare")
async def compare(req: CompareRequest):
    """批量对比多个 JD，并发处理。"""
    if matcher is None:
        raise HTTPException(status_code=503, detail="匹配器未就绪")
    if not req.items:
        raise HTTPException(status_code=400, detail="至少一个 JD")

    # 并发处理：每个 JD 一个线程，互不阻塞
    async def run_one(item: CompareItem) -> Dict[str, Any]:
        try:
            report = await run_in_threadpool(matcher.match, item.jd, req.resume)
            return {"name": item.name, "report": report, "error": None}
        except Exception as exc:
            return {"name": item.name, "report": None, "error": str(exc)}

    results = await asyncio.gather(*[run_one(it) for it in req.items])

    # 按 overall_score 排序
    ranked = sorted(
        [r for r in results if r["report"]],
        key=lambda x: x["report"]["overall_score"],
        reverse=True,
    )

    # 构建对比表：所有 JD 的技能并集
    all_missing: Dict[str, set] = {}
    all_matched: Dict[str, set] = {}
    for r in results:
        if not r["report"]:
            continue
        name = r["name"]
        all_missing[name] = {s["name"] for s in r["report"]["missing_skills"]}
        all_matched[name] = {s["name"] for s in r["report"]["matched_skills"]}

    return {
        "results": results,
        "ranking": [r["name"] for r in ranked],
        "missing_union": sorted(set().union(*all_missing.values())) if all_missing else [],
    }


@app.post("/upload_jd")
async def upload_jd(file: UploadFile = File(...)):
    """上传单个 JD 文件，返回文本内容。"""
    suffix = os.path.splitext(file.filename or "")[1].lower()
    if suffix not in (".md", ".txt"):
        raise HTTPException(status_code=400, detail="仅支持 .md / .txt")

    content = (await file.read()).decode("utf-8", errors="ignore")
    if not content.strip():
        raise HTTPException(status_code=400, detail="文件内容为空")

    return {
        "filename": os.path.basename(file.filename or "jd.md"),
        "content": content,
    }


# ---------------- 静态前端 ----------------
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))