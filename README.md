# JD-简历匹配助手

输入多份 JD 和一份简历，输出缺口技能、补课优先级、项目改写建议和面试风险点。

## 线上地址
（部署后填）

## 功能
- 单 JD 匹配：`POST /match`
- 多 JD 对比：`POST /compare`（asyncio 并发处理）
- JD 文件上传：`POST /upload_jd`
- 前端支持动态添加多条 JD + 上传文件

## 核心设计
- **MatchReport schema**（pydantic）：8 个字段强约束
- **结构化输出**：ChatTongyi + `with_structured_output`
- **并发对比**：`asyncio.gather` + `run_in_threadpool`

## 输出字段
| 字段 | 说明 |
|---|---|
| overall_score | 0-100 整体匹配分 |
| risk_level | high/medium/low |
| matched_skills | 已匹配技能 + 证据 |
| missing_skills | 缺口技能 + 严重度 |
| projects_to_build | 建议做的项目（P0/P1/P2） |
| resume_rewrites | 简历改写建议（具体到句子） |
| risk_points | 面试风险 + 缓解建议 |
| interview_focus | 预测面试题 |

## 技术栈
- LLM：qwen-plus（DashScope）
- 框架：FastAPI + pydantic
- 并发：asyncio
- 前端：原生 HTML/CSS/JS

## 评测结果
跑评测 
cd D:\demo3\tests
python eval_match.py
| 指标 | 结果 |
|---|---|
| JSON 合法率 | 100% |
| 字段完整率 | 100% |
| 分数标准差 | 0.00（3 次完全一致） |
| 平均响应时间 | 23.1s |

## 本地运行
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# 配 .env：DASHSCOPE_API_KEY=sk-xxx, LLM_MODEL=qwen-plus
uvicorn main:app --port 8001
## 线上地址
http://121.40.172.119:8080/

## 评测结果
| 指标 | 结果 |
|---|---|
| JSON 合法率 | 100% |
| 字段完整率 | 100% |
| 分数标准差 | 0.00（3 次完全一致） |
| 平均响应时间 | 23.1s |