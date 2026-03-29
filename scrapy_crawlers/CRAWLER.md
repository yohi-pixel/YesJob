# job_info_collector 爬虫模块总览与维护手册

> 最后更新：2026-03-19
> 适用范围：`scrapy_crawlers/`（Scrapy 多站点爬虫）+ 与前端数据导出的接口约定

---

## 1. 文档目标

本文件是爬虫模块的统一入口，解决三件事：

1. 约定统一数据接口（供前端与后续分析模块消费）。
2. 说明各站点爬虫的实现逻辑与关键依赖。
3. 提供可执行的维护 Runbook（运行、验收、排障、变更流程）。

---

## 2. 模块边界与目录

### 2.1 爬虫模块目录

```text
scrapy_crawlers/
├── scrapy.cfg
├── CRAWLER.md
└── crawlers/
		├── items.py
		├── pipelines.py
		├── settings.py
		└── spiders/
				├── tencent.py
				├── bilibili.py
				├── netease.py
				├── mihoyo.py
				└── antgroup.py
```

### 2.2 上下游关系

- 上游：各招聘站点公开接口（列表 + 详情，部分站点带 token/CSRF）。
- 本模块输出：统一写入 `data/jobs.csv`、`data/jobs.jsonl`（增量去重）。
- 下游消费：`src/export_frontend_jobs.py` 将 `data/jobs.jsonl` 导出为前端数据文件（`web/data/*.json`）。

说明：字节跳动抓取当前由 `src/bytedance_campus_scraper.py`（Playwright）承担，不属于本目录 Scrapy spider。

---

## 3. 统一数据契约（核心接口规范）

### 3.1 爬虫输出字段（JobItem 标准）

所有 spider 必须输出以下字段（允许空值，但字段名不得变更）：

| 字段 | 类型 | 说明 |
|------|------|------|
| company | string | 公司名 |
| job_id | string | 站点职位唯一 ID |
| title | string | 岗位标题 |
| recruit_type | string | 招聘类型/项目 |
| job_category | string | 岗位类别 |
| job_function | string | 职能/岗位性质 |
| work_city | string | 主工作城市 |
| work_cities | string[] | 工作城市列表 |
| team_intro | string | 团队/部门介绍 |
| responsibilities | string | 岗位职责 |
| requirements | string | 岗位要求 |
| bonus_points | string | 加分项 |
| tags | string[] | 标签 |
| publish_time | string | 发布时间（站点原值） |
| detail_url | string | 职位详情页链接 |
| fetched_at | string | 抓取时间（ISO 8601） |
| source_page | number | 来源分页页码 |

### 3.2 增量写入与去重规则

- 统一输出文件：
	- `data/jobs.csv`
	- `data/jobs.jsonl`
- 去重主键：`(company, job_id)`
- 去重时机：
	- 启动时加载历史 `jobs.csv` 形成已存在主键集合。
	- 运行时 `process_item` 再做本轮内存去重，重复项直接丢弃。

结果保证：同一岗位可重复抓取，但不会重复落盘。

### 3.3 前端消费接口（文件协议）

前端不直连爬虫，而是消费导出后的静态 JSON。爬虫侧必须保证字段兼容以下协议。

#### A) 主数据文件

- `web/data/jobs.index.json`：分片索引
- `web/data/chunks/jobs-*.json`：分片数据
- 回退：`web/data/jobs.json`（整包）

索引文件关键结构：

```json
{
	"version": 1,
	"generated_at": "2026-03-19T00:00:00Z",
	"chunk_mode": "full",
	"chunk_size": 120,
	"total": 1234,
	"files": {
		"jobs": "jobs.json",
		"chunks_dir": "chunks"
	},
	"chunks": [
		{"file": "jobs-0001.json", "count": 120, "start": 0, "end": 119}
	]
}
```

#### B) 宣讲日历文件

- `web/data/campus_face2face.json`

字段约定：

| 字段 | 类型 | 说明 |
|------|------|------|
| company | string | 企业名 |
| date | string | 支持 `YYYY-MM-DD` 或 `MM-DD` |
| consult_url | string | 宣讲咨询链接 |
| location | string | 地点 |
| intro | string | 简介 |

---

## 4. 站点爬虫实现摘要

### 4.1 腾讯（`tencent`）

- 类型：API 直连（无登录）
- 架构：项目映射/城市字典/岗位类别字典预加载 -> 列表分页 -> 详情补全
- 关键接口：
	- `POST /api/v1/position/searchPosition`
	- `POST /api/v1/jobDetails/getJobDetailsByPostId`
	- `GET /api/v1/position/getProjectMapping`
	- `GET /api/v1/position/getPositionWorkCities`
	- `GET /api/v1/position/getPositionFamily`
- 主要风险：接口鉴权升级、字段名改动、城市编码映射失效

### 4.2 哔哩哔哩（`bilibili`）

- 类型：API 直连（需 CSRF）
- 架构：先取 `csrf token` -> 列表分页 -> 可选详情补全（`fetch_detail=1`）
- 关键接口：
	- `GET /api/auth/v1/csrf/token`
	- `POST /api/campus/position/positionList`
	- `GET /api/campus/position/detail/{id}`（可选）
- 主要风险：CSRF 获取失败、请求头被风控、返回结构漂移

### 4.3 网易互娱（`netease`）

- 类型：API 直连（无登录）
- 架构：filters 可达性确认 -> 列表分页 -> 详情补全
- 关键接口：
	- `GET /api/recruitment/campus/position/filters`
	- `POST /api/recruitment/campus/position/list`
	- `GET /api/recruitment/campus/position/detail?positionId=...`
- 主要风险：`project_id`/筛选参数变更、`info` 字段结构变化

### 4.4 米哈游（`mihoyo`）

- 类型：API 直连（无登录）
- 架构：列表分页 -> 详情补全
- 关键接口：
	- `POST /ats-portal/v1/job/list`
	- `POST /ats-portal/v1/job/info`
- 固定参数：`channelDetailIds=[1]`，`hireType=1`
- 主要风险：渠道参数失效、详情字段改名

### 4.5 蚂蚁集团（`antgroup`）

- 类型：API 直连（列表接口已含主要字段）
- 架构：仅分页搜索，不做详情二跳
- 关键接口：
	- `POST /api/campus/position/search`
- 固定参数：`batchIds=["26022600074513"]`（可根据业务批次调整）
- 主要风险：批次 ID 过期、字段层级变化（`data` 嵌套）

---

## 5. 运行方式

### 5.1 基础命令

```powershell
cd scrapy_crawlers
python -m scrapy list
```

### 5.2 单站点运行示例

```powershell
# 腾讯：抓取前 2 页
python -m scrapy crawl tencent -a start_page=1 -a end_page=2

# B站：抓取前 2 页并开启详情补全
python -m scrapy crawl bilibili -a start_page=1 -a end_page=2 -a fetch_detail=1

# 网易：指定 project_id
python -m scrapy crawl netease -a start_page=1 -a end_page=2 -a project_id=30

# 米哈游
python -m scrapy crawl mihoyo -a start_page=1 -a end_page=2

# 蚂蚁
python -m scrapy crawl antgroup -a start_page=1 -a end_page=2
```

### 5.3 一次性跑全站（顺序执行）

```powershell
cd scrapy_crawlers
python -m scrapy crawl tencent
python -m scrapy crawl bilibili
python -m scrapy crawl netease
python -m scrapy crawl mihoyo
python -m scrapy crawl antgroup
```

说明：由于使用增量去重，重复执行不会产生重复落盘。

---

## 6. 验收标准

每次改动后至少完成以下检查：

1. 能跑通小样本（每站 1-2 页）。
2. `data/jobs.jsonl` 新增记录中 `company + job_id` 唯一。
3. `title/job_category/work_city/detail_url` 关键字段可读。
4. `work_cities/tags` 保持数组语义（CSV 中允许 `|` 拼接）。
5. 前端导出成功，`web/data/jobs.index.json` 和 `web/data/chunks/` 可加载。

---

## 7. 常见故障排查

### 7.1 启动正常但无新增

- 先看日志中 `IncrementalPipeline: new=... skipped=...`。
- 若 `skipped` 很高且业务确认无新岗，属于预期。
- 若确认有新岗但无新增，检查 `job_id` 提取逻辑是否变化。

### 7.2 某站突然 401/403 或 code 非 0

- 优先在浏览器 Network 面板对比最新请求头与请求体。
- 检查是否新增 CSRF、签名、Referer/Origin 校验。
- 必要时临时切 Playwright 方案抓网络响应，避免服务中断。

### 7.3 字段大面积为空

- 保存一页原始 JSON 样本。
- 对照 spider 的 normalize 映射更新字段路径与兜底优先级。
- 修复后先跑 1 页样本再全量。

### 7.4 前端显示“未找到可用数据目录”

- 确认 `web/data/jobs.index.json` 或 `web/data/jobs.json` 存在。
- 重新执行导出：

```powershell
python src/export_frontend_jobs.py --input data/jobs.jsonl --output-root web
```

---

## 8. 维护流程（推荐）

每次网站变更按以下顺序处理：

1. 先抓包确认接口是否变更（URL、参数、响应结构、鉴权）。
2. 在对应 spider 做最小改动，保持统一 schema 不变。
3. 跑小样本并记录对比（条数、缺失率、关键字段样本）。
4. 更新本文件与对应站点维护文档。
5. 再执行全量抓取 + 前端导出验证。

---

## 9. 与 docs 文档关系

本文件提供模块总规范；各站点深度复盘与历史结论仍保留在：

- `docs/TENCENT_SCRAPER_MAINTENANCE.md`
- `docs/BILIBILI_SCRAPER_MAINTENANCE.md`
- `docs/MIHOYO_SCRAPER_MAINTENANCE.md`
- `docs/BYTEDANCE_CAMPUS_SCRAPER_PLAN.md`

维护原则：

- 本文件偏“标准与入口”。
- 站点文档偏“细节与复盘”。