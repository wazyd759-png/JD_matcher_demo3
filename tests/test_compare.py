import requests
import json

BASE = "http://127.0.0.1:8001"

resume = """张三
教育：XX大学 计算机科学 本科 2022-2026

技能：
- Python（熟练）、Go（了解）
- PyTorch、LangChain、FastAPI
- Chroma、DashScope、Docker
- MySQL、Redis

项目：
1. RAG 求职知识库助手（2024.09-2024.12）
   - 用 Chroma + DashScope Embedding 做向量检索
   - 用 bge-reranker-base 做 CrossEncoder 重排
   - FastAPI + Docker + Nginx 部署到阿里云 ECS
   - 检索命中率 100%，平均响应 1.46s

2. 电商推荐系统课程项目（2024.03-2024.06）
   - 用 PyTorch 实现双塔召回模型
   - Recall@10 达到 0.65

实习：某公司后端开发实习生（2024.06-2024.09）
   - 负责订单查询接口优化，P99 从 800ms 降到 120ms
"""

items = [
    {
        "name": "上海银行-算法工程",
        "jd": "总行金融科技岗位（算法工程）\n要求：Python、PyTorch、Transformer、RAG、Prompt工程、Docker、Linux、文档解析、智能体工具调用"
    },
    {
        "name": "某互联网-AI应用",
        "jd": "AI应用工程师\n要求：熟悉LLM、RAG、LangChain、FastAPI；有全栈经验优先；3年以上经验"
    },
    {
        "name": "某公司-传统后端",
        "jd": "Java后端开发\n要求：精通Java、Spring Boot、MySQL、Redis、分布式系统、5年经验"
    }
]

r = requests.post(f"{BASE}/compare", json={"items": items, "resume": resume}, timeout=300)
data = r.json()

print("=== 排名 ===")
for name in data["ranking"]:
    for item in data["results"]:
        if item["name"] == name and item["report"]:
            print(f"{name}: {item['report']['overall_score']} 分, 风险 {item['report']['risk_level']}")

print("\n=== 明细 ===")
for item in data["results"]:
    if item["report"]:
        rp = item["report"]
        print(f"\n【{item['name']}】")
        print(f"  分数: {rp['overall_score']}")
        print(f"  缺口: {', '.join(s['name'] for s in rp['missing_skills'])}")
        print(f"  建议做: {', '.join(p['title'] for p in rp['projects_to_build'][:2])}")
    else:
        print(f"\n【{item['name']}】失败: {item['error']}")