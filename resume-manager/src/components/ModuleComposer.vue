<script setup lang="ts">
import { computed } from 'vue'
import { useResumeStore } from '@/stores/resume'
import { Eye, EyeOff } from 'lucide-vue-next'
import type { Resume } from '@/types'

const props = defineProps<{
  resumeId: string
  resume: Resume
}>()

const store = useResumeStore()

const modules = computed(() => [
  {
    key: 'basicInfo',
    label: '基本信息',
    enabled: !!props.resume.basicInfo.name,
    count: null as number | null,
  },
  {
    key: 'experiences',
    label: '经历与项目',
    enabled: props.resume.experiences.length > 0,
    count: props.resume.experiences.length,
  },
  {
    key: 'selfDescription',
    label: '自我描述',
    enabled: !!(
      props.resume.selfDescription.selfEvaluation ||
      props.resume.selfDescription.careerObjective ||
      props.resume.selfDescription.personalSummary
    ),
    count: null as number | null,
  },
])

function toggleModule(key: string) {
  // This is a visual indicator only — all modules are always saved.
  // The "enabled" state reflects whether the module has content.
}
</script>

<template>
  <div class="sticky-note note-yellow mb-6">
    <h3 class="font-hand text-base text-ink mb-3">模块拼接</h3>
    <p class="text-xs text-pencil-light mb-3">
      以下显示当前简历各模块的内容状态。有内容的模块将包含在导出 PDF 中。
    </p>
    <div class="space-y-2">
      <div
        v-for="mod in modules"
        :key="mod.key"
        :class="[
          'flex items-center justify-between p-2.5 rounded-lg transition-colors',
          mod.enabled ? 'bg-white/50' : 'bg-white/20 opacity-60',
        ]"
      >
        <div class="flex items-center gap-2">
          <component
            :is="mod.enabled ? Eye : EyeOff"
            :size="16"
            :class="mod.enabled ? 'text-accent' : 'text-pencil-light'"
          />
          <span class="text-sm font-medium">{{ mod.label }}</span>
          <span v-if="mod.count !== null" class="text-xs text-pencil-light">({{ mod.count }})</span>
        </div>
        <span
          :class="[
            'text-xs px-2 py-0.5 rounded-full',
            mod.enabled
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-400',
          ]"
        >
          {{ mod.enabled ? '有内容' : '未填写' }}
        </span>
      </div>
    </div>
  </div>
</template>
