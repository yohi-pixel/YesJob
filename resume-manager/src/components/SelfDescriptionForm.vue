<script setup lang="ts">
import { Plus, X } from 'lucide-vue-next'
import type { SelfDescription } from '@/types'
import { useResumeStore } from '@/stores/resume'

const props = defineProps<{
  resumeId: string
  selfDescription: SelfDescription
}>()

const emit = defineEmits<{
  (e: 'ai-optimize', field: 'selfEvaluation' | 'careerObjective' | 'personalSummary'): void
}>()

const store = useResumeStore()
const desc = props.selfDescription

function update(patch: Partial<SelfDescription>) {
  store.updateSelfDescription(props.resumeId, patch)
}

function addTag() {
  const tag = prompt('输入岗位标签：')
  if (tag?.trim()) {
    update({ tags: [...desc.tags, tag.trim()] })
  }
}

function removeTag(index: number) {
  update({ tags: desc.tags.filter((_: string, i: number) => i !== index) })
}
</script>

<template>
  <div>
    <h2 class="section-title mb-4">自我描述</h2>

    <!-- Tags -->
    <div class="mb-4">
      <label class="text-xs text-pencil font-medium mb-1 block">岗位标签</label>
      <div class="flex flex-wrap gap-1.5 mb-1">
        <span
          v-for="(tag, ti) in desc.tags"
          :key="ti"
          class="tag text-xs flex items-center gap-1"
        >
          #{{ tag }}
          <button @click="removeTag(ti)" class="hover:text-red-500"><X :size="10" /></button>
        </span>
      </div>
      <button class="text-xs text-accent hover:underline cursor-pointer" @click="addTag">+ 添加标签</button>
    </div>

    <!-- Self evaluation -->
    <div class="sticky-note note-pink mb-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-hand text-base text-ink">自我评价</h3>
        <button
          v-if="desc.selfEvaluation"
          class="text-xs text-accent hover:underline cursor-pointer"
          @click="emit('ai-optimize', 'selfEvaluation')"
        >✨ AI 优化</button>
      </div>
      <textarea
        class="hand-input min-h-[120px]"
        placeholder="简要介绍自己的专业能力、性格特点、团队协作经验等..."
        :value="desc.selfEvaluation"
        @input="update({ selfEvaluation: ($event.target as HTMLTextAreaElement).value })"
      />
    </div>

    <!-- Career objective -->
    <div class="sticky-note note-blue mb-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-hand text-base text-ink">求职意向</h3>
        <button
          v-if="desc.careerObjective"
          class="text-xs text-accent hover:underline cursor-pointer"
          @click="emit('ai-optimize', 'careerObjective')"
        >✨ AI 优化</button>
      </div>
      <textarea
        class="hand-input min-h-[80px]"
        placeholder="期望的岗位方向、城市、薪资范围等..."
        :value="desc.careerObjective"
        @input="update({ careerObjective: ($event.target as HTMLTextAreaElement).value })"
      />
    </div>

    <!-- Personal summary -->
    <div class="sticky-note note-green">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-hand text-base text-ink">个人总结</h3>
        <button
          v-if="desc.personalSummary"
          class="text-xs text-accent hover:underline cursor-pointer"
          @click="emit('ai-optimize', 'personalSummary')"
        >✨ AI 优化</button>
      </div>
      <textarea
        class="hand-input min-h-[100px]"
        placeholder="综合总结你的核心竞争力、成长经历、未来规划..."
        :value="desc.personalSummary"
        @input="update({ personalSummary: ($event.target as HTMLTextAreaElement).value })"
      />
    </div>
  </div>
</template>
