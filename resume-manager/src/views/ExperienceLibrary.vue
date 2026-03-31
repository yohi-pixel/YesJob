<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '@/stores/resume'
import { Copy, Search, ExternalLink, BookOpen, FolderOpen, Briefcase, User, Plus, X } from 'lucide-vue-next'
import type { ExperienceItem, SelfDescription } from '@/types'

const router = useRouter()
const store = useResumeStore()
const searchQuery = ref('')
const activeCategory = ref<'project' | 'internship' | 'self-desc'>('project')
const showNewForm = ref(false)
const newExpType = ref<'project' | 'internship'>('project')
const newExp = ref({
  title: '',
  role: '',
  organization: '',
  period: '',
  techStack: '',
  description: '',
  tags: '',
  targetResumeId: '',
})
const newSelfDesc = ref({
  selfEvaluation: '',
  careerObjective: '',
  personalSummary: '',
  tags: '',
  targetResumeId: '',
})

interface ExperienceWithSource extends ExperienceItem {
  _resumeId: string
  _resumeTitle: string
  _category: 'project' | 'internship'
}

interface SelfDescWithSource extends SelfDescription {
  _resumeId: string
  _resumeTitle: string
}

const allExperiences = computed<ExperienceWithSource[]>(() => {
  const list: ExperienceWithSource[] = []
  for (const r of store.resumes) {
    for (const exp of r.experiences) {
      // Auto-detect category based on tags or keywords
      const category = detectCategory(exp)
      list.push({
        ...exp,
        _resumeId: r.id,
        _resumeTitle: r.title,
        _category: category,
      })
    }
  }
  return list
})

function detectCategory(exp: ExperienceItem): 'project' | 'internship' {
  const title = exp.title.toLowerCase()
  const org = exp.organization.toLowerCase()
  const tags = exp.tags.map(t => t.toLowerCase())
  
  // Keywords for internship
  const internshipKeywords = ['实习', 'intern', ' Internship']
  for (const kw of internshipKeywords) {
    if (title.includes(kw) || org.includes(kw)) return 'internship'
  }
  
  // Keywords for project
  const projectKeywords = ['项目', 'project', ' Project', '比赛', '竞赛', '大赛']
  for (const kw of projectKeywords) {
    if (title.includes(kw) || org.includes(kw)) return 'project'
  }
  
  // Check tags
  if (tags.some(t => t.includes('实习') || t.includes('intern'))) return 'internship'
  if (tags.some(t => t.includes('项目') || t.includes('project'))) return 'project'
  
  // Default to project
  return 'project'
}

const allSelfDescriptions = computed<SelfDescWithSource[]>(() => {
  const list: SelfDescWithSource[] = []
  for (const r of store.resumes) {
    if (r.selfDescription.selfEvaluation || r.selfDescription.careerObjective || r.selfDescription.personalSummary) {
      list.push({
        ...r.selfDescription,
        _resumeId: r.id,
        _resumeTitle: r.title,
      })
    }
  }
  return list
})

const filteredExperiences = computed(() => {
  const q = searchQuery.value.toLowerCase()
  let list = allExperiences.value.filter(e => e._category === activeCategory.value)
  if (!q) return list
  return list.filter(
    e =>
      e.title.toLowerCase().includes(q) ||
      e.role.toLowerCase().includes(q) ||
      e.organization.toLowerCase().includes(q) ||
      e.tags.some(t => t.toLowerCase().includes(q)) ||
      e.techStack.some(t => t.toLowerCase().includes(q))
  )
})

const filteredSelfDesc = computed(() => {
  const q = searchQuery.value.toLowerCase()
  let list = allSelfDescriptions.value
  if (!q) return list
  return list.filter(
    e =>
      e.selfEvaluation.toLowerCase().includes(q) ||
      e.careerObjective.toLowerCase().includes(q) ||
      e.personalSummary.toLowerCase().includes(q) ||
      e.tags.some(t => t.toLowerCase().includes(q))
  )
})

const uniqueTags = computed(() => {
  const tags = new Set<string>()
  const list = activeCategory.value === 'self-desc' ? allSelfDescriptions.value : allExperiences.value.filter(e => e._category === activeCategory.value)
  for (const e of list) {
    e.tags.forEach(t => tags.add(t))
  }
  return [...tags]
})

const categories = [
  { key: 'project', label: '项目经历', icon: FolderOpen },
  { key: 'internship', label: '实习经历', icon: Briefcase },
  { key: 'self-desc', label: '自我描述', icon: User },
] as const

function deepCopyToResume(exp: ExperienceWithSource) {
  const currentId = store.currentResumeId
  if (!currentId) {
    if (store.resumes.length === 0) {
      alert('请先创建一份简历')
      return
    }
    const options = store.resumes.map((r, i) => `${i + 1}. ${r.title}`).join('\n')
    const choice = prompt(`复制到哪份简历？\n${options}\n请输入序号：`)
    if (!choice) return
    const idx = parseInt(choice) - 1
    if (idx < 0 || idx >= store.resumes.length) {
      alert('无效选择')
      return
    }
    const copy: ExperienceItem = JSON.parse(JSON.stringify(exp))
    delete (copy as any)._resumeId
    delete (copy as any)._resumeTitle
    delete (copy as any)._category
    copy.id = Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
    store.updateResume(store.resumes[idx].id, {
      experiences: [...store.resumes[idx].experiences, copy],
    })
    alert(`已复制到「${store.resumes[idx].title}」`)
  } else {
    const copy: ExperienceItem = JSON.parse(JSON.stringify(exp))
    delete (copy as any)._resumeId
    delete (copy as any)._resumeTitle
    delete (copy as any)._category
    copy.id = Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
    store.addExperience(currentId, copy)
    alert('已复制到当前简历')
  }
}

function copySelfDescToResume(item: SelfDescWithSource) {
  const currentId = store.currentResumeId
  if (!currentId) {
    if (store.resumes.length === 0) {
      alert('请先创建一份简历')
      return
    }
    const options = store.resumes.map((r, i) => `${i + 1}. ${r.title}`).join('\n')
    const choice = prompt(`复制到哪份简历？\n${options}\n请输入序号：`)
    if (!choice) return
    const idx = parseInt(choice) - 1
    if (idx < 0 || idx >= store.resumes.length) {
      alert('无效选择')
      return
    }
    store.updateSelfDescription(store.resumes[idx].id, {
      selfEvaluation: item.selfEvaluation,
      careerObjective: item.careerObjective,
      personalSummary: item.personalSummary,
      tags: item.tags,
    })
    alert(`已复制到「${store.resumes[idx].title}」`)
  } else {
    store.updateSelfDescription(currentId, {
      selfEvaluation: item.selfEvaluation,
      careerObjective: item.careerObjective,
      personalSummary: item.personalSummary,
      tags: item.tags,
    })
    alert('已复制到当前简历')
  }
}

function goToResume(resumeId: string) {
  router.push({ name: 'resume-edit', params: { id: resumeId } })
}

function openNewForm(type: 'project' | 'internship' = 'project') {
  newExpType.value = type
  newExp.value = {
    title: '',
    role: '',
    organization: '',
    period: '',
    techStack: '',
    description: '',
    tags: '',
    targetResumeId: store.resumes[0]?.id || '',
  }
  showNewForm.value = true
}

function openNewSelfDescForm() {
  newSelfDesc.value = {
    selfEvaluation: '',
    careerObjective: '',
    personalSummary: '',
    tags: '',
    targetResumeId: store.resumes[0]?.id || '',
  }
  showNewForm.value = true
}

function saveNewExperience() {
  if (newExpType.value === 'project' && !newExp.value.title) {
    alert('请输入项目名称')
    return
  }
  if (newExpType.value === 'internship' && !newExp.value.organization) {
    alert('请输入公司名称')
    return
  }
  if (!newExp.value.targetResumeId) {
    alert('请先创建一份简历')
    return
  }
  
  // Convert bullet points (lines starting with - or •) to proper format
  const formatDescription = (desc: string) => {
    if (!desc) return ''
    return desc.split('\n').map(line => {
      const trimmed = line.trim()
      if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
        return trimmed
      }
      return trimmed
    }).filter(Boolean).join('\n')
  }
  
  const exp: ExperienceItem = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
    title: newExp.value.title || newExp.value.organization,
    role: newExp.value.role,
    organization: newExp.value.organization,
    period: newExp.value.period,
    techStack: newExp.value.techStack.split(',').map(s => s.trim()).filter(Boolean),
    description: formatDescription(newExp.value.description),
    tags: newExp.value.tags.split(',').map(s => s.trim()).filter(Boolean),
  }
  
  store.addExperience(newExp.value.targetResumeId, exp)
  showNewForm.value = false
  alert('已添加到简历')
}

function saveNewSelfDesc() {
  if (!newSelfDesc.value.targetResumeId) {
    alert('请先创建一份简历')
    return
  }
  if (!newSelfDesc.value.selfEvaluation && !newSelfDesc.value.careerObjective && !newSelfDesc.value.personalSummary) {
    alert('请至少填写一项内容')
    return
  }
  
  store.updateSelfDescription(newSelfDesc.value.targetResumeId, {
    selfEvaluation: newSelfDesc.value.selfEvaluation,
    careerObjective: newSelfDesc.value.careerObjective,
    personalSummary: newSelfDesc.value.personalSummary,
    tags: newSelfDesc.value.tags.split(',').map(s => s.trim()).filter(Boolean),
  })
  showNewForm.value = false
  alert('已添加到简历')
}

function closeNewForm() {
  showNewForm.value = false
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h1 class="section-title">经历库</h1>
      <!-- Project/Internship buttons -->
      <template v-if="activeCategory === 'project' || activeCategory === 'internship'">
        <div class="flex items-center gap-2">
          <button class="hand-btn hand-btn-primary flex items-center gap-1" @click="openNewForm('project')">
            <Plus :size="16" />
            <span>新增项目</span>
          </button>
          <button class="hand-btn bg-emerald-50 text-emerald-600 hover:bg-emerald-100 flex items-center gap-1" @click="openNewForm('internship')">
            <Plus :size="16" />
            <span>新增实习</span>
          </button>
        </div>
      </template>
      <!-- Self-desc button -->
      <template v-else>
        <div class="flex items-center gap-2">
          <button class="hand-btn hand-btn-primary flex items-center gap-1" @click="openNewSelfDescForm">
            <Plus :size="16" />
            <span>新增自我描述</span>
          </button>
        </div>
      </template>
    </div>
    <p class="text-sm text-gray-500 mb-6">
      所有简历中的项目/实习经历和自我描述汇聚于此，可深拷贝到任意简历。
    </p>

    <!-- Search -->
    <div class="relative mb-4">
      <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
      <input
        v-model="searchQuery"
        class="hand-input pl-9"
        placeholder="搜索项目名称、角色、技术栈、标签..."
      />
    </div>

    <!-- Category tabs -->
    <div class="flex gap-2 mb-6 border-b border-gray-200 pb-2">
      <button
        v-for="cat in categories"
        :key="cat.key"
        :class="[
          'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all',
          activeCategory === cat.key 
            ? 'bg-indigo-50 text-indigo-600' 
            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
        ]"
        @click="activeCategory = cat.key"
      >
        <component :is="cat.icon" :size="16" />
        {{ cat.label }}
      </button>
    </div>

    <!-- Tags cloud -->
    <div v-if="uniqueTags.length" class="flex flex-wrap gap-2 mb-6">
      <span
        v-for="tag in uniqueTags"
        :key="tag"
        class="tag cursor-pointer hover:bg-indigo-600 hover:text-white transition-colors"
        @click="searchQuery = tag"
      >
        #{{ tag }}
      </span>
    </div>

    <!-- Empty: experiences -->
    <div v-if="activeCategory !== 'self-desc' && allExperiences.filter(e => e._category === activeCategory).length === 0" class="card p-8 text-center">
      <BookOpen :size="40" class="mx-auto mb-3 text-gray-300" />
      <p class="font-medium text-gray-500">{{ activeCategory === 'project' ? '项目经历' : '实习经历' }}库为空~</p>
      <p class="text-sm text-gray-400 mt-1">在简历中添加{{ activeCategory === 'project' ? '项目' : '实习' }}经历后，会自动出现在这里</p>
    </div>

    <!-- Empty: self-desc -->
    <div v-if="activeCategory === 'self-desc' && allSelfDescriptions.length === 0" class="card p-8 text-center">
      <User :size="40" class="mx-auto mb-3 text-gray-300" />
      <p class="font-medium text-gray-500">自我描述库为空~</p>
      <p class="text-sm text-gray-400 mt-1">在简历中添加自我描述后，会自动出现在这里</p>
    </div>

    <!-- Experience cards -->
    <div v-else-if="activeCategory !== 'self-desc'" class="space-y-3">
      <div
        v-for="exp in filteredExperiences"
        :key="exp.id + '-' + exp._resumeId"
        class="card p-4"
      >
        <div class="flex items-start justify-between mb-2">
          <div>
            <h3 class="font-medium text-gray-900">{{ exp.title || '未命名项目' }}</h3>
            <p class="text-sm text-gray-500">{{ exp.role }}<span v-if="exp.organization"> · {{ exp.organization }}</span></p>
            <p v-if="exp.period" class="text-xs text-gray-400">{{ exp.period }}</p>
          </div>
          <div class="flex gap-1 shrink-0">
            <button
              class="hand-btn text-xs py-1 px-2"
              title="深拷贝到简历"
              @click="deepCopyToResume(exp)"
            >
              <Copy :size="12" />
              <span>复制</span>
            </button>
            <button
              class="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="查看原简历"
              @click="goToResume(exp._resumeId)"
            >
              <ExternalLink :size="12" class="text-gray-400" />
            </button>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="exp.tags.length" class="flex flex-wrap gap-1 mb-2">
          <span v-for="tag in exp.tags" :key="tag" class="tag">#{{ tag }}</span>
        </div>

        <!-- Tech stack -->
        <div v-if="exp.techStack.length" class="flex flex-wrap gap-1 mb-2">
          <span v-for="tech in exp.techStack" :key="tech" class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{{ tech }}</span>
        </div>

        <!-- Description -->
        <p v-if="exp.description" class="text-sm text-gray-600 line-clamp-3 whitespace-pre-line">
          {{ exp.description }}
        </p>

        <!-- Source -->
        <div class="text-xs text-gray-400 mt-2">
          来自：{{ exp._resumeTitle }}
        </div>
      </div>

      <div v-if="filteredExperiences.length === 0 && searchQuery" class="text-center py-8">
        <p class="text-gray-400">没有找到匹配的经历</p>
      </div>
    </div>

    <!-- Self-description cards -->
    <div v-else class="space-y-3">
      <div
        v-for="item in filteredSelfDesc"
        :key="item._resumeId"
        class="card p-4"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-medium text-gray-900">自我描述</h3>
            <p class="text-xs text-gray-400">来自：{{ item._resumeTitle }}</p>
          </div>
          <button
            class="hand-btn text-xs py-1 px-2"
            title="复制到简历"
            @click="copySelfDescToResume(item)"
          >
            <Copy :size="12" />
            <span>复制</span>
          </button>
        </div>

        <div v-if="item.selfEvaluation" class="mb-3">
          <p class="text-xs font-medium text-gray-500 mb-1">自我评价</p>
          <p class="text-sm text-gray-700 line-clamp-3">{{ item.selfEvaluation }}</p>
        </div>

        <div v-if="item.careerObjective" class="mb-3">
          <p class="text-xs font-medium text-gray-500 mb-1">职业目标</p>
          <p class="text-sm text-gray-700 line-clamp-2">{{ item.careerObjective }}</p>
        </div>

        <div v-if="item.personalSummary">
          <p class="text-xs font-medium text-gray-500 mb-1">个人总结</p>
          <p class="text-sm text-gray-700 line-clamp-3">{{ item.personalSummary }}</p>
        </div>

        <div v-if="item.tags.length" class="flex flex-wrap gap-1 mt-3 pt-3 border-t border-gray-100">
          <span v-for="tag in item.tags" :key="tag" class="tag">#{{ tag }}</span>
        </div>
      </div>

      <div v-if="filteredSelfDesc.length === 0 && searchQuery" class="text-center py-8">
        <p class="text-gray-400">没有找到匹配的自我描述</p>
      </div>
    </div>

    <!-- New Experience Modal - Different forms for project/internship/self-desc -->
    <div v-if="showNewForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="card w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <!-- Project Experience Form -->
        <template v-if="activeCategory !== 'self-desc' && newExpType === 'project'">
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-medium text-lg">新增项目经历</h3>
            <button class="p-1 hover:bg-gray-100 rounded" @click="closeNewForm">
              <X :size="20" class="text-gray-400" />
            </button>
          </div>
          <div class="p-4 space-y-4">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">添加到简历 *</label>
              <select v-model="newExp.targetResumeId" class="hand-input">
                <option value="">选择简历</option>
                <option v-for="r in store.resumes" :key="r.id" :value="r.id">{{ r.title }}</option>
              </select>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">项目名称 *</label>
              <input v-model="newExp.title" class="hand-input" placeholder="项目名称" />
            </div>
            
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-500 mb-1 block">角色</label>
                <input v-model="newExp.role" class="hand-input" placeholder="前端开发" />
              </div>
              <div>
                <label class="text-xs text-gray-500 mb-1 block">时间</label>
                <input v-model="newExp.period" class="hand-input" placeholder="2024.03 - 2024.06" />
              </div>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">技术栈（逗号分隔）</label>
              <input v-model="newExp.techStack" class="hand-input" placeholder="Vue, TypeScript, Node.js" />
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">项目描述（支持分点，每行以 - 或 • 开头）</label>
              <textarea v-model="newExp.description" class="hand-textarea" rows="5" placeholder="- 负责前端架构设计&#10;- 使用 Vue3 + TS 重构..."></textarea>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">标签（逗号分隔）</label>
              <input v-model="newExp.tags" class="hand-input" placeholder="后端, Python, 比赛" />
            </div>
          </div>
          <div class="flex justify-end gap-2 p-4 border-t border-gray-100">
            <button class="hand-btn" @click="closeNewForm">取消</button>
            <button class="hand-btn hand-btn-primary" @click="saveNewExperience">保存</button>
          </div>
        </template>

        <!-- Internship Experience Form -->
        <template v-else-if="activeCategory !== 'self-desc' && newExpType === 'internship'">
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-medium text-lg">新增实习经历</h3>
            <button class="p-1 hover:bg-gray-100 rounded" @click="closeNewForm">
              <X :size="20" class="text-gray-400" />
            </button>
          </div>
          <div class="p-4 space-y-4">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">添加到简历 *</label>
              <select v-model="newExp.targetResumeId" class="hand-input">
                <option value="">选择简历</option>
                <option v-for="r in store.resumes" :key="r.id" :value="r.id">{{ r.title }}</option>
              </select>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">公司名称 *</label>
              <input v-model="newExp.organization" class="hand-input" placeholder="公司名称" />
            </div>
            
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-500 mb-1 block">岗位</label>
                <input v-model="newExp.role" class="hand-input" placeholder="前端实习生" />
              </div>
              <div>
                <label class="text-xs text-gray-500 mb-1 block">时间</label>
                <input v-model="newExp.period" class="hand-input" placeholder="2024.06 - 2024.09" />
              </div>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">工作内容（支持分点，每行以 - 或 • 开头）</label>
              <textarea v-model="newExp.description" class="hand-textarea" rows="5" placeholder="- 参与需求评审会议&#10;- 负责 XX 模块开发..."></textarea>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">收获/技能（逗号分隔）</label>
              <input v-model="newExp.tags" class="hand-input" placeholder="团队协作, 业务理解" />
            </div>
          </div>
          <div class="flex justify-end gap-2 p-4 border-t border-gray-100">
            <button class="hand-btn" @click="closeNewForm">取消</button>
            <button class="hand-btn bg-emerald-500 text-white hover:bg-emerald-600" @click="saveNewExperience">保存</button>
          </div>
        </template>

        <!-- Self Description Form -->
        <template v-else>
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-medium text-lg">新增自我描述</h3>
            <button class="p-1 hover:bg-gray-100 rounded" @click="closeNewForm">
              <X :size="20" class="text-gray-400" />
            </button>
          </div>
          <div class="p-4 space-y-4">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">添加到简历 *</label>
              <select v-model="newSelfDesc.targetResumeId" class="hand-input">
                <option value="">选择简历</option>
                <option v-for="r in store.resumes" :key="r.id" :value="r.id">{{ r.title }}</option>
              </select>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">自我评价</label>
              <textarea v-model="newSelfDesc.selfEvaluation" class="hand-textarea" rows="3" placeholder="热爱技术，具备良好的学习能力和团队协作能力..."></textarea>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">职业目标</label>
              <textarea v-model="newSelfDesc.careerObjective" class="hand-textarea" rows="2" placeholder="希望从事前端开发工作..."></textarea>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">个人总结</label>
              <textarea v-model="newSelfDesc.personalSummary" class="hand-textarea" rows="3" placeholder="个人优势总结..."></textarea>
            </div>
            
            <div>
              <label class="text-xs text-gray-500 mb-1 block">标签（逗号分隔）</label>
              <input v-model="newSelfDesc.tags" class="hand-input" placeholder="主动学习, 责任心强" />
            </div>
          </div>
          <div class="flex justify-end gap-2 p-4 border-t border-gray-100">
            <button class="hand-btn" @click="closeNewForm">取消</button>
            <button class="hand-btn hand-btn-primary" @click="saveNewSelfDesc">保存</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
