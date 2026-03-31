<script setup lang="ts">
import { Plus, X, GripVertical } from 'lucide-vue-next'
import type { ExperienceItem } from '@/types'
import { useResumeStore } from '@/stores/resume'

const props = defineProps<{
  resumeId: string
  experiences: ExperienceItem[]
}>()

const emit = defineEmits<{
  (e: 'ai-optimize', expId: string): void
}>()

const store = useResumeStore()

function addExp() {
  store.addExperience(props.resumeId)
}

function removeExp(id: string) {
  store.removeExperience(props.resumeId, id)
}

function updateField(id: string, field: keyof ExperienceItem, value: any) {
  store.updateExperience(props.resumeId, id, { [field]: value })
}

function addTag(id: string) {
  const exp = props.experiences.find(e => e.id === id)
  if (!exp) return
  const tag = prompt('输入岗位标签：')
  if (tag?.trim()) {
    const tags = [...exp.tags, tag.trim()]
    store.updateExperience(props.resumeId, id, { tags })
  }
}

function removeTag(id: string, tagIndex: number) {
  const exp = props.experiences.find(e => e.id === id)
  if (!exp) return
  const tags = exp.tags.filter((_: string, i: number) => i !== tagIndex)
  store.updateExperience(props.resumeId, id, { tags })
}

function addTech(id: string) {
  const exp = props.experiences.find(e => e.id === id)
  if (!exp) return
  const tech = prompt('输入技术栈：')
  if (tech?.trim()) {
    const techStack = [...exp.techStack, tech.trim()]
    store.updateExperience(props.resumeId, id, { techStack })
  }
}

function removeTech(id: string, techIndex: number) {
  const exp = props.experiences.find(e => e.id === id)
  if (!exp) return
  const techStack = exp.techStack.filter((_: string, i: number) => i !== techIndex)
  store.updateExperience(props.resumeId, id, { techStack })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="section-title">经历与项目</h2>
      <button class="hand-btn hand-btn-primary text-xs" @click="addExp">
        <Plus :size="14" />
        <span>添加经历</span>
      </button>
    </div>

    <div v-if="experiences.length === 0" class="sticky-note note-blue p-4 text-center mb-4">
      <p class="font-hand text-sm text-ink-light">
        暂无经历，点击「添加经历」或上传简历自动解析
      </p>
    </div>

    <div class="space-y-4">
      <div
        v-for="(exp, idx) in experiences"
        :key="exp.id"
        class="sticky-note"
        :class="idx % 3 === 0 ? 'note-yellow' : idx % 3 === 1 ? 'note-blue' : 'note-green'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <GripVertical :size="14" class="text-pencil-light cursor-grab" />
            <span class="font-hand text-sm text-pencil-light">#{{ idx + 1 }}</span>
          </div>
          <div class="flex gap-1">
            <button
              v-if="exp.description"
              class="p-1 hover:bg-note-yellow rounded transition-colors"
              title="AI 优化"
              @click="emit('ai-optimize', exp.id)"
            >
              <span class="text-xs">✨</span>
            </button>
            <button
              class="p-1 hover:bg-red-100 rounded transition-colors"
              @click="removeExp(exp.id)"
            >
              <X :size="14" class="text-red-400" />
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">项目/岗位名称 *</label>
            <input
              class="hand-input"
              placeholder="如：电商后台系统"
              :value="exp.title"
              @input="updateField(exp.id, 'title', ($event.target as HTMLInputElement).value)"
            />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">角色 *</label>
            <input
              class="hand-input"
              placeholder="如：后端开发"
              :value="exp.role"
              @input="updateField(exp.id, 'role', ($event.target as HTMLInputElement).value)"
            />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">组织/公司</label>
            <input
              class="hand-input"
              placeholder="如：XX科技有限公司"
              :value="exp.organization"
              @input="updateField(exp.id, 'organization', ($event.target as HTMLInputElement).value)"
            />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">时间段</label>
            <input
              class="hand-input"
              placeholder="如：2024.06 - 2024.09"
              :value="exp.period"
              @input="updateField(exp.id, 'period', ($event.target as HTMLInputElement).value)"
            />
          </div>
        </div>

        <div class="mb-3">
          <label class="text-xs text-pencil font-medium mb-1 block">技术栈</label>
          <div class="flex flex-wrap gap-1.5 mb-1">
            <span
              v-for="(tech, ti) in exp.techStack"
              :key="ti"
              class="tag tag-green text-xs flex items-center gap-1"
            >
              {{ tech }}
              <button @click="removeTech(exp.id, ti)" class="hover:text-red-500"><X :size="10" /></button>
            </span>
          </div>
          <button class="text-xs text-accent hover:underline cursor-pointer" @click="addTech(exp.id)">+ 添加技术栈</button>
        </div>

        <div class="mb-3">
          <label class="text-xs text-pencil font-medium mb-1 block">详细描述</label>
          <textarea
            class="hand-input min-h-[100px]"
            placeholder="使用 STAR 法则描述：情境、任务、行动、结果"
            :value="exp.description"
            @input="updateField(exp.id, 'description', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>

        <div>
          <label class="text-xs text-pencil font-medium mb-1 block">岗位标签</label>
          <div class="flex flex-wrap gap-1.5 mb-1">
            <span
              v-for="(tag, ti) in exp.tags"
              :key="ti"
              class="tag text-xs flex items-center gap-1"
            >
              #{{ tag }}
              <button @click="removeTag(exp.id, ti)" class="hover:text-red-500"><X :size="10" /></button>
            </span>
          </div>
          <button class="text-xs text-accent hover:underline cursor-pointer" @click="addTag(exp.id)">+ 添加标签</button>
        </div>
      </div>
    </div>
  </div>
</template>
