---
name: resume-manager-module
overview: 基于 Vue3 + localStorage + 校园手绘风重新开发简历管理模块。三大核心模块（基本信息/经历与项目/自我描述）分别解析，支持模块拼接保存、多模板PDF导出、跨简历项目经历深拷贝复用、AI兜底解析与按标签重写优化。仅解析和AI功能通过后端API（DeepSeek），其余数据存储于localStorage。
design:
  architecture:
    framework: vue
  styleKeywords:
    - Campus Hand-drawn
    - Notebook Paper Texture
    - Colorful Sticky Notes
    - Hand-drawn SVG Decorations
    - Warm Pastel Palette
    - Playful Typography
    - Lo-fi Illustration
  fontSystem:
    fontFamily: ZCOOL XiaoWei, Noto Sans SC, sans-serif
    heading:
      size: 28px
      weight: 400
    subheading:
      size: 18px
      weight: 400
    body:
      size: 14px
      weight: 400
  colorSystem:
    primary:
      - "#4A7C59"
      - "#5D9CEC"
      - "#F5A623"
    background:
      - "#FFF8F0"
      - "#FFFFFF"
      - "#F5F0E8"
    text:
      - "#3D3D3D"
      - "#6B6B6B"
      - "#9E9E9E"
    functional:
      - "#E8F5E9"
      - "#FFF9C4"
      - "#E3F2FD"
      - "#FCE4EC"
      - "#FF6B6B"
todos:
  - id: init-backend-resume
    content: 创建 src/ai_agent/resume/ 后端模块（router、schemas、parser PDF/DOCX、splitter、extractor、optimizer），注册到现有 app.py
    status: pending
  - id: scaffold-vue-frontend
    content: 使用 [skill:frontend-design] 初始化 resume-manager/ Vue3+TS+Tailwind 项目，搭建路由、Pinia store、类型定义和页面骨架
    status: pending
  - id: implement-resume-list
    content: 实现我的简历列表页（创建/上传入口、简历卡片、模块状态展示、删除/导出操作）
    status: pending
    dependencies:
      - scaffold-vue-frontend
  - id: implement-module-forms
    content: 实现三大模块编辑表单：BasicInfoForm（含学业成绩/课程/技能掌握度/获奖）、ExperienceForm（动态增删）、SelfDescriptionForm，对接后端解析 API
    status: pending
    dependencies:
      - scaffold-vue-frontend
      - init-backend-resume
  - id: implement-advanced-features
    content: 实现模块拼接面板、项目经历库（跨简历深拷贝）、AI 优化按钮（标签选择+调用后端 optimize 接口）
    status: pending
    dependencies:
      - implement-module-forms
  - id: implement-export
    content: 实现多模板 PDF 导出预览页：校园手绘风模板、简洁表格模板，使用 html2canvas + jsPDF 前端生成
    status: pending
    dependencies:
      - implement-module-forms
  - id: docs-and-e2e
    content: 补充文档（docs/RESUME_MODULE_PRD.md、更新 CLAUDE.md 和 DECISIONS.md）+ 端到端功能验证
    status: pending
    dependencies:
      - implement-advanced-features
      - implement-export
---

## 产品概述

简历管理模块是 job_info_collector 项目的新增功能，提供简历全生命周期管理：上传解析、在线编辑、模块拼接保存、AI 优化、多模板导出 PDF。作为独立子项目开发，后续可并入主网站。

## Core Features

### 简历三大模块结构

简历按三大模块拆分：

- **基本信息模块**：姓名、联系方式、学历、专业、年级、**学业成绩**、**相关课程**、**技能与掌握程度**、**获奖与比赛**
- **经历与项目模块**：项目经历、工作经历、实习经历（支持跨简历深拷贝复用）
- **自我描述模块**：自我评价、求职意向、个人总结

### 核心交互

- PDF/Word 上传后端解析，按三大模块分别提取结构化数据
- 在线表单编辑器，支持从零创建或编辑解析结果
- **模块拼接**：用户自由选择模块组合，保存至"我的简历"
- **项目经历库**：所有已保存简历的项目经历汇聚为共享库，支持深拷贝新建
- **AI 能力**（复用 DeepSeek）：解析兜底（模块解析失败时 AI 辅助拆分）；按特定标签对项目和自我描述进行 AI 优化重写
- **多模板 PDF 导出**：校园手绘风模板、简洁表格模板等

### 数据存储

- 除 PDF 解析和 AI 优化需临时上传文件外，全部数据保存在 **localStorage**
- 后端仅提供解析 API 和 AI 优化 API，不负责 CRUD 和持久化存储

## Tech Stack Selection

### 前端

- **框架**: Vue 3 + TypeScript（Vite 构建）
- **UI**: 自定义组件 + Tailwind CSS（校园手绘风）
- **PDF 渲染/导出**: html2canvas + jsPDF（前端生成 PDF，无需后端）
- **图标**: Lucide Vue
- **PDF 前端预览**: pdf.js（用于上传后原始 PDF 预览）
- **路由**: Vue Router 4

### 后端（仅解析 + AI，挂载到现有 AI Agent）

- **框架**: FastAPI（注册到现有 `src/ai_agent/app.py`）
- **PDF 解析**: pdfplumber
- **DOCX 解析**: python-docx
- **AI**: 复用现有 `LLMClient`（DeepSeek）
- **模型结构化拆分**: DeepSeek chat completion + JSON 输出
- **新依赖**: pdfplumber, python-docx 追加到 requirements.txt

### 数据存储

- **前端**: localStorage（简历 CRUD、模块数据、项目经历库）
- **后端无持久化**: 仅临时处理上传文件，处理完即丢弃

## Implementation Approach

### 架构策略

前端为主、后端为辅的架构：

1. **前端承担全部数据管理**：所有简历 CRUD、模块拼接、项目经历库均在 localStorage 中管理
2. **后端仅提供两个能力**：文件解析（PDF/DOCX → 结构化 JSON）和 AI 优化重写
3. **AI Agent 集成**：复用现有 `LLMClient`、`ModelConfig`、`sanitize` 工具，新增简历解析和优化路由

### 关键技术决策

1. **PDF 导出前端化**：使用 html2canvas + jsPDF 在浏览器端生成 PDF，支持多模板切换，无需后端参与
2. **三模块解析策略**：先用正则/规则按中文简历常见标题（教育背景、项目经历、自我评价等）粗分模块，解析失败时调用 DeepSeek AI 做兜底拆分
3. **深拷贝项目经历**：前端 JSON.parse(JSON.stringify()) 深拷贝，从 localStorage 的项目经历库中选取并复制到当前编辑简历
4. **AI 优化按标签重写**：前端将项目描述/自我描述 + 目标标签发送到后端，后端调用 DeepSeek 按标签（如 STAR 结构化、量化成果突出、技术栈对齐等）进行重写

### 与现有 AI Agent 的集成

```mermaid
graph LR
    subgraph 前端 [resume-manager/ Vue3 前端]
        LS[localStorage<br/>简历数据+经历库]
    end

    subgraph 后端 [src/ai_agent/ FastAPI]
        PARSER[/api/resume/parse<br/>PDF/DOCX解析]
        OPT[/api/resume/optimize<br/>AI优化重写]
        LLM[LLMClient<br/>DeepSeek]
    end

    LS -->|上传文件| PARSER
    PARSER -->|结构化JSON| LS
    LS -->|文本+标签| OPT
    OPT --> LLM
    LLM -->|优化结果| OPT
    OPT -->|重写文本| LS
```

后端新增路由挂载到现有 `app.py`，通过 `app.include_router(resume_router)` 自动注册。复用 `LLMClient` 做 AI 调用，复用 `sanitize_text` 做输入清洗。

## Implementation Notes

- **向后兼容**：新增 `src/ai_agent/resume/` 不影响现有爬虫、分析、AI Agent 代码
- **安全性**：复用 `ai_agent/utils/security.py` 的 sanitize 工具函数
- **日志**：复用现有 logging 模式，解析和 AI 调用错误记录到控制台
- **性能**：PDF 解析在后端完成，大文件（>10MB）返回解析超时提示；AI 优化设置 25s 超时；localStorage 存储限制约 5MB，足够存储数百份简历的结构化数据
- **前端 PDF 导出**：html2canvas 将模板 DOM 渲染为 canvas，jsPDF 转为 PDF；多模板通过切换不同 CSS class 实现
- **部署**：后端启动命令不变，简历路由自动挂载；前端 `npm run dev` 独立运行

## Architecture Design

```
resume-manager/                         # Vue3 前端独立子项目
├── src/
│   ├── views/                          # 页面视图
│   ├── components/                     # 通用组件
│   ├── composables/                    # 组合式函数（数据管理）
│   ├── stores/                         # localStorage 状态管理
│   └── utils/                          # 工具函数

src/ai_agent/resume/                    # 后端模块（挂载到现有 FastAPI）
├── router.py                           # /api/resume/parse + /api/resume/optimize
├── schemas.py                          # 请求/响应模型
├── parser/                             # PDF/DOCX 解析器 + 模块拆分
└── optimizer.py                        # AI 优化重写逻辑
```

## Directory Structure

```
resume-manager/                         # [NEW] Vue3 前端独立子项目
├── package.json                        # [NEW] 前端依赖（vue3, vue-router, pinia, tailwindcss, jspdf, html2canvas）
├── vite.config.ts                      # [NEW] Vite 配置，API 代理到后端 8001
├── tsconfig.json                       # [NEW] TypeScript 配置
├── tailwind.config.js                  # [NEW] Tailwind 配置
├── postcss.config.js                   # [NEW] PostCSS 配置
├── index.html                          # [NEW] 入口 HTML
├── src/
│   ├── main.ts                         # [NEW] Vue 入口
│   ├── App.vue                         # [NEW] 根组件 + 路由
│   ├── router/index.ts                 # [NEW] Vue Router 配置
│   ├── stores/
│   │   └── resumeStore.ts              # [NEW] Pinia store，localStorage 读写
│   ├── types/
│   │   └── resume.ts                   # [NEW] 三大模块 + 子模块 TypeScript 类型
│   ├── api/
│   │   └── resume.ts                   # [NEW] 后端 API 调用封装（parse, optimize）
│   ├── composables/
│   │   ├── useResumeEditor.ts          # [NEW] 简历编辑组合式函数
│   │   └── useProjectLibrary.ts        # [NEW] 项目经历库 + 深拷贝
│   ├── views/
│   │   ├── ResumeListView.vue          # [NEW] 我的简历列表页
│   │   ├── ResumeEditView.vue          # [NEW] 简历编辑页（创建+编辑）
│   │   ├── ResumeDetailView.vue        # [NEW] 简历详情页
│   │   ├── ProjectLibraryView.vue      # [NEW] 项目经历库页
│   │   └── ExportPreviewView.vue       # [NEW] 导出预览页（多模板切换）
│   ├── components/
│   │   ├── ModuleCard.vue              # [NEW] 模块卡片（基本信息/经历/自我描述）
│   │   ├── BasicInfoForm.vue           # [NEW] 基本信息表单（含学业成绩/课程/技能掌握度/获奖）
│   │   ├── ExperienceForm.vue          # [NEW] 经历与项目表单（动态增删）
│   │   ├── SelfDescriptionForm.vue     # [NEW] 自我描述表单
│   │   ├── ModuleAssembler.vue         # [NEW] 模块拼接面板
│   │   ├── ProjectSelector.vue         # [NEW] 项目经历选择器（从经历库深拷贝）
│   │   ├── UploadZone.vue              # [NEW] 文件上传拖拽区域
│   │   ├── AiOptimizeButton.vue        # [NEW] AI 优化按钮 + 标签选择
│   │   ├── PdfPreview.vue              # [NEW] PDF 原始预览
│   │   ├── ExportTemplate.vue          # [NEW] PDF 导出模板容器
│   │   └── HanddrawnTemplate.vue       # [NEW] 校园手绘风导出模板
│   ├── utils/
│   │   ├── localStorage.ts             # [NEW] localStorage 封装（含容量检查）
│   │   ├── deepCopy.ts                 # [NEW] 深拷贝工具
│   │   └── pdfExport.ts                # [NEW] html2canvas + jsPDF 导出封装
│   ├── styles/
│   │   ├── main.css                    # [NEW] Tailwind 入口 + 全局样式
│   │   └── handdrawn.css               # [NEW] 校园手绘风专用样式
│   └── assets/
│       └── handdrawn/                  # [NEW] 手绘风 SVG 装饰素材（边框/图标/分割线）

src/ai_agent/resume/                    # [NEW] 后端简历模块
├── __init__.py                         # [NEW] 模块初始化
├── router.py                           # [NEW] API 路由：POST /api/resume/parse, POST /api/resume/optimize
├── schemas.py                          # [NEW] Pydantic 模型：ParseRequest, ParseResponse, OptimizeRequest, OptimizeResponse
├── parser/
│   ├── __init__.py                     # [NEW]
│   ├── base.py                         # [NEW] 解析器基类
│   ├── pdf_parser.py                   # [NEW] PDF 文本提取 + 模块拆分
│   ├── docx_parser.py                  # [NEW] DOCX 文本提取 + 模块拆分
│   ├── splitter.py                     # [NEW] 基于正则的中文简历模块拆分器
│   └── extractor.py                    # [NEW] 结构化字段提取（姓名/手机/邮箱/技能等）
└── optimizer.py                        # [NEW] AI 优化重写（调用 LLMClient）

src/ai_agent/app.py                     # [MODIFY] 注册 resume_router

requirements.txt                        # [MODIFY] 追加 pdfplumber, python-docx

docs/
└── RESUME_MODULE_PRD.md                # [NEW] 简历模块产品需求文档
```

## Key Code Structures

### 后端请求/响应模型 (src/ai_agent/resume/schemas.py)

```python
class ParseRequest(BaseModel):
    file: UploadFile                    # PDF 或 DOCX 文件
    file_type: Literal["pdf", "docx"]

class ParseResponse(BaseModel):
    success: bool
    raw_text: str = ""                  # 完整提取文本
    basic_info: dict = {}               # 基本信息（姓名/手机/邮箱/学历/专业/年级/成绩/课程/技能/获奖）
    experiences: list[dict] = []        # 经历与项目列表
    self_description: dict = {}         # 自我描述
    parse_method: Literal["rule", "ai", "hybrid"]  # 解析方式
    warnings: list[str] = []            # 解析警告

class OptimizeRequest(BaseModel):
    text: str                           # 待优化文本
    tags: list[str]                     # 优化标签（star/quantify/tech-align/concise 等）
    context: str = ""                   # 上下文（岗位JD或简历其他部分）

class OptimizeResponse(BaseModel):
    optimized_text: str
    tags_used: list[str]
```

### 前端核心类型 (resume-manager/src/types/resume.ts)

```typescript
interface ResumeModule {
  type: "basicInfo" | "experience" | "selfDescription"
  enabled: boolean                     // 是否拼接到我的简历
  data: BasicInfo | Experience[] | SelfDescription
}

interface BasicInfo {
  name: string; phone: string; email: string;
  education: string; major: string; grade: string;
  academicScore: string;               // 学业成绩/ GPA
  relevantCourses: string[];           // 相关课程
  skills: SkillItem[];                 // 技能与掌握程度
  awards: AwardItem[];                 // 获奖与比赛
}

interface SkillItem {
  name: string;
  level: "了解" | "熟悉" | "掌握" | "精通"
}

interface AwardItem {
  name: string; level: string; date: string; description: string
}

interface Experience {
  id: string;                          // UUID，用于深拷贝追踪
  type: "project" | "work" | "internship";
  title: string; organization: string; role: string;
  startDate: string; endDate: string;
  description: string;                 // 支持AI优化重写
  techStack: string[];
}

interface SelfDescription {
  selfEvaluation: string;
  careerObjective: string;
  personalSummary: string;
}
```

## Design Style

采用**校园手绘风**（Campus Hand-drawn Style），营造轻松活泼的校园求职氛围。

### 视觉特征

- **手绘边框**: SVG 实现的波浪线、虚线边框、手绘箭头装饰
- **纸张质感**: 米白色背景 (#FFF8F0) 搭配轻微纸张纹理
- **手写字体**: 标题使用 ZCOOL XiaoWei（站酷小薇体），正文使用 Noto Sans SC
- **彩色便签**: 不同模块使用淡彩色便签卡片（淡黄 #FFF9C4 / 淡绿 #E8F5E9 / 淡蓝 #E3F2FD / 淡粉 #FCE4EC）
- **手绘图标**: 使用自定义 SVG 图标，模仿铅笔/马克笔手绘风格
- **胶带装饰**: 模块卡片角落使用"透明胶带"效果固定
- **活页夹效果**: 顶部导航模拟笔记本活页夹环

### 交互风格

- 卡片悬浮时轻微倾斜旋转（2-3度）
- 按钮按下时模拟手按纸面效果（scale + 阴影变化）
- AI 优化加载时显示手绘风格的"思考中..."动画（铅笔写字动画）
- 模块拼接拖拽时有虚线占位效果
- Toast 通知采用便利贴样式

## Agent Extensions

### Skill: frontend-design

- **Purpose**: 开发 Vue3 前端页面时使用，生成校园手绘风高质量 UI 代码
- **Expected outcome**: 产出符合校园手绘风设计规范的精美 Vue3 组件代码

### Skill: brainstorming

- **Purpose**: 在实现复杂交互（模块拼接、深拷贝、AI 优化流程）前进行设计探索
- **Expected outcome**: 明确交互流程和边界情况，减少实现返工

### SubAgent: code-explorer

- **Purpose**: 在开发过程中搜索现有 AI Agent 代码中的可复用模式（LLMClient、sanitize、路由注册方式等）
- **Expected outcome**: 快速定位可复用的工具函数和接口定义，确保与现有代码风格一致