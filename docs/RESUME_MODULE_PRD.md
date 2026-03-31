# 简历管理模块 PRD

## 1. 概述

简历管理模块为 job_info_collector 项目新增简历管理能力，支持简历上传解析、在线编辑、AI 优化、多模板导出和投递管理。

## 2. 核心功能

### 2.1 三大模块

| 模块 | 数据来源 | 说明 |
|------|----------|------|
| 基本信息 | 手动填写 | 姓名、联系方式、学历、专业、年级、GPA、课程、技能、获奖 |
| 经历与项目 | PDF/DOCX 解析 + 手动编辑 | 项目经历、实习经历、工作经历，支持岗位标签 |
| 自我描述 | PDF/DOCX 解析 + 手动编辑 | 自我评价、求职意向、个人总结，支持岗位标签 |

### 2.2 功能清单

- **简历 CRUD**：创建、编辑、复制（深拷贝）、删除
- **PDF/DOCX 解析**：上传文件自动提取经历与自我描述（正则拆分 + AI 兜底）
- **模块拼接**：展示各模块内容状态，有内容的模块包含在导出中
- **岗位标签**：为经历和自我描述打标签（如"后端开发"、"产品经理"）
- **AI 优化**：按标签调用 DeepSeek 重写经历描述和自我描述
- **项目经历库**：所有简历经历汇聚为共享库，支持跨简历深拷贝
- **多模板导出**：校园手绘风、简洁表格两种 PDF 模板
- **投递管理**：记录公司、岗位、链接、日期、关联简历

## 3. 技术架构

```
前端 (resume-manager/)          后端 (src/ai_agent/resume/)
Vue3 + TS + Pinia        →      FastAPI
Tailwind CSS                     pdfplumber + python-docx
html2canvas + jsPDF              DeepSeek
localStorage                     2 个 API 端点
```

### 3.1 后端 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/resume/parse` | 上传文件，返回解析结果 |
| POST | `/api/resume/optimize` | AI 重写指定内容 |

### 3.2 前端路由

| 路由 | 页面 |
|------|------|
| `/` | 简历列表 |
| `/resume/edit/:id` | 简历编辑 |
| `/resume/export/:id` | 导出预览 |
| `/experience-library` | 项目经历库 |
| `/delivery` | 投递管理 |

## 4. 启动方式

### 后端
```bash
cd src
pip install -r ../requirements.txt
uvicorn ai_agent.app:app --reload --port 8000
```

### 前端
```bash
cd resume-manager
npm install
npm run dev
```

访问 http://localhost:5174

## 5. 数据存储

所有简历和投递数据存储在浏览器 localStorage：
- `resume-manager-resumes`：简历数据
- `resume-manager-deliveries`：投递记录

## 6. 并入主网站路径

1. 前端 `npm run build` → 构建产物放入 `web/resume/`
2. 后端路由已注册到 `src/ai_agent/app.py`，无需额外配置
3. 后端部署到云服务，前端静态资源走 GitHub Pages
