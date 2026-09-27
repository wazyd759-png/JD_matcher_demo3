"""JD-简历匹配核心：用 LLM + structured output 生成 MatchReport。"""
from __future__ import annotations

import os
from typing import Any, Dict

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate

from schema import MatchReport

MATCH_PROMPT = """你是一个资深的技术招聘顾问和简历优化专家。
请分析下面的简历与 JD，输出结构化的匹配报告。

分析原则：
1. 技能判断要基于简历里的具体证据，不要凭猜测。
2. missing_skills 里只放 JD 明确要求但简历没有的。
3. projects_to_build 要针对 missing_skills 里优先级最高的 2-3 项。
4. risk_points 要客观，指出真实的风险。
5. 所有中文描述简洁明了，每条不超过 60 字。

=== JD ===
{jd}

=== 简历 ===
{resume}
"""


class JDMatcher:
    def __init__(self, llm_model: str = "qwen-plus") -> None:
        # ChatTongyi 自动从环境变量 DASHSCOPE_API_KEY 读 key
        # 如果环境变量没设，ChatTongyi 会报错，报错信息里会明确说明
        if not os.getenv("DASHSCOPE_API_KEY"):
            raise RuntimeError(
                "未找到环境变量 DASHSCOPE_API_KEY。"
                "请在 .env 文件里设置，或用 $env:DASHSCOPE_API_KEY 临时设置。"
            )

        self.llm = ChatTongyi(model=llm_model)
        self.structured = self.llm.with_structured_output(MatchReport)
        self.prompt = ChatPromptTemplate.from_messages([("human", MATCH_PROMPT)])

    def match(self, jd: str, resume: str) -> Dict[str, Any]:
        if not jd.strip() or not resume.strip():
            raise ValueError("JD 和简历都不能为空")

        messages = self.prompt.format_messages(jd=jd, resume=resume)
        report: MatchReport = self.structured.invoke(messages)
        return report.model_dump()