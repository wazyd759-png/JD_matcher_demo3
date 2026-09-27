import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
"""评测 MatchReport 的 4 个指标：JSON 合法率、字段完整率、稳定性、响应时间。"""
import json
import time
import statistics
import requests
from pydantic import ValidationError
from schema import MatchReport

BASE = "http://127.0.0.1:8001"

JD = """AI 应用工程师（大模型方向）
职责：负责 RAG 问答系统设计与开发；优化检索效果；Prompt 工程；FastAPI 封装；Docker 部署
要求：Python、FastAPI、LangChain、LlamaIndex、Transformer 原理、Attention、RAG、Chroma/FAISS、Docker、Linux；有微调或 Agent 经验优先"""

RESUME = """张三
技能：Python（熟练）、PyTorch、LangChain、FastAPI、Chroma、Docker
项目1：RAG 求职知识库助手，检索命中率 100%，平均响应 1.46s
项目2：电商推荐系统，PyTorch 双塔模型，Recall@10 0.65
实习：后端开发，订单接口 P99 从 800ms 降至 120ms"""

REQUIRED_FIELDS = [
    "overall_score", "risk_level", "matched_skills",
    "missing_skills", "projects_to_build",
    "resume_rewrites", "risk_points", "interview_focus",
]

RUNS = 3


def run_once():
    t0 = time.time()
    r = requests.post(f"{BASE}/match",
                      json={"jd": JD, "resume": RESUME},
                      timeout=180)
    return r.json()["report"], time.time() - t0


print(f"评测 {RUNS} 次，评估稳定性...\n")

reports, times = [], []
legal_count = 0
complete_scores = []

for i in range(RUNS):
    try:
        report, elapsed = run_once()
        try:
            MatchReport(**report)
            legal = True
            legal_count += 1
        except ValidationError:
            legal = False
        complete = sum(1 for f in REQUIRED_FIELDS if report.get(f)) / len(REQUIRED_FIELDS)
        complete_scores.append(complete)
        reports.append(report)
        times.append(elapsed)
        print(f"  第 {i+1} 次：合法={legal}  分数={report['overall_score']}  "
              f"风险={report['risk_level']}  耗时={elapsed:.1f}s")
    except Exception as e:
        print(f"  第 {i+1} 次：失败 {e}")

print("\n===== 评测汇总 =====")
print(f"JSON 合法率     : {legal_count / RUNS:.1%}")
print(f"字段完整率      : {statistics.mean(complete_scores):.1%}")

if len(reports) >= 2:
    scores = [r["overall_score"] for r in reports]
    levels = [r["risk_level"] for r in reports]
    print(f"分数范围        : {min(scores)} ~ {max(scores)}（差 {max(scores)-min(scores)}）")
    print(f"分数标准差      : {statistics.stdev(scores):.2f}")
    print(f"风险等级一致    : {len(set(levels)) == 1}")

print(f"平均响应时间    : {statistics.mean(times):.1f}s")