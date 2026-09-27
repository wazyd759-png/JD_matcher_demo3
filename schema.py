"""MatchReport 数据模型：定义 JD-简历匹配的结构化输出。"""
from typing import List, Literal
from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    name: str = Field(..., description="技能名称，如 Python、RAG、Docker")
    required_level: Literal["must", "nice"] = Field(..., description="JD 要求的级别")
    in_resume: bool = Field(..., description="简历里是否有直接或间接证据")
    gap: Literal["none", "low", "medium", "high"] = Field(
        ..., description="缺口严重程度"
    )
    evidence: str = Field("", description="简历里的证据原文，最多 50 字")


class ProjectSuggestion(BaseModel):
    title: str = Field(..., description="项目标题，一句话")
    why: str = Field(..., description="为什么需要做这个项目，对应 JD 的哪条要求")
    stack: List[str] = Field(..., description="技术栈列表")
    est_hours: int = Field(..., description="预估小时数")
    priority: Literal["P0", "P1", "P2"] = Field(..., description="优先级")


class RiskPoint(BaseModel):
    category: str = Field(..., description="风险类别：技术深度/项目相关性/经历空档/软技能")
    description: str = Field(..., description="风险描述")
    severity: Literal["high", "medium", "low"]
    mitigation: str = Field(..., description="缓解建议")


class ResumeRewrite(BaseModel):
    section: str = Field(..., description="要改的简历模块，如 项目经历/技能栏")
    issue: str = Field(..., description="当前问题")
    suggestion: str = Field(..., description="改写建议，要具体到句子")


class MatchReport(BaseModel):
    jd_title: str
    jd_company: str
    overall_score: int = Field(..., ge=0, le=100, description="整体匹配分")
    risk_level: Literal["high", "medium", "low"]
    matched_skills: List[SkillItem]
    missing_skills: List[SkillItem]
    projects_to_build: List[ProjectSuggestion]
    resume_rewrites: List[ResumeRewrite]
    risk_points: List[RiskPoint]
    interview_focus: List[str] = Field(..., description="面试可能追问的方向")