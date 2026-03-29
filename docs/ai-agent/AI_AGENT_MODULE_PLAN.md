# AI Agent 模块规划（Job Info Collector）

## 1. 目标与范围

本规划面向网站新增 AI Agent 能力，按两阶段实现：

1. 职位匹配问答
- 用户向 AI 描述背景和求职诉求。
- AI 从岗位列表中筛选、排序，并返回适合用户的岗位卡片。

2. 简历建议问答
- AI 基于用户画像与目标岗位，提供简历制作或修改建议。
- 输出包含可执行修改项，不做空泛建议。

本期只做模块化规划与目录骨架，不在本文件中绑定具体模型厂商。

## 2. 产品能力拆解

### 2.1 场景 A：岗位推荐

输入：
- 用户背景：学历、专业、年级、技能、项目经历、城市偏好、行业偏好。
- 用户目标：岗位方向、公司偏好、实习/校招、薪资预期（可选）。
- 当前岗位数据：来源 web/data/jobs.index.json + chunks 或 jobs.json 回退。

输出：
- 推荐岗位列表（Top K，默认 6-12 条）。
- 每个岗位的匹配原因（2-4 条）。
- 可直接渲染的岗位卡片字段（沿用现有前端卡片契约）。

### 2.2 场景 B：简历建议

输入：
- 用户基本信息与技能栈。
- 用户简历文本（可选，后续支持上传解析）。
- 目标岗位（用户指定或来自场景 A 推荐结果）。

输出：
- 简历差距诊断（技能、项目、关键词、表达）。
- 可执行修改建议（按优先级 P0/P1/P2）。
- 面向 ATS 的关键词补齐建议。
- 可复用的简历 bullet 模板（按岗位方向生成）。

## 3. 总体架构

采用 前端编排 + 后端 Agent 服务 的分层架构。

1. 前端层（web/assets/ai-agent）
- 聊天入口、对话状态管理、推荐卡片渲染、建议面板展示。
- 调用后端 AI API，不直接访问模型。

2. Agent 服务层（src/ai_agent）
- 意图识别与任务编排。
- 岗位检索与重排。
- 简历建议生成。
- 响应结构化输出（便于前端稳定渲染）。

3. 数据层
- 读取前端导出的岗位主数据。
- 后续可扩展向量索引（本期先关键词 + 规则重排）。

## 4. 推荐的模块目录

### 4.1 后端目录（已创建）

- src/ai_agent/api
  - 对外 HTTP 接口层。
- src/ai_agent/orchestrator
  - Agent 流程编排，串联检索、重排、生成。
- src/ai_agent/retrieval
  - 岗位召回（关键词、标签、城市、岗位类别过滤）。
- src/ai_agent/matching
  - 匹配打分与解释生成。
- src/ai_agent/resume_advisor
  - 简历诊断和修改建议模块。
- src/ai_agent/prompts
  - Prompt 模板与版本管理。
- src/ai_agent/schemas
  - 请求/响应数据模型定义。
- src/ai_agent/utils
  - 日志、文本清洗、通用工具。

### 4.2 前端目录（已创建）

- web/assets/ai-agent/components
  - 聊天面板、推荐列表、建议卡片组件。
- web/assets/ai-agent/services
  - 与 AI API 通信封装。
- web/assets/ai-agent/state
  - 对话与会话状态管理。
- web/assets/ai-agent/styles
  - AI 模块样式。

## 5. 数据契约设计（建议）

### 5.1 推荐请求

- session_id: string
- user_profile:
  - education, major, grade, skills[], experience_summary, city_preferences[], intent
- constraints:
  - recruit_type, job_category, city, company_whitelist[], company_blacklist[]
- top_k: number

### 5.2 推荐响应

- answer: string（给用户的自然语言总结）
- jobs: JobCard[]
  - company, title, recruit_type, job_category, work_city, detail_url, publish_time
  - match_score
  - match_reasons[]
- trace:
  - retrieved_count, filtered_count, model_version

### 5.3 简历建议请求

- session_id: string
- user_profile
- resume_text: string
- target_jobs: JobCard[] 或 job_ids[]

### 5.4 简历建议响应

- diagnosis:
  - strengths[], gaps[], missing_keywords[]
- suggestions:
  - p0[], p1[], p2[]
- rewritten_bullets[]
- follow_up_questions[]

## 6. 实施路线（建议按周）

### Phase 1：岗位推荐 MVP

目标：用户输入诉求后返回可点击岗位卡片。

实现要点：
1. 完成 API：/api/ai/recommend-jobs
2. 完成检索：城市/类别/关键词召回 + 简单打分
3. 输出结构化 jobs 列表，前端可复用现有卡片字段
4. 增加最小可观测日志（耗时、召回量、命中率）

验收标准：
- 能稳定返回 Top K 岗位。
- 推荐理由可解释且与岗位字段一致。
- 不影响现有筛选、排序、加载更多链路。

### Phase 2：简历建议 MVP

目标：用户基于目标岗位获取可执行简历优化建议。

实现要点：
1. 完成 API：/api/ai/resume-advice
2. 以目标岗位 JD 关键词生成差距分析
3. 输出优先级建议 + 改写示例
4. 前端支持建议分组展示和复制

验收标准：
- 建议内容结构化、可操作。
- 每条建议可追溯到岗位要求或用户信息。
- 响应时延在可接受范围（建议 < 8s）。

### Phase 3：增强能力（可选）

1. 向量检索与混合检索（BM25 + Embedding）
2. 多轮会话记忆（短期会话 + 用户画像持久化）
3. 简历文件上传解析（PDF/DOCX）
4. 推荐解释质量评测与自动回归测试

## 7. 工程与发布要求

1. 代码规范
- 目录边界清晰，禁止在前端直接拼接模型调用。
- Prompt 与业务逻辑分离，Prompt 放入 prompts 目录并版本化。

2. 可靠性
- API 必须有超时与失败兜底。
- 返回结构化错误码，前端可提示用户重试。

3. 性能
- 推荐流程默认限制 top_k 和文本长度。
- 记录召回耗时、重排耗时、总耗时。

4. 安全与合规
- 避免保存敏感个人信息。
- 记录日志时进行脱敏。

## 8. 里程碑交付物

1. 规划与文档
- 本文档：AI Agent 模块规划。

2. 目录骨架
- src/ai_agent/*
- web/assets/ai-agent/*

3. 下一步开发入口
- 优先落地 Phase 1 的接口与前端最小交互。

## 9. 下一步建议

1. 在 docs/DECISIONS.md 增加 AI Agent 技术选型决策记录。
2. 先实现 recommend-jobs 接口，再联调前端聊天入口。
3. 使用 30-50 条标注样本做推荐质量人工评估，确认再扩展到简历建议。
