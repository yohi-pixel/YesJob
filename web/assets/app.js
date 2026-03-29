const state = {
  allJobs: [],
  filteredJobs: [],
  campusEvents: [],
  eventsByDate: new Map(),
  visibleCount: 0,
  pageSize: 30,
  chunkWarmCount: 2,
  loadState: "准备中",
  dataRoot: "",
  useFallback: false,
  viewMode: "jobs",
  calendar: {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
  },
  filters: {
    company: [],
    companyExclude: [],
    project: [],
    projectExclude: [],
    category: [],
    categoryExclude: [],
    city: [],
    cityExclude: [],
    query: "",
    excludeQuery: "",
    searchFields: ["title", "responsibilities", "requirements", "bonusPoints"],
    searchLogic: "or",
    sortBy: "publish_time",
  },
};

const PINNED_CITIES = ["北京", "上海", "广州", "深圳", "杭州"];
const CITY_ALIAS_MAP = {
  北京市: "北京",
  北京: "北京",
  上海市: "上海",
  上海: "上海",
  广州市: "广州",
  广州: "广州",
  深圳市: "深圳",
  深圳: "深圳",
  杭州市: "杭州",
  杭州: "杭州",
};

const els = {
  loadStateText: document.getElementById("loadStateText"),
  updatedAtText: document.getElementById("updatedAtText"),
  resultCountText: document.getElementById("resultCountText"),
  statusMessage: document.getElementById("statusMessage"),
  viewJobsTab: document.getElementById("viewJobsTab"),
  viewCalendarTab: document.getElementById("viewCalendarTab"),
  jobsView: document.getElementById("jobsView"),
  calendarView: document.getElementById("calendarView"),
  calendarMonthLabel: document.getElementById("calendarMonthLabel"),
  calendarMeta: document.getElementById("calendarMeta"),
  calendarGrid: document.getElementById("calendarGrid"),
  calendarModal: document.getElementById("calendarModal"),
  calendarModalClose: document.getElementById("calendarModalClose"),
  calendarModalTitle: document.getElementById("calendarModalTitle"),
  calendarModalBody: document.getElementById("calendarModalBody"),
  searchInput: document.getElementById("searchInput"),
  excludeSearchInput: document.getElementById("excludeSearchInput"),
  searchLogicSelect: document.getElementById("searchLogicSelect"),
  mobileFilterToggle: document.getElementById("mobileFilterToggle"),
  filtersSidebar: document.getElementById("filtersSidebar"),
  companyTreeFilter: document.getElementById("companyTreeFilter"),
  companyTreeSummary: document.getElementById("companyTreeSummary"),
  cityFilter: document.getElementById("cityFilter"),
  cityFilterSummary: document.getElementById("cityFilterSummary"),
  cityPrimaryOptions: document.getElementById("cityPrimaryOptions"),
  cityOtherCities: document.getElementById("cityOtherCities"),
  cityOtherOptions: document.getElementById("cityOtherOptions"),
  sortBy: document.getElementById("sortBy"),
  clearFilters: document.getElementById("clearFilters"),
  listContainer: document.getElementById("listContainer"),
  loadMoreBtn: document.getElementById("loadMoreBtn"),
  cardTpl: document.getElementById("jobCardTpl"),
  overviewEntry: document.getElementById("overviewEntry"),
};

function cleanupEmptyQuerySuffix() {
  if (!window.location.search && window.location.href.endsWith("?")) {
    const cleanUrl = `${window.location.pathname}${window.location.hash || ""}`;
    window.history.replaceState({}, "", cleanUrl);
  }
}

function setLoadState(nextState, message) {
  state.loadState = nextState;
  els.loadStateText.textContent = nextState;
  if (message) {
    els.statusMessage.textContent = message;
  }
}

function pad2(num) {
  return String(num).padStart(2, "0");
}

function normalizeDateKey(rawDate) {
  const text = String(rawDate || "").trim();
  if (!text) return "";

  const fullMatch = text.match(/^(\d{4})[\/.-](\d{1,2})[\/.-](\d{1,2})$/);
  const shortMatch = text.match(/^(\d{1,2})[\/.-](\d{1,2})$/);

  let year = state.calendar.year;
  let month = 0;
  let day = 0;

  if (fullMatch) {
    year = Number(fullMatch[1]);
    month = Number(fullMatch[2]);
    day = Number(fullMatch[3]);
  } else if (shortMatch) {
    month = Number(shortMatch[1]);
    day = Number(shortMatch[2]);
  } else {
    const dt = new Date(text);
    if (Number.isNaN(dt.getTime())) return "";
    year = dt.getFullYear();
    month = dt.getMonth() + 1;
    day = dt.getDate();
  }

  const safeDate = new Date(year, month - 1, day);
  if (
    safeDate.getFullYear() !== year ||
    safeDate.getMonth() + 1 !== month ||
    safeDate.getDate() !== day
  ) {
    return "";
  }

  return `${year}-${pad2(month)}-${pad2(day)}`;
}

function normalizeCampusEvent(item) {
  const event = {
    company: String(item.company || "").trim(),
    date: String(item.date || "").trim(),
    consult_url: String(item.consult_url || item.consultUrl || "").trim(),
    location: String(item.location || "").trim(),
    intro: String(item.intro || "").trim(),
  };
  event.date_key = normalizeDateKey(event.date);
  return event;
}

function buildEventDateMap(events) {
  const dateMap = new Map();
  for (const event of events) {
    if (!event.date_key) continue;
    if (!dateMap.has(event.date_key)) {
      dateMap.set(event.date_key, []);
    }
    dateMap.get(event.date_key).push(event);
  }
  return dateMap;
}

function setViewMode(mode) {
  state.viewMode = mode;
  const calendarMode = mode === "calendar";

  els.jobsView.classList.toggle("is-hidden-view", calendarMode);
  els.calendarView.classList.toggle("is-hidden-view", !calendarMode);

  els.viewJobsTab.classList.toggle("is-active", !calendarMode);
  els.viewCalendarTab.classList.toggle("is-active", calendarMode);
  els.viewJobsTab.setAttribute("aria-selected", String(!calendarMode));
  els.viewCalendarTab.setAttribute("aria-selected", String(calendarMode));

  if (calendarMode) {
    renderCalendarView();
  }
}

function getMonthMeta() {
  const { year, month } = state.calendar;
  return {
    year,
    month,
    monthKey: `${year}-${pad2(month)}`,
    daysInMonth: new Date(year, month, 0).getDate(),
    firstWeekday: new Date(year, month - 1, 1).getDay(),
  };
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderEventSummaries(events) {
  if (!events.length) {
    return '<p class="calendar-day-summary">暂无宣讲安排</p>';
  }
  const sample = events
    .slice(0, 2)
    .map((event) => `<span class="calendar-company-art">${escapeHtml(event.company || "未命名企业")}</span>`);
  const moreText = events.length > 2 ? ` 等 ${events.length} 场` : "";
  return `<p class="calendar-day-summary">${sample.join("<span class=\"calendar-company-sep\"> · </span>")}${
    moreText ? `<span class="calendar-more-text">${escapeHtml(moreText)}</span>` : ""
  }</p>`;
}

function renderCalendarView() {
  const { year, month, monthKey, daysInMonth, firstWeekday } = getMonthMeta();
  els.calendarMonthLabel.textContent = `${year} 年 ${month} 月宣讲日历`;

  const monthEvents = state.campusEvents.filter((item) => item.date_key.startsWith(monthKey));
  els.calendarMeta.textContent = monthEvents.length
    ? `本月共 ${monthEvents.length} 场宣讲，点击日期卡片查看完整信息。`
    : "本月暂无宣讲信息，后续更新 campus_face2face.json 后将自动映射。";

  const weekCount = Math.ceil((firstWeekday + daysInMonth) / 7);
  const fragment = document.createDocumentFragment();

  els.calendarGrid.style.gridTemplateRows = `repeat(${weekCount}, minmax(76px, auto))`;

  for (let weekIndex = 0; weekIndex < weekCount; weekIndex++) {
    let weekDay = 0;

    while (weekDay < 7) {
      const dayNumber = weekIndex * 7 + weekDay - firstWeekday + 1;
      const isInMonth = dayNumber > 0 && dayNumber <= daysInMonth;

      if (!isInMonth) {
        weekDay += 1;
        continue;
      }

      const dateKey = `${year}-${pad2(month)}-${pad2(dayNumber)}`;
      const dayEvents = state.eventsByDate.get(dateKey) || [];

      if (dayEvents.length) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "calendar-day is-active-day has-events";
        btn.dataset.dateKey = dateKey;
        btn.setAttribute("aria-label", `${dateKey}，${dayEvents.length} 场宣讲`);
        btn.style.gridColumn = `${weekDay + 1} / span 1`;
        btn.style.gridRow = String(weekIndex + 1);
        btn.innerHTML = `
          <div class="calendar-day-top">
            <span class="calendar-day-num">${dayNumber}</span>
            <span class="calendar-day-count">${dayEvents.length} 场</span>
          </div>
          ${renderEventSummaries(dayEvents)}
        `;
        fragment.appendChild(btn);
        weekDay += 1;
        continue;
      }

      const rangeStartDay = dayNumber;
      const rangeStartCol = weekDay;
      let rangeEndDay = dayNumber;
      let span = 1;

      while (weekDay + span < 7) {
        const nextDay = weekIndex * 7 + (weekDay + span) - firstWeekday + 1;
        const inMonth = nextDay > 0 && nextDay <= daysInMonth;
        if (!inMonth) break;
        const nextDateKey = `${year}-${pad2(month)}-${pad2(nextDay)}`;
        const nextEvents = state.eventsByDate.get(nextDateKey) || [];
        if (nextEvents.length) break;
        rangeEndDay = nextDay;
        span += 1;
      }

      const emptyCard = document.createElement("article");
      emptyCard.className = "calendar-day is-empty-merged";
      emptyCard.style.gridColumn = `${rangeStartCol + 1} / span ${span}`;
      emptyCard.style.gridRow = String(weekIndex + 1);
      const rangeLabel = rangeStartDay === rangeEndDay ? `${rangeStartDay} 日` : `${rangeStartDay}-${rangeEndDay} 日`;
      emptyCard.innerHTML = `
        <div class="calendar-day-top">
          <span class="calendar-day-num">${rangeLabel}</span>
        </div>
        <p class="calendar-day-summary">暂无宣讲安排</p>
      `;
      fragment.appendChild(emptyCard);
      weekDay += span;
    }
  }

  els.calendarGrid.innerHTML = "";
  els.calendarGrid.appendChild(fragment);
}

function openCalendarModal(dateKey) {
  const events = state.eventsByDate.get(dateKey) || [];
  els.calendarModalTitle.textContent = `${dateKey} 宣讲安排`;

  if (!events.length) {
    els.calendarModalBody.innerHTML = '<p class="calendar-day-summary">当日暂无宣讲安排。</p>';
  } else {
    els.calendarModalBody.innerHTML = events
      .map((event) => {
        const linkHtml = event.consult_url
          ? `<a href="${escapeHtml(event.consult_url)}" target="_blank" rel="noreferrer noopener">${escapeHtml(
              event.consult_url
            )}</a>`
          : "暂无";
        return `
          <article class="campus-event-card">
            <h4>${escapeHtml(event.company || "未命名企业")}</h4>
            <p class="campus-event-row"><strong>日期：</strong>${escapeHtml(event.date || dateKey)}</p>
            <p class="campus-event-row"><strong>宣讲咨询网址：</strong>${linkHtml}</p>
            <p class="campus-event-row"><strong>宣讲地点：</strong>${escapeHtml(event.location || "待更新")}</p>
            <p class="campus-event-row"><strong>宣讲简介：</strong>${escapeHtml(event.intro || "待更新")}</p>
          </article>
        `;
      })
      .join("");
  }

  els.calendarModal.classList.remove("is-hidden");
  els.calendarModal.setAttribute("aria-hidden", "false");
}

function closeCalendarModal() {
  els.calendarModal.classList.add("is-hidden");
  els.calendarModal.setAttribute("aria-hidden", "true");
}

async function tryFetchJson(url) {
  const response = await fetch(url, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${url}`);
  }
  return response.json();
}

function resolveDataCandidates() {
  const fromModule = new URL("../data/", import.meta.url).toString();
  const fromCurrent = new URL("data/", window.location.href).toString();
  const fromRoot = new URL("/data/", window.location.origin).toString();
  return [...new Set([fromModule, fromCurrent, fromRoot])];
}

async function locateDataRoot() {
  setLoadState("定位数据目录", "正在定位数据目录...");
  const candidates = resolveDataCandidates();

  for (const base of candidates) {
    try {
      await tryFetchJson(new URL("jobs.index.json", base).toString());
      return base;
    } catch {
      // Continue probing.
    }
  }

  for (const base of candidates) {
    try {
      await tryFetchJson(new URL("jobs.json", base).toString());
      return base;
    } catch {
      // Continue probing.
    }
  }

  throw new Error("未找到可用数据目录，请确认 web/data 下存在 jobs.index.json 或 jobs.json");
}

function nextMode(current) {
  if (current === "include") return "exclude";
  if (current === "exclude") return "off";
  return "include";
}

function markInputMode(input, mode) {
  input.dataset.mode = mode;
  input.checked = mode === "include";
  input.indeterminate = mode === "exclude";
  const label = input.closest("label");
  if (label) {
    label.classList.toggle("filter-mode-exclude", mode === "exclude");
  }
}

function applyCheckboxModes(container) {
  if (!container) return;
  const boxes = container.querySelectorAll('input[type="checkbox"][data-mode]');
  for (const box of boxes) {
    markInputMode(box, box.dataset.mode || "off");
  }
}

function tokenizeKeywords(text) {
  return String(text || "")
    .toLowerCase()
    .split(/[\s,，;；、|]+/)
    .map((x) => x.trim())
    .filter(Boolean);
}

function searchInFields(job, tokens, fields, logic = "or") {
  if (!tokens.length) return true;

  const textMap = {};
  for (const field of fields) {
    const fieldName = field === "bonusPoints" ? "bonus_points" : field;
    textMap[field] = String(job[fieldName] || "").toLowerCase();
  }

  if (logic === "or") {
    return tokens.some((token) => {
      return fields.some((field) => textMap[field].includes(token));
    });
  } else {
    return tokens.every((token) => {
      return fields.some((field) => textMap[field].includes(token));
    });
  }
}

function matchesAny(selectedValues, excludedValues, value) {
  const normalized = String(value || "");
  if (selectedValues.length && !selectedValues.includes(normalized)) return false;
  if (excludedValues.includes(normalized)) return false;
  return true;
}

function matchScoped(selectedKeys, excludedKeys, company, value) {
  const key = `${company || ""}@@${value || ""}`;
  if (selectedKeys.length && !selectedKeys.includes(key)) return false;
  if (excludedKeys.includes(key)) return false;
  return true;
}

function makeScopedKey(company, value) {
  return `${String(company || "").trim()}@@${String(value || "").trim()}`;
}

function parseScopedKey(key) {
  const [company, value] = String(key || "").split("@@");
  return { company: company || "", value: value || "" };
}

function normalizeJob(job) {
  const workCities = Array.isArray(job.work_cities)
    ? job.work_cities
    : String(job.work_cities || "")
        .split("|")
        .map((x) => x.trim())
        .filter(Boolean);
  const tags = Array.isArray(job.tags)
    ? job.tags
    : String(job.tags || "")
        .split("|")
        .map((x) => x.trim())
        .filter(Boolean);

  const searchBlob = String(
    job.search_blob || `${job.title || ""} ${job.responsibilities || ""} ${job.requirements || ""} ${job.bonus_points || ""}`
  );

  const normalizedCities = normalizeCityList([job.work_city, ...workCities]);

  return {
    ...job,
    work_cities: workCities,
    normalized_cities: normalizedCities,
    tags,
    search_blob: searchBlob,
    search_blob_lower: String(job.search_blob_lower || searchBlob).toLowerCase(),
    project: String(job.job_function || job.recruit_type || "").trim(),
  };
}

function normalizeCityName(value) {
  const text = String(value || "").trim().replace(/\s+/g, "");
  if (!text) return "";
  if (CITY_ALIAS_MAP[text]) return CITY_ALIAS_MAP[text];
  if (text.endsWith("市") && text.length > 1) {
    const base = text.slice(0, -1);
    return CITY_ALIAS_MAP[base] || base;
  }
  return text;
}

function normalizeCityList(values) {
  const set = new Set();
  for (const item of values) {
    const city = normalizeCityName(item);
    if (city) set.add(city);
  }
  return [...set];
}

function pickDetailText(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text || "暂无信息";
}

function scoreByRelevance(job, q) {
  if (!q) return 0;
  const text = job.search_blob_lower;
  if (!text) return 0;

  let score = 0;
  let start = 0;
  while (true) {
    const found = text.indexOf(q, start);
    if (found === -1) break;
    score += 1;
    start = found + q.length;
  }
  return score;
}

function parseTimeOrZero(value) {
  const ms = Date.parse(String(value || ""));
  return Number.isFinite(ms) ? ms : 0;
}

function updateStatusText(message) {
  els.statusMessage.textContent = message;
}

function syncMetrics() {
  els.resultCountText.textContent = String(state.filteredJobs.length);
}

function updateLoadMoreButton() {
  const hasMore = state.visibleCount < state.filteredJobs.length;
  els.loadMoreBtn.disabled = !hasMore;
  els.loadMoreBtn.textContent = hasMore ? "加载更多" : "已加载全部";
}

function mergeJobsIntoState(jobs) {
  if (!jobs.length) return;
  const dedup = new Map();
  for (const job of state.allJobs.concat(jobs)) {
    const key = `${job.company || ""}@@${job.job_id || job.detail_url || ""}`;
    dedup.set(key, job);
  }
  state.allJobs = [...dedup.values()];
}

function renderList(reset = false) {
  if (reset) {
    els.listContainer.innerHTML = "";
    state.visibleCount = Math.min(state.pageSize, state.filteredJobs.length);
  }

  const fragment = document.createDocumentFragment();
  const jobsToRender = state.filteredJobs.slice(0, state.visibleCount);

  for (const job of jobsToRender) {
    const node = els.cardTpl.content.firstElementChild.cloneNode(true);
    const titleNode = node.querySelector(".title");
    const linkNode = node.querySelector(".detail-link");
    const companyNode = node.querySelector('[data-field="company"]');
    const projectNode = node.querySelector('[data-field="project"]');
    const categoryNode = node.querySelector('[data-field="category"]');
    const cityNode = node.querySelector('[data-field="city"]');
    const publishTimeNode = node.querySelector('[data-field="publishTime"]');
    const responsibilitiesNode = node.querySelector('[data-field="responsibilities"]');
    const requirementsNode = node.querySelector('[data-field="requirements"]');
    const bonusPointsNode = node.querySelector('[data-field="bonusPoints"]');

    titleNode.textContent = job.title || "未命名岗位";
    if (job.detail_url) {
      linkNode.href = job.detail_url;
    } else {
      linkNode.removeAttribute("href");
      linkNode.textContent = "无详情链接";
      linkNode.style.pointerEvents = "none";
      linkNode.style.opacity = "0.6";
    }

    companyNode.textContent = job.company || "未知公司";
    projectNode.textContent = job.project || "未知项目";
    categoryNode.textContent = job.job_category || "未知类别";
    cityNode.textContent = job.work_city || (Array.isArray(job.work_cities) ? job.work_cities.join("/") : "未知城市");
    publishTimeNode.textContent = job.publish_time || "时间未知";
    responsibilitiesNode.textContent = pickDetailText(job.responsibilities);
    requirementsNode.textContent = pickDetailText(job.requirements);
    bonusPointsNode.textContent = pickDetailText(job.bonus_points);

    fragment.appendChild(node);
  }

  els.listContainer.innerHTML = "";
  els.listContainer.appendChild(fragment);
  updateLoadMoreButton();
}

function extractOptions(jobs, key, fallback = "") {
  const set = new Set();
  for (const job of jobs) {
    const value = String(job[key] || fallback).trim();
    if (value) set.add(value);
  }
  return [...set].sort((a, b) => a.localeCompare(b, "zh-CN"));
}

function makeScopedKey(company, value) {
  return `${String(company || "").trim()}@@${String(value || "").trim()}`;
}

function parseScopedKey(key) {
  const [company, value] = String(key || "").split("@@");
  return { company: company || "", value: value || "" };
}

function buildCompanyTreeData(jobs) {
  const companyMap = new Map();
  for (const job of jobs) {
    const company = String(job.company || "").trim();
    if (!company) continue;
    if (!companyMap.has(company)) {
      companyMap.set(company, { projects: new Set(), categories: new Set() });
    }
    const row = companyMap.get(company);
    if (job.project) row.projects.add(String(job.project).trim());
    if (job.job_category) row.categories.add(String(job.job_category).trim());
  }

  return [...companyMap.entries()]
    .map(([company, value]) => ({
      company,
      projects: [...value.projects].sort((a, b) => a.localeCompare(b, "zh-CN")),
      categories: [...value.categories].sort((a, b) => a.localeCompare(b, "zh-CN")),
    }))
    .sort((a, b) => a.company.localeCompare(b.company, "zh-CN"));
}

function syncCompanyTreeSelections(companyTree) {
  const companySet = new Set(companyTree.map((row) => row.company));
  state.filters.company = state.filters.company.filter((company) => companySet.has(company));

  const projectSet = new Set();
  const categorySet = new Set();
  for (const row of companyTree) {
    for (const project of row.projects) projectSet.add(makeScopedKey(row.company, project));
    for (const category of row.categories) categorySet.add(makeScopedKey(row.company, category));
  }

  state.filters.project = state.filters.project.filter((key) => projectSet.has(key));
  state.filters.category = state.filters.category.filter((key) => categorySet.has(key));
}

function updateCompanyTreeSummary(companyTree) {
  if (!els.companyTreeSummary) return;
  const selectedCompanyCount = state.filters.company.length;
  const selectedProjectCount = state.filters.project.length;
  const selectedCategoryCount = state.filters.category.length;

  if (!selectedCompanyCount && !selectedProjectCount && !selectedCategoryCount) {
    els.companyTreeSummary.textContent = `共 ${companyTree.length} 家公司，按公司展开项目与类别（均支持多选）。`;
    return;
  }

  els.companyTreeSummary.textContent = `已选 公司 ${selectedCompanyCount} / 项目 ${selectedProjectCount} / 类别 ${selectedCategoryCount}`;
}

function renderCompanyTreeFilter(jobs) {
  if (!els.companyTreeFilter) return;

  const companyTree = buildCompanyTreeData(jobs);
  syncCompanyTreeSelections(companyTree);
  updateCompanyTreeSummary(companyTree);

  const selectedCompanies = new Set(state.filters.company);
  const excludedCompanies = new Set(state.filters.companyExclude);
  const selectedProjects = new Set(state.filters.project);
  const excludedProjects = new Set(state.filters.projectExclude);
  const selectedCategories = new Set(state.filters.category);
  const excludedCategories = new Set(state.filters.categoryExclude);

  els.companyTreeFilter.innerHTML = companyTree
    .map((row) => {
      const companyMode = selectedCompanies.has(row.company) ? "include" : excludedCompanies.has(row.company) ? "exclude" : "off";
      const companyChecked = companyMode === "include" ? "checked" : "";
      const projectsHtml = row.projects.length
        ? row.projects
            .map((project) => {
              const scopedKey = makeScopedKey(row.company, project);
              const mode = selectedProjects.has(scopedKey) ? "include" : excludedProjects.has(scopedKey) ? "exclude" : "off";
              const checked = mode === "include" ? "checked" : "";
              return `<label class="company-option-item"><input type="checkbox" data-kind="project" data-mode="${mode}" data-company="${escapeHtml(
                row.company
              )}" value="${escapeHtml(scopedKey)}" ${checked} />${escapeHtml(project)}</label>`;
            })
            .join("")
        : '<span class="sidebar-hint">暂无项目</span>';

      const categoriesHtml = row.categories.length
        ? row.categories
            .map((category) => {
              const scopedKey = makeScopedKey(row.company, category);
              const mode = selectedCategories.has(scopedKey) ? "include" : excludedCategories.has(scopedKey) ? "exclude" : "off";
              const checked = mode === "include" ? "checked" : "";
              return `<label class="company-option-item"><input type="checkbox" data-kind="category" data-mode="${mode}" data-company="${escapeHtml(
                row.company
              )}" value="${escapeHtml(scopedKey)}" ${checked} />${escapeHtml(category)}</label>`;
            })
            .join("")
        : '<span class="sidebar-hint">暂无类别</span>';

      return `
        <details class="company-node" ${companyMode !== "off" ? "open" : ""}>
          <summary>
            <input class="company-company-check" type="checkbox" data-kind="company" data-mode="${companyMode}" value="${escapeHtml(row.company)}" ${companyChecked} />
            <span>${escapeHtml(row.company)}</span>
          </summary>
          <div class="company-node-body">
            <section class="company-subgroup">
              <h4 class="company-subgroup-title">项目</h4>
              <div class="company-sub-options">${projectsHtml}</div>
            </section>
            <section class="company-subgroup">
              <h4 class="company-subgroup-title">类别</h4>
              <div class="company-sub-options">${categoriesHtml}</div>
            </section>
          </div>
        </details>
      `;
    })
    .join("");
}

function matchesAny(selectedValues, value) {
  if (!selectedValues.length) return true;
  return selectedValues.includes(String(value || ""));
}

function matchScoped(selectedKeys, company, value) {
  if (!selectedKeys.length) return true;
  return selectedKeys.includes(makeScopedKey(company, value));
}

function extractCities(jobs) {
  const set = new Set();
  for (const job of jobs) {
    if (Array.isArray(job.normalized_cities)) {
      for (const city of job.normalized_cities) {
        if (city) set.add(city);
      }
    }
  }
  const cities = [...set];
  const pinned = PINNED_CITIES.filter((city) => cities.includes(city));
  const others = cities.filter((city) => !PINNED_CITIES.includes(city)).sort((a, b) => a.localeCompare(b, "zh-CN"));
  return { pinned, others };
}

function renderCityCheckboxes(container, cities) {
  if (!container) return;
  const selected = new Set(state.filters.city);
  const excluded = new Set(state.filters.cityExclude);
  container.innerHTML = cities
    .map((city) => {
      const mode = selected.has(city) ? "include" : excluded.has(city) ? "exclude" : "off";
      const checked = mode === "include" ? "checked" : "";
      return `<label class="city-option-item"><input type="checkbox" data-kind="city" data-mode="${mode}" value="${escapeHtml(city)}" ${checked} />${escapeHtml(
        city
      )}</label>`;
    })
    .join("");
  applyCheckboxModes(container);
}

function updateCityFilterSummary() {
  if (!els.cityFilterSummary) return;
  const selected = state.filters.city;
  const excluded = state.filters.cityExclude;
  if (!selected.length && !excluded.length) {
    els.cityFilterSummary.textContent = "全部城市";
    return;
  }
  if (selected.length && !excluded.length && selected.length <= 2) {
    els.cityFilterSummary.textContent = selected.join("、");
    return;
  }
  const selectedText = selected.length ? `+${selected.length}` : "";
  const excludedText = excluded.length ? `-${excluded.length}` : "";
  els.cityFilterSummary.textContent = `城市 ${selectedText} ${excludedText}`.trim();
}

function syncCitySelectionByOptions(cities) {
  const valid = new Set(cities);
  state.filters.city = state.filters.city.filter((city) => valid.has(city));
}

function renderCityFilterOptions(jobs) {
  if (!els.cityPrimaryOptions || !els.cityOtherOptions || !els.cityOtherCities) return;

  const { pinned, others } = extractCities(jobs);
  const available = [...pinned, ...others];
  syncCitySelectionByOptions(available);

  renderCityCheckboxes(els.cityPrimaryOptions, pinned);
  renderCityCheckboxes(els.cityOtherOptions, others);
  els.cityOtherCities.classList.toggle("is-hidden", !others.length);
  if (!others.length) {
    els.cityOtherCities.removeAttribute("open");
  }

  updateCityFilterSummary();
}

function refreshFilterOptions() {
  const jobsByCompanyTree = state.allJobs.filter((job) => {
    if (state.filters.city.length) {
      const cities = new Set(Array.isArray(job.normalized_cities) ? job.normalized_cities : []);
      if (!state.filters.city.some((city) => cities.has(city))) return false;
    }
    return true;
  });

  renderCompanyTreeFilter(jobsByCompanyTree);

  const jobsForCity = state.allJobs.filter((job) => {
    if (!matchesAny(state.filters.company, job.company)) return false;
    if (!matchScoped(state.filters.project, job.company, job.project)) return false;
    if (!matchScoped(state.filters.category, job.company, job.job_category)) return false;
    return true;
  });

  renderCityFilterOptions(jobsForCity);
}

function applyFilters() {
  const includeTokens = tokenizeKeywords(state.filters.query);
  const excludeTokens = tokenizeKeywords(state.filters.excludeQuery);

  const filtered = state.allJobs.filter((job) => {
    if (!matchesAny(state.filters.company, state.filters.companyExclude, job.company)) return false;
    if (!matchScoped(state.filters.project, state.filters.projectExclude, job.company, job.project)) return false;
    if (!matchScoped(state.filters.category, state.filters.categoryExclude, job.company, job.job_category)) return false;

    if (state.filters.city.length || state.filters.cityExclude.length) {
      const cities = new Set(Array.isArray(job.normalized_cities) ? job.normalized_cities : []);
      const includePass = !state.filters.city.length || state.filters.city.some((city) => cities.has(city));
      const excludeHit = state.filters.cityExclude.some((city) => cities.has(city));
      if (!includePass || excludeHit) return false;
    }

    if (includeTokens.length) {
      if (!searchInFields(job, includeTokens, state.filters.searchFields, state.filters.searchLogic)) return false;
    }

    if (excludeTokens.length) {
      const blob = String(job.search_blob_lower || "");
      if (excludeTokens.some((token) => blob.includes(token))) return false;
    }
    return true;
  });

  if (state.filters.sortBy === "relevance") {
    filtered.sort((a, b) => scoreByRelevance(b, includeTokens) - scoreByRelevance(a, includeTokens));
  } else {
    filtered.sort((a, b) => parseTimeOrZero(b.publish_time) - parseTimeOrZero(a.publish_time));
  }

  state.filteredJobs = filtered;
  syncMetrics();
  renderList(true);

  if (!filtered.length) {
    updateStatusText("当前筛选条件下没有匹配岗位，请调整筛选或搜索词。");
  } else {
    updateStatusText(`已加载 ${state.allJobs.length} 条岗位，当前匹配 ${filtered.length} 条。`);
  }
}

function debounce(fn, wait) {
  let timer = null;
  return (...args) => {
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), wait);
  };
}

function bindEvents() {
  const debouncedSearch = debounce((value) => {
    state.filters.query = value;
    applyFilters();
  }, 220);

  els.searchInput.addEventListener("input", (event) => {
    debouncedSearch(event.target.value || "");
  });

  if (els.mobileFilterToggle && els.filtersSidebar) {
    const syncMobileToggleState = () => {
      const isOpen = els.filtersSidebar.classList.contains("is-open");
      els.mobileFilterToggle.setAttribute("aria-expanded", String(isOpen));
      els.mobileFilterToggle.textContent = isOpen ? "◀" : "▶";
    };

    els.mobileFilterToggle.addEventListener("click", () => {
      els.filtersSidebar.classList.toggle("is-open");
      syncMobileToggleState();
    });

    document.addEventListener("click", (event) => {
      if (window.matchMedia("(max-width: 900px)").matches === false) return;
      if (!(event.target instanceof Node)) return;
      const clickedToggle = els.mobileFilterToggle.contains(event.target);
      const clickedSidebar = els.filtersSidebar.contains(event.target);
      if (!clickedToggle && !clickedSidebar) {
        els.filtersSidebar.classList.remove("is-open");
        syncMobileToggleState();
      }
    });

    window.addEventListener("resize", () => {
      if (window.matchMedia("(max-width: 900px)").matches === false) {
        els.filtersSidebar.classList.remove("is-open");
        syncMobileToggleState();
      }
    });
  }

  if (els.companyTreeFilter) {
    els.companyTreeFilter.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") return;
      event.preventDefault();

      const kind = target.dataset.kind;
      if (!kind) return;
      const excludeKey = `${kind}Exclude`;
      const value = target.value;
      const company = target.dataset.company || "";

      const currentMode = target.dataset.mode || "off";
      const next = nextMode(currentMode);
      markInputMode(target, next);

      const includeSet = new Set(state.filters[kind] || []);
      const excludeSet = new Set(state.filters[excludeKey] || []);
      includeSet.delete(value);
      excludeSet.delete(value);
      if (next === "include") includeSet.add(value);
      if (next === "exclude") excludeSet.add(value);
      state.filters[kind] = [...includeSet];
      state.filters[excludeKey] = [...excludeSet];

      if (kind === "company" && next !== "include") {
        state.filters.project = state.filters.project.filter((key) => parseScopedKey(key).company !== value);
        state.filters.projectExclude = state.filters.projectExclude.filter((key) => parseScopedKey(key).company !== value);
        state.filters.category = state.filters.category.filter((key) => parseScopedKey(key).company !== value);
        state.filters.categoryExclude = state.filters.categoryExclude.filter((key) => parseScopedKey(key).company !== value);
      }

      if ((kind === "project" || kind === "category") && next === "include" && company) {
        state.filters.companyExclude = state.filters.companyExclude.filter((item) => item !== company);
        if (!state.filters.company.includes(company)) {
          state.filters.company = [...state.filters.company, company];
        }
      }

      state.filters.city = [];
      state.filters.cityExclude = [];
      refreshFilterOptions();
      applyFilters();
    });
  }

  if (els.cityPrimaryOptions && els.cityOtherOptions && els.cityFilter) {
    const onCitySelectionChange = (event) => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") return;
      event.preventDefault();

      const city = target.value;
      const currentMode = target.dataset.mode || "off";
      const next = nextMode(currentMode);
      markInputMode(target, next);

      const selected = new Set(state.filters.city);
      const excluded = new Set(state.filters.cityExclude);
      selected.delete(city);
      excluded.delete(city);
      if (next === "include") selected.add(city);
      if (next === "exclude") excluded.add(city);

      state.filters.city = [...selected];
      state.filters.cityExclude = [...excluded];
      updateCityFilterSummary();
      applyFilters();
    };

    els.cityPrimaryOptions.addEventListener("click", onCitySelectionChange);
    els.cityOtherOptions.addEventListener("click", onCitySelectionChange);

    els.cityFilter.addEventListener("toggle", () => {
      const opened = els.cityFilter.hasAttribute("open");
      els.cityFilter.dataset.open = opened ? "true" : "false";
    });

    document.addEventListener("click", (event) => {
      if (!(event.target instanceof Node)) return;

      const allDetails = [els.cityFilter, ...document.querySelectorAll(".company-node")].filter(Boolean);
      for (const detailEl of allDetails) {
        if (detailEl.hasAttribute("open") && !detailEl.contains(event.target)) {
          detailEl.removeAttribute("open");
        }
      }
    });
  }

  if (els.excludeSearchInput) {
    const debouncedExcludeSearch = debounce(() => {
      state.filters.excludeQuery = els.excludeSearchInput.value || "";
      applyFilters();
    }, 220);
    els.excludeSearchInput.addEventListener("input", debouncedExcludeSearch);
  }

  if (els.searchLogicSelect) {
    els.searchLogicSelect.addEventListener("change", (event) => {
      state.filters.searchLogic = event.target.value || "or";
      applyFilters();
    });
  }

  const searchFieldCheckboxes = document.querySelectorAll('input[type="checkbox"][data-field]');
  searchFieldCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", (event) => {
      const field = event.target.dataset.field;
      if (event.target.checked) {
        if (!state.filters.searchFields.includes(field)) {
          state.filters.searchFields.push(field);
        }
      } else {
        state.filters.searchFields = state.filters.searchFields.filter((f) => f !== field);
      }
      applyFilters();
    });
  });

  els.sortBy.addEventListener("change", (event) => {
    state.filters.sortBy = event.target.value;
    applyFilters();
  });

  els.clearFilters.addEventListener("click", () => {
    state.filters = {
      ...state.filters,
      company: [],
      companyExclude: [],
      project: [],
      projectExclude: [],
      category: [],
      categoryExclude: [],
      city: [],
      cityExclude: [],
      query: "",
      excludeQuery: "",
      searchFields: ["title", "responsibilities", "requirements", "bonusPoints"],
      searchLogic: "or",
      sortBy: "publish_time",
    };
    els.searchInput.value = "";
    if (els.excludeSearchInput) {
      els.excludeSearchInput.value = "";
    }
    if (els.searchLogicSelect) {
      els.searchLogicSelect.value = "or";
    }
    const searchFieldCheckboxes = document.querySelectorAll('input[type="checkbox"][data-field]');
    searchFieldCheckboxes.forEach((checkbox) => {
      checkbox.checked = true;
    });
    els.sortBy.value = "publish_time";
    refreshFilterOptions();
    applyFilters();
  });

  els.loadMoreBtn.addEventListener("click", () => {
    state.visibleCount = Math.min(state.visibleCount + state.pageSize, state.filteredJobs.length);
    renderList(false);
  });

  els.overviewEntry.addEventListener("click", () => {
    window.alert("数据概览功能已预留入口，后续版本上线。当前先专注岗位检索与筛选。");
  });

  els.viewJobsTab.addEventListener("click", () => {
    setViewMode("jobs");
  });

  els.viewCalendarTab.addEventListener("click", () => {
    setViewMode("calendar");
  });

  els.calendarGrid.addEventListener("click", (event) => {
    const target = event.target.closest(".calendar-day");
    if (!target || !target.dataset.dateKey) return;
    openCalendarModal(target.dataset.dateKey);
  });

  els.calendarModalClose.addEventListener("click", closeCalendarModal);
  els.calendarModal.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.dataset.role === "close-modal") {
      closeCalendarModal();
    }
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !els.calendarModal.classList.contains("is-hidden")) {
      closeCalendarModal();
    }
  });
}

async function loadCampusSchedule(base) {
  try {
    const raw = await tryFetchJson(new URL("campus_face2face.json", base).toString());
    const list = Array.isArray(raw) ? raw : [];
    state.campusEvents = list.map(normalizeCampusEvent).filter((item) => item.date_key);
    state.eventsByDate = buildEventDateMap(state.campusEvents);
  } catch {
    state.campusEvents = [];
    state.eventsByDate = new Map();
  }
  renderCalendarView();
}

async function loadWithIndex(base) {
  const index = await tryFetchJson(new URL("jobs.index.json", base).toString());
  const chunks = Array.isArray(index.chunks) ? index.chunks : [];
  const files = chunks.map((item) => item.file).filter(Boolean);

  const warm = files.slice(0, state.chunkWarmCount);
  const rest = files.slice(state.chunkWarmCount);
  state.allJobs = [];
  els.updatedAtText.textContent = index.generated_at || "-";

  for (let i = 0; i < warm.length; i++) {
    const name = warm[i];
    const records = await tryFetchJson(new URL(`chunks/${name}`, base).toString()).catch(() => []);
    mergeJobsIntoState(records.map(normalizeJob));
    refreshFilterOptions();
    applyFilters();
    setLoadState("加载中", `首批分片加载中... ${i + 1}/${warm.length}（${state.allJobs.length} 条）`);
  }

  setLoadState("加载中", `首批分片已加载 (${state.allJobs.length} 条)，正在补齐剩余数据...`);

  if (rest.length) {
    loadRestChunksBatched(base, rest);
  } else {
    setLoadState("完成", `分片加载完成，共 ${state.allJobs.length} 条岗位。`);
  }
}

// Load remaining chunks in small batches to respect mobile browser concurrency limits.
// Each batch is awaited before the next starts, so at most BATCH_SIZE requests run in parallel.
async function loadRestChunksBatched(base, files) {
  const BATCH_SIZE = 2;
  let failedCount = 0;

  for (let i = 0; i < files.length; i += BATCH_SIZE) {
    const batch = files.slice(i, i + BATCH_SIZE);
    const results = await Promise.all(
      batch.map((name) =>
        tryFetchJson(new URL(`chunks/${name}`, base).toString()).catch(() => {
          failedCount++;
          return [];
        })
      )
    );

    const newJobs = results.flat().map(normalizeJob);
    if (!newJobs.length) continue;
    mergeJobsIntoState(newJobs);
    refreshFilterOptions();
    applyFilters();
    setLoadState(
      "加载中",
      `正在补齐数据... 已加载 ${state.allJobs.length} 条（${i + batch.length}/${files.length} 批次完成）`
    );
  }

  if (failedCount > 0) {
    setLoadState("完成", `加载完成，共 ${state.allJobs.length} 条岗位（${failedCount} 个分片加载失败已跳过）。`);
  } else {
    setLoadState("完成", `已加载全部分片，共 ${state.allJobs.length} 条岗位。`);
  }
}

async function loadWithFallback(base, reason = "") {
  const jobs = await tryFetchJson(new URL("jobs.json", base).toString());
  state.allJobs = Array.isArray(jobs) ? jobs.map(normalizeJob) : [];
  state.useFallback = true;
  els.updatedAtText.textContent = "兼容模式";
  setLoadState("兼容模式", `已切换 jobs.json 回退加载。${reason}`.trim());
}

async function initDataFlow() {
  try {
    state.dataRoot = await locateDataRoot();
    setLoadState("加载中", "正在加载岗位数据...");

    try {
      await loadWithIndex(state.dataRoot);
    } catch (indexError) {
      await loadWithFallback(state.dataRoot, "index/chunks 不可用。");
      console.warn("index/chunks load failed:", indexError);
    }

    refreshFilterOptions();
    applyFilters();
    await loadCampusSchedule(state.dataRoot);

    if (!state.useFallback && state.loadState !== "完成") {
      setLoadState("完成", `加载完成，共 ${state.allJobs.length} 条岗位。`);
    }
  } catch (error) {
    setLoadState("失败", "数据加载失败，请检查 web/data 目录是否可访问。");
    updateStatusText(String(error.message || error));
    console.error(error);
  }
}

function start() {
  cleanupEmptyQuerySuffix();
  bindEvents();
  initDataFlow();
}

start();
