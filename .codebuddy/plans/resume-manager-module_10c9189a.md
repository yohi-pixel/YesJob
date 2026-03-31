---
name: resume-manager-module
overview: 基于 Vue3 + localStorage + 校园手绘风开发简历管理模块。基本信息手动填写；PDF/Word上传仅解析经历与自我描述；支持模块拼接、岗位标签、跨简历项目经历深拷贝、AI按标签重写、多模板PDF导出、投递管理（公司+岗位+链接+简历关联）。后端仅提供解析和AI优化两个API。
todos:
  - id: init-backend-resume
    content: 创建 src/ai_agent/resume/ 后端模块（router、schemas、parser PDF/DOCX、splitter 仅提取经历+自我描述、extractor、optimizer），注册到 app.py
    status: completed
  - id: scaffold-vue-frontend
    content: 使用 [skill:frontend-design] 初始化 resume-manager/ Vue3+TS+Tailwind 项目，搭建侧边栏布局、路由、Pinia store、类型定义、手绘风骨架页面
    status: completed
  - id: implement-resume-list
    content: 实现我的简历列表页（创建/上传入口、便签卡片、模块状态指示器、删除/导出操作）
    status: completed
    dependencies:
      - scaffold-vue-frontend
  - id: implement-module-forms
    content: 实现三大模块编辑表单：BasicInfoForm（手动填写含成绩/课程/技能掌握度/获奖）、ExperienceForm（动态增删+解析填充+岗位标签）、SelfDescriptionForm（岗位标签），对接后端 parse API
    status: completed
    dependencies:
      - scaffold-vue-frontend
      - init-backend-resume
  - id: implement-advanced-features
    content: 实现模块拼接面板、项目经历库浏览页（跨简历深拷贝）、AI 优化按钮（标签选择+调用后端 optimize 接口）
    status: completed
    dependencies:
      - implement-module-forms
  - id: implement-export
    content: 实现多模板 PDF 导出预览页：校园手绘风模板、简洁表格模板，使用 html2canvas + jsPDF 前端生成
    status: completed
    dependencies:
      - implement-module-forms
  - id: implement-delivery
    content: 实现投递管理页：投递记录 CRUD（公司+岗位+链接+日期+关联简历）、搜索筛选、侧边栏导航入口
    status: completed
    dependencies:
      - scaffold-vue-frontend
  - id: docs-and-e2e
    content: 补充文档（docs/RESUME_MODULE_PRD.md、更新 CLAUDE.md 和 DECISIONS.md）+ 端到端功能验证
    status: completed
    dependencies:
      - implement-advanced-features
      - implement-export
      - implement-delivery
---

