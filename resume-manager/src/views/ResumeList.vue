<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '@/stores/resume'
import { parseResume } from '@/services/api'
import {
  Plus,
  Upload,
  FileText,
  Copy,
  Trash2,
  Edit3,
  CheckCircle,
  Circle,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronRight,
  User,
} from 'lucide-vue-next'
import type { Resume } from '@/types'

const router = useRouter()
const store = useResumeStore()

const uploading = ref(false)
const uploadError = ref('')
const expandedCard = ref<string | null>(null)

const resumes = computed(() => store.resumes)

function getStatusInfo(resume: Resume) {
  const hasBasic = !!resume.basicInfo.name
  const hasExp = resume.experiences.length > 0
  const hasSelf = !!resume.selfDescription.selfEvaluation ||
    !!resume.selfDescription.careerObjective ||
    !!resume.selfDescription.personalSummary
  return { hasBasic, hasExp, hasSelf }
}

function toggleExpand(id: string) {
  expandedCard.value = expandedCard.value === id ? null : id
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  uploading.value = true
  uploadError.value = ''

  try {
    const result = await parseResume(file)
    const resume = store.createResume(file.name.replace(/\.[^.]+$/, ''))

    if (result.experiences?.length) {
      resume.experiences = result.experiences.map(exp => ({
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
        title: exp.title,
        role: exp.role,
        organization: exp.organization,
        period: exp.period,
        techStack: exp.tech_stack || [],
        description: exp.description,
        tags: exp.tags || [],
      }))
    }
    if (result.self_description) {
      resume.selfDescription = {
        selfEvaluation: result.self_description.self_evaluation || '',
        careerObjective: result.self_description.career_objective || '',
        personalSummary: result.self_description.personal_summary || '',
        tags: result.self_description.tags || [],
      }
    }
    store.updateResume(resume.id, {
      experiences: resume.experiences,
      selfDescription: resume.selfDescription,
    })
    router.push({ name: 'resume-edit', params: { id: resume.id } })
  } catch (e: any) {
    uploadError.value = e.message || '上传解析失败'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function handleCreate() {
  const resume = store.createResume()
  expandedCard.value = resume.id  // Auto expand new resume
}

function handleEdit(id: string) {
  router.push({ name: 'resume-edit', params: { id } })
}

function handleDuplicate(id: string) {
  const copy = store.duplicateResume(id)
  if (copy) router.push({ name: 'resume-edit', params: { id: copy.id } })
}

function handleDelete(id: string, event: MouseEvent) {
  event.stopPropagation()
  if (confirm('确定删除这份简历吗？')) {
    store.deleteResume(id)
  }
}

function updateBasicInfo(resumeId: string, field: string, value: string) {
  store.updateBasicInfo(resumeId, { [field]: value })
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="section-title">我的简历</h1>
      <div class="flex gap-2">
        <button class="hand-btn" @click="handleCreate">
          <Plus :size="16" />
          <span>新建简历</span>
        </button>
        <label class="hand-btn cursor-pointer">
          <Upload :size="16" />
          <span>{{ uploading ? '解析中...' : '上传解析' }}</span>
          <input
            type="file"
            accept=".pdf,.docx"
            class="hidden"
            :disabled="uploading"
            @change="handleUpload"
          />
        </label>
      </div>
    </div>

    <!-- Upload error -->
    <div v-if="uploadError" class="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
      <div class="flex items-center gap-2">
        <AlertCircle :size="16" class="text-red-500" />
        <span class="text-sm text-red-600">{{ uploadError }}</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!uploading && resumes.length === 0" class="text-center py-16">
      <div class="inline-block card p-8 max-w-md">
        <FileText :size="48" class="mx-auto mb-4 text-gray-300" />
        <p class="font-medium text-gray-600 mb-2">还没有简历哦~</p>
        <p class="text-sm text-gray-400">
          点击「新建简历」手动创建，或「上传解析」从 PDF/Word 导入经历
        </p>
      </div>
    </div>

    <!-- Resume cards -->
    <div v-else class="space-y-4">
      <div
        v-for="resume in resumes"
        :key="resume.id"
        class="card overflow-hidden"
      >
        <!-- Card Header -->
        <div 
          class="flex items-center gap-3 p-4 cursor-pointer hover:bg-gray-50"
          @click="toggleExpand(resume.id)"
        >
          <component 
            :is="expandedCard === resume.id ? ChevronDown : ChevronRight" 
            :size="18" 
            class="text-gray-400" 
          />
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-gray-900 truncate">
              {{ resume.title || '未命名简历' }}
            </h3>
            <div class="flex flex-wrap gap-2 mt-1">
              <span
                :class="[
                  'inline-flex items-center px-2 py-0.5 text-xs rounded',
                  getStatusInfo(resume).hasBasic ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-400'
                ]"
              >
                <CheckCircle v-if="getStatusInfo(resume).hasBasic" :size="10" class="mr-1" />
                <Circle v-else :size="10" class="mr-1 opacity-40" />
                基本信息
              </span>
              <span
                :class="[
                  'inline-flex items-center px-2 py-0.5 text-xs rounded',
                  getStatusInfo(resume).hasExp ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-400'
                ]"
              >
                <CheckCircle v-if="getStatusInfo(resume).hasExp" :size="10" class="mr-1" />
                <Circle v-else :size="10" class="mr-1 opacity-40" />
                经历
              </span>
              <span
                :class="[
                  'inline-flex items-center px-2 py-0.5 text-xs rounded',
                  getStatusInfo(resume).hasSelf ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-400'
                ]"
              >
                <CheckCircle v-if="getStatusInfo(resume).hasSelf" :size="10" class="mr-1" />
                <Circle v-else :size="10" class="mr-1 opacity-40" />
                自我描述
              </span>
            </div>
          </div>
          <div class="flex gap-1 shrink-0" @click.stop>
            <button
              class="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="复制"
              @click="handleDuplicate(resume.id)"
            >
              <Copy :size="14" class="text-gray-400" />
            </button>
            <button
              class="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="编辑详情"
              @click="handleEdit(resume.id)"
            >
              <Edit3 :size="14" class="text-indigo-500" />
            </button>
            <button
              class="p-1.5 hover:bg-red-50 rounded transition-colors"
              title="删除"
              @click="handleDelete(resume.id, $event)"
            >
              <Trash2 :size="14" class="text-red-400" />
            </button>
          </div>
        </div>

        <!-- Expanded Basic Info Form -->
        <div v-if="expandedCard === resume.id" class="border-t border-gray-100 p-4 bg-gray-50">
          <div class="flex items-center gap-2 mb-4">
            <User :size="16" class="text-indigo-500" />
            <span class="font-medium text-gray-900">基本信息</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">姓名</label>
              <input 
                class="hand-input text-sm" 
                placeholder="请输入姓名"
                :value="resume.basicInfo.name"
                @input="updateBasicInfo(resume.id, 'name', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">手机</label>
              <input 
                class="hand-input text-sm" 
                placeholder="138xxxxxxx"
                :value="resume.basicInfo.phone"
                @input="updateBasicInfo(resume.id, 'phone', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">邮箱</label>
              <input 
                class="hand-input text-sm" 
                placeholder="xx@xx.com"
                :value="resume.basicInfo.email"
                @input="updateBasicInfo(resume.id, 'email', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">学校</label>
              <input 
                class="hand-input text-sm" 
                placeholder="XX大学"
                :value="resume.basicInfo.school"
                @input="updateBasicInfo(resume.id, 'school', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">学历</label>
              <select 
                class="hand-input text-sm"
                :value="resume.basicInfo.degree"
                @change="updateBasicInfo(resume.id, 'degree', ($event.target as HTMLSelectElement).value)"
              >
                <option value="">请选择</option>
                <option>本科</option>
                <option>硕士</option>
                <option>博士</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">专业</label>
              <input 
                class="hand-input text-sm" 
                placeholder="专业"
                :value="resume.basicInfo.major"
                @input="updateBasicInfo(resume.id, 'major', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">年级</label>
              <input 
                class="hand-input text-sm" 
                placeholder="2025届/大三"
                :value="resume.basicInfo.grade"
                @input="updateBasicInfo(resume.id, 'grade', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">GPA</label>
              <input 
                class="hand-input text-sm" 
                placeholder="3.8/4.0"
                :value="resume.basicInfo.gpa"
                @input="updateBasicInfo(resume.id, 'gpa', ($event.target as HTMLInputElement).value)"
              />
            </div>
          </div>
          <div class="mt-3 flex justify-end">
            <button 
              class="hand-btn hand-btn-primary text-xs"
              @click="handleEdit(resume.id)"
            >
              编辑详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="uploading" class="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
      <div class="card p-6 text-center">
        <Loader2 :size="32" class="mx-auto mb-3 text-indigo-500 animate-spin" />
        <p class="font-medium text-lg">正在解析简历...</p>
        <p class="text-sm text-gray-400 mt-1">提取项目经历与自我描述中</p>
      </div>
    </div>
  </div>
</template>
