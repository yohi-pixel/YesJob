<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResumeStore } from '@/stores/resume'
import { optimizeContent } from '@/services/api'
import { ArrowLeft, Upload, Loader2, Download } from 'lucide-vue-next'
import BasicInfoForm from '@/components/BasicInfoForm.vue'
import ExperienceForm from '@/components/ExperienceForm.vue'
import SelfDescriptionForm from '@/components/SelfDescriptionForm.vue'
import ModuleComposer from '@/components/ModuleComposer.vue'
import type { OptimizeRequest } from '@/types'

const props = defineProps<{ id: string }>()

const route = useRoute()
const router = useRouter()
const store = useResumeStore()

type Tab = 'basic' | 'experience' | 'self-desc'
const activeTab = ref<Tab>('basic')
const aiLoading = ref(false)
const aiTarget = ref('')

const resume = computed(() => {
  return store.resumes.find(r => r.id === props.id) ?? null
})

const tabs: { key: Tab; label: string }[] = [
  { key: 'basic', label: '基本信息' },
  { key: 'experience', label: '经历与项目' },
  { key: 'self-desc', label: '自我描述' },
]

onMounted(() => {
  if (resume.value) {
    store.setCurrent(resume.value.id)
  } else {
    router.replace('/')
  }
})

function updateTitle(e: Event) {
  store.updateResume(props.id, { title: (e.target as HTMLInputElement).value })
}

function goBack() {
  router.push('/')
}

// Upload & parse additional file for current resume
async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !resume.value) return

  aiLoading.value = true
  aiTarget.value = '解析中...'

  try {
    const { parseResume } = await import('@/services/api')
    const result = await parseResume(file)

    if (result.experiences?.length) {
      const newExps = result.experiences.map(exp => ({
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
        title: exp.title,
        role: exp.role,
        organization: exp.organization,
        period: exp.period,
        techStack: exp.tech_stack || [],
        description: exp.description,
        tags: exp.tags || [],
      }))
      store.updateResume(props.id, {
        experiences: [...resume.value.experiences, ...newExps],
      })
    }

    if (result.self_description) {
      store.updateSelfDescription(props.id, {
        selfEvaluation: result.self_description.self_evaluation || resume.value.selfDescription.selfEvaluation,
        careerObjective: result.self_description.career_objective || resume.value.selfDescription.careerObjective,
        personalSummary: result.self_description.personal_summary || resume.value.selfDescription.personalSummary,
        tags: result.self_description.tags || resume.value.selfDescription.tags,
      })
    }

    activeTab.value = 'experience'
  } catch (err: any) {
    alert('解析失败：' + (err.message || '未知错误'))
  } finally {
    aiLoading.value = false
    aiTarget.value = ''
    input.value = ''
  }
}

// AI optimize experience
async function handleAiOptimizeExp(expId: string) {
  const exp = resume.value?.experiences.find(e => e.id === expId)
  if (!exp?.description || !exp.tags.length) {
    alert('请先填写描述并添加至少一个岗位标签')
    return
  }

  const tag = prompt(`选择优化目标标签（当前有：${exp.tags.join(', ')}）：`) || exp.tags[0]
  aiLoading.value = true
  aiTarget.value = `优化「${exp.title}」`

  try {
    const req: OptimizeRequest = {
      content: exp.description,
      target_tag: tag,
      section_type: 'experience',
    }
    const result = await optimizeContent(req)
    store.updateExperience(props.id, expId, { description: result.optimized_content })
  } catch (err: any) {
    alert('AI 优化失败：' + (err.message || '请检查后端服务'))
  } finally {
    aiLoading.value = false
    aiTarget.value = ''
  }
}

// AI optimize self-description field
async function handleAiOptimizeSelf(field: 'selfEvaluation' | 'careerObjective' | 'personalSummary') {
  const desc = resume.value?.selfDescription
  if (!desc) return

  const content = desc[field]
  if (!content) {
    alert('请先填写内容')
    return
  }

  const tag = desc.tags.length
    ? (prompt(`选择优化目标标签（当前有：${desc.tags.join(', ')}）：`) || desc.tags[0])
    : '通用'

  aiLoading.value = true
  aiTarget.value = `优化自我描述`

  try {
    const req: OptimizeRequest = {
      content,
      target_tag: tag,
      section_type: 'self_description',
    }
    const result = await optimizeContent(req)
    store.updateSelfDescription(props.id, { [field]: result.optimized_content })
  } catch (err: any) {
    alert('AI 优化失败：' + (err.message || '请检查后端服务'))
  } finally {
    aiLoading.value = false
    aiTarget.value = ''
  }
}
</script>

<template>
  <div v-if="resume" class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-4">
      <button class="hand-btn text-xs" @click="goBack">
        <ArrowLeft :size="14" />
        <span>返回</span>
      </button>
      <input
        class="hand-input flex-1 text-lg font-hand"
        :value="resume.title"
        @input="updateTitle"
      />
      <label class="hand-btn text-xs cursor-pointer">
        <Upload :size="14" />
        <span>追加上传</span>
        <input type="file" accept=".pdf,.docx" class="hidden" @change="handleUpload" />
      </label>
      <router-link :to="{ name: 'resume-export', params: { id: resume.id } }" class="hand-btn hand-btn-primary text-xs">
        <Download :size="14" />
        <span>导出PDF</span>
      </router-link>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 mb-6 border-b border-gray-200 pb-2">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="[
          'hand-btn text-xs',
          activeTab === tab.key ? 'hand-btn-primary' : '',
        ]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Module composer -->
    <ModuleComposer :resume-id="resume.id" :resume="resume" />

    <!-- Tab content -->
    <div>
      <BasicInfoForm
        v-if="activeTab === 'basic'"
        :resume-id="resume.id"
        :basic-info="resume.basicInfo"
      />
      <ExperienceForm
        v-if="activeTab === 'experience'"
        :resume-id="resume.id"
        :experiences="resume.experiences"
        @ai-optimize="handleAiOptimizeExp"
      />
      <SelfDescriptionForm
        v-if="activeTab === 'self-desc'"
        :resume-id="resume.id"
        :self-description="resume.selfDescription"
        @ai-optimize="handleAiOptimizeSelf"
      />
    </div>

    <!-- AI loading overlay -->
    <div v-if="aiLoading" class="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
      <div class="card p-6 text-center">
        <Loader2 :size="28" class="mx-auto mb-3 text-indigo-500 animate-spin" />
        <p class="font-medium text-lg">{{ aiTarget }}...</p>
        <p class="text-sm text-gray-400 mt-1">DeepSeek 正在为你优化</p>
      </div>
    </div>
  </div>
</template>
