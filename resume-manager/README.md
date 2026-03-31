# Resume Manager — 简历管理模块

校园手绘风的简历管理 SPA，支持简历上传解析、在线编辑、AI 优化、多模板导出和投递管理。

## 快速开始

```bash
npm install
npm run dev
# 访问 http://localhost:5174
```

需要后端服务运行在 http://localhost:8000（提供解析和 AI 优化 API）。

## 功能

- 📄 简历 CRUD（创建、编辑、复制、删除）
- 📤 PDF/DOCX 上传解析（自动提取经历与自我描述）
- ✏️ 三大模块编辑（基本信息/经历与项目/自我描述）
- 🏷️ 岗位标签系统
- ✨ DeepSeek AI 优化（按标签重写）
- 📚 项目经历库（跨简历深拷贝）
- 🎨 多模板 PDF 导出（手绘风/简洁表格）
- 📋 投递管理（公司+岗位+链接+简历关联）

## 技术栈

- Vue 3 + TypeScript
- Pinia（状态管理）
- Tailwind CSS v4（手绘风样式）
- html2canvas + jsPDF（前端 PDF 生成）
- lucide-vue-next（图标）
