# AI Agent Backend Modules

该目录承载网站 AI/Agent 后端能力，分为接口层、编排层、检索与建议能力层。

子目录职责：
- api: 对外接口定义与请求路由。
- orchestrator: 任务编排、意图分发。
- retrieval: 岗位召回与过滤。
- matching: 岗位打分与理由生成。
- resume_advisor: 简历诊断和建议。
- prompts: Prompt 模板与版本管理。
- schemas: 请求/响应数据结构。
- utils: 日志、清洗与公共方法。

开发顺序建议：
1. 先完成 retrieval + matching。
2. 再接 orchestrator + api。
3. 最后接入 resume_advisor。
