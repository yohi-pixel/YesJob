<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '@/stores/resume'
import { Copy, Search, FolderOpen, Briefcase, User, Plus, X, Check } from 'lucide-vue-next'
import type { ExperienceItem, SelfDescription } from '@/types'

const router = useRouter()
const store = useResumeStore()

const resumeTitle = ref('')
const searchQuery = ref('')
const selectedExpIds = ref<string[]>([])
const selectedSelfDesc = ref<{
  selfEvaluation: boolean
  careerObjective: boolean
  personalSummary: boolean
}>({
  selfEvaluation: false,
  careerObjective: false,
  personalSummary: false,
})

// Get all experiences from all resumes
const allExperiences = computed(() => {
  const list: (ExperienceItem & { _resumeId: string, _resumeTitle: string })[] = []
  for (const r of store.resumes) {
    for (const exp of r.experiences) {
      list.push({
        ...exp,
        _resumeId: r.id,
        _resumeTitle: r.title,
      })
    }
  }
  return list
})

// Get all self-descriptions from all resumes
const allSelfDescriptions = computed(() => {
  const list: (SelfDescription & { _resumeId: string, _resumeTitle: string })[] = []
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

// Filtered experiences
const filteredExperiences = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return allExperiences.value
  return allExperiences.value.filter(e =>
    e.title.toLowerCase().includes(q) ||
    e.role.toLowerCase().includes(q) ||
    e.organization.toLowerCase().includes(q) ||
    e.tags.some(t => t.toLowerCase().includes(q)) ||
    e.techStack.some(t => t.toLowerCase().includes(q))
  )
})

function toggleExp(id: string) {
  const idx = selectedExpIds.value.indexOf(id)
  if (idx >= 0) {
    selectedExpIds.value.splice(idx, 1)
  } else {
    selectedExpIds.value.push(id)
  }
}

function isExpSelected(id: string): boolean {
  return selectedExpIds.value.includes(id)
}

function toggleSelfDesc(field: 'selfEvaluation' | 'careerObjective' | 'personalSummary') {
  selectedSelfDesc.value[field] = !selectedSelfDesc.value[field]
}

function hasSelectedItems(): boolean {
  return selectedExpIds.value.length > 0 || 
    selectedSelfDesc.value.selfEvaluation || 
    selectedSelfDesc.value.careerObjective || 
    selectedSelfDesc.value.personalSummary
}

function assembleResume() {
  if (!resumeTitle.value.trim()) {
    alert('请输入简历标题')
    return
  }
  if (!hasSelectedItems()) {
    alert('请至少选择一项经历或自我描述')
    return
  }

  // Create new resume
  const resume = store.createResume(resumeTitle.value.trim())

  // Add selected experiences
  const selectedExps = allExperiences.value.filter(e => selectedExpIds.value.includes(e.id))
  for (const exp of selectedExps) {
    const newExp: ExperienceItem = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
      title: exp.title,
      role: exp.role,
      organization: exp.organization,
      period: exp.period,
      techStack: [...exp.techStack],
      description: exp.description,
      tags: [...exp.tags],
    }
    store.addExperience(resume.id, newExp)
  }

  // Add selected self-description
  if (selectedSelfDesc.value.selfEvaluation || selectedSelfDesc.value.careerObjective || selectedSelfDesc.value.personalSummary) {
    const sourceSelfDesc = allSelfDescriptions.value[0] // Use first one as source
    store.updateSelfDescription(resume.id, {
      selfEvaluation: selectedSelfDesc.value.selfEvaluation && sourceSelfDesc ? sourceSelfDesc.selfEvaluation : '',
      careerObjective: selectedSelfDesc.value.careerObjective && sourceSelfDesc ? sourceSelfDesc.careerObjective : '',
      personalSummary: selectedSelfDesc.value.personalSummary && sourceSelfDesc ? sourceSelfDesc.personalSummary : '',
      tags: sourceSelfDesc?.tags || [],
    })
  }

  router.push({ name: 'resume-edit', params: { id: resume.id } })
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="section-title mb-4">简历组装</h1>
    <p class="text-sm text-gray-500 mb-6">
      从经历库中选择项目经历、实习经历和自我描述，组装成一份新简历。
    </p>

    <!-- Resume Title -->
    <div class="card p-4 mb-6">
      <label class="text-xs text-gray-500 mb-2 block">简历标题 *</label>
      <input 
        v-model="resumeTitle" 
        class="hand-input" 
        placeholder="例如：前端开发简历 - 2024届"
      />
    </div>

    <!-- Search -->
    <div class="relative mb-4">
      <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
      <input
        v-model="searchQuery"
        class="hand-input pl-9"
        placeholder="搜索经历名称、角色、技术栈..."
      />
    </div>

    <!-- Project Experiences -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-3">
        <FolderOpen :size="18" class="text-indigo-500" />
        <h2 class="font-medium text-gray-900">项目经历</h2>
        <span class="text-xs text-gray-400">({{ selectedExpIds.length }} / {{ filteredExperiences.length }} 已选)</span>
      </div>
      
      <div v-if="filteredExperiences.length === 0" class="card p-6 text-center">
        <FolderOpen :size="32" class="mx-auto mb-2 text-gray-300" />
        <p class="text-sm text-gray-400">暂无项目经历，请先在经历库中添加</p>
      </div>
      
      <div v-else class="space-y-2">
        <div
          v-for="exp in filteredExperiences"
          :key="exp.id"
          :class="[
            'card p-3 cursor-pointer transition-all',
            isExpSelected(exp.id) ? 'ring-2 ring-indigo-500 bg-indigo-50' : 'hover:bg-gray-50'
          ]"
          @click="toggleExp(exp.id)"
        >
          <div class="flex items-start gap-3">
            <div :class="[
              'w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 mt-0.5',
              isExpSelected(exp.id) ? 'bg-indigo-500 border-indigo-500' : 'border-gray-300'
            ]">
              <Check v-if="isExpSelected(exp.id)" :size="12" class="text-white" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-900">{{ exp.title }}</h3>
              <p class="text-sm text-gray-500">{{ exp.role }}<span v-if="exp.organization"> · {{ exp.organization }}</span></p>
              <p v-if="exp.period" class="text-xs text-gray-400">{{ exp.period }}</p>
              <div v-if="exp.techStack.length" class="flex flex-wrap gap-1 mt-2">
                <span v-for="tech in exp.techStack.slice(0, 5)" :key="tech" class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{{ tech }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">来自：{{ exp._resumeTitle }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Self Descriptions -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-3">
        <User :size="18" class="text-emerald-500" />
        <h2 class="font-medium text-gray-900">自我描述</h2>
        <span class="text-xs text-gray-400">
          (
          <span :class="selectedSelfDesc.selfEvaluation ? 'text-emerald-600' : 'text-gray-400'">自我评价</span> / 
          <span :class="selectedSelfDesc.careerObjective ? 'text-emerald-600' : 'text-gray-400'">职业目标</span> / 
          <span :class="selectedSelfDesc.personalSummary ? 'text-emerald-600' : 'text-gray-400'">个人总结</span>
          )
        </span>
      </div>
      
      <div v-if="allSelfDescriptions.length === 0" class="card p-6 text-center">
        <User :size="32" class="mx-auto mb-2 text-gray-300" />
        <p class="text-sm text-gray-400">暂无自我描述，请先在经历库中添加</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="selfDesc in allSelfDescriptions"
          :key="selfDesc._resumeId"
          class="card p-4"
        >
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs text-gray-400">来自：{{ selfDesc._resumeTitle }}</span>
          </div>
          
          <div class="space-y-3">
            <!-- Self Evaluation -->
            <div v-if="selfDesc.selfEvaluation" class="flex items-start gap-3">
              <div 
                :class="[
                  'w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 mt-0.5 cursor-pointer',
                  selectedSelfDesc.selfEvaluation ? 'bg-emerald-500 border-emerald-500' : 'border-gray-300 hover:border-emerald-400'
                ]"
                @click="toggleSelfDesc('selfEvaluation')"
              >
                <Check v-if="selectedSelfDesc.selfEvaluation" :size="12" class="text-white" />
              </div>
              <div class="flex-1">
                <p class="text-xs font-medium text-gray-500 mb-1">自我评价</p>
                <p class="text-sm text-gray-700 line-clamp-2">{{ selfDesc.selfEvaluation }}</p>
              </div>
            </div>
            
            <!-- Career Objective -->
            <div v-if="selfDesc.careerObjective" class="flex items-start gap-3">
              <div 
                :class="[
                  'w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 mt-0.5 cursor-pointer',
                  selectedSelfDesc.careerObjective ? 'bg-emerald-500 border-emerald-500' : 'border-gray-300 hover:border-emerald-400'
                ]"
                @click="toggleSelfDesc('careerObjective')"
              >
                <Check v-if="selectedSelfDesc.careerObjective" :size="12" class="text-white" />
              </div>
              <div class="flex-1">
                <p class="text-xs font-medium text-gray-500 mb-1">职业目标</p>
                <p class="text-sm text-gray-700 line-clamp-2">{{ selfDesc.careerObjective }}</p>
              </div>
            </div>
            
            <!-- Personal Summary -->
            <div v-if="selfDesc.personalSummary" class="flex items-start gap-3">
              <div 
                :class="[
                  'w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 mt-0.5 cursor-pointer',
                  selectedSelfDesc.personalSummary ? 'bg-emerald-500 border-emerald-500' : 'border-gray-300 hover:border-emerald-400'
                ]"
                @click="toggleSelfDesc('personalSummary')"
              >
                <Check v-if="selectedSelfDesc.personalSummary" :size="12" class="text-white" />
              </div>
              <div class="flex-1">
                <p class="text-xs font-medium text-gray-500 mb-1">个人总结</p>
                <p class="text-sm text-gray-700 line-clamp-2">{{ selfDesc.personalSummary }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assemble Button -->
    <div class="sticky bottom-4">
      <button
        class="hand-btn hand-btn-primary w-full py-3 text-lg flex items-center justify-center gap-2"
        :disabled="!hasSelectedItems()"
        @click="assembleResume"
      >
        <Plus :size="20" />
        <span>组装简历</span>
      </button>
    </div>
  </div>
</template>
