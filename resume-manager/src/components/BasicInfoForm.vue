<script setup lang="ts">
import { Plus, X } from 'lucide-vue-next'
import type { BasicInfo } from '@/types'
import { useResumeStore } from '@/stores/resume'

const props = defineProps<{
  resumeId: string
  basicInfo: BasicInfo
}>()

const store = useResumeStore()

function update(patch: Partial<BasicInfo>) {
  store.updateBasicInfo(props.resumeId, patch)
}

function updateCourses(value: string) {
  update({ courses: value.split('\n').map(s => s.trim()).filter(Boolean) })
}

function addSkill() {
  store.addSkill(props.resumeId)
}

function removeSkill(index: number) {
  store.removeSkill(props.resumeId, index)
}

function updateSkill(index: number, field: 'name' | 'level', value: string) {
  const skills = [...props.basicInfo.skills]
  skills[index] = { ...skills[index], [field]: value }
  update({ skills })
}

function addAward() {
  store.addAward(props.resumeId)
}

function removeAward(index: number) {
  store.removeAward(props.resumeId, index)
}

function updateAward(index: number, field: 'name' | 'level' | 'date', value: string) {
  const awards = [...props.basicInfo.awards]
  awards[index] = { ...awards[index], [field]: value }
  update({ awards })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Core info -->
    <div class="card p-5">
      <h3 class="font-medium text-gray-900 mb-4">基本信息</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">姓名 *</label>
          <input 
            class="hand-input" 
            placeholder="你的姓名" 
            :value="basicInfo.name"
            @input="update({ name: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">手机号</label>
          <input 
            class="hand-input" 
            placeholder="138xxxxxxxx" 
            :value="basicInfo.phone"
            @input="update({ phone: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">邮箱</label>
          <input 
            class="hand-input" 
            placeholder="xx@xx.com" 
            :value="basicInfo.email"
            @input="update({ email: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">学校</label>
          <input 
            class="hand-input" 
            placeholder="XX大学" 
            :value="basicInfo.school"
            @input="update({ school: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">学历</label>
          <select 
            class="hand-input"
            :value="basicInfo.degree"
            @change="update({ degree: ($event.target as HTMLSelectElement).value })"
          >
            <option value="">请选择</option>
            <option>大专</option>
            <option>本科</option>
            <option>硕士</option>
            <option>博士</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">专业</label>
          <input 
            class="hand-input" 
            placeholder="计算机科学与技术" 
            :value="basicInfo.major"
            @input="update({ major: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">年级</label>
          <input 
            class="hand-input" 
            placeholder="2025届 / 大三" 
            :value="basicInfo.grade"
            @input="update({ grade: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">GPA</label>
          <input 
            class="hand-input" 
            placeholder="3.8/4.0" 
            :value="basicInfo.gpa"
            @input="update({ gpa: ($event.target as HTMLInputElement).value })" 
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 font-medium mb-1.5 block">排名</label>
          <input 
            class="hand-input" 
            placeholder="5/100" 
            :value="basicInfo.rank"
            @input="update({ rank: ($event.target as HTMLInputElement).value })" 
          />
        </div>
      </div>
    </div>

    <!-- Courses -->
    <div class="card p-5">
      <h3 class="font-medium text-gray-900 mb-3">主要课程</h3>
      <textarea 
        class="hand-textarea" 
        placeholder="每行一个课程，如：数据结构、算法导论"
        :value="basicInfo.courses.join('\n')"
        @input="updateCourses(($event.target as HTMLTextAreaElement).value)"
      />
    </div>

    <!-- Skills -->
    <div class="card p-5">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-medium text-gray-900">技能特长</h3>
        <button class="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1" @click="addSkill">
          <Plus :size="14" /> 添加
        </button>
      </div>
      <div v-if="basicInfo.skills.length === 0" class="text-sm text-gray-400 py-2">
        点击添加技能
      </div>
      <div v-else class="space-y-2">
        <div v-for="(skill, idx) in basicInfo.skills" :key="idx" class="flex gap-2 items-center">
          <input 
            class="hand-input flex-1" 
            placeholder="技能名称" 
            :value="skill.name"
            @input="updateSkill(idx, 'name', ($event.target as HTMLInputElement).value)"
          />
          <select 
            class="hand-input w-24"
            :value="skill.level"
            @change="updateSkill(idx, 'level', ($event.target as HTMLSelectElement).value)"
          >
            <option>了解</option>
            <option>熟悉</option>
            <option>熟练</option>
            <option>精通</option>
          </select>
          <button class="p-2 text-gray-400 hover:text-red-500" @click="removeSkill(idx)">
            <X :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Awards -->
    <div class="card p-5">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-medium text-gray-900">获奖荣誉</h3>
        <button class="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1" @click="addAward">
          <Plus :size="14" /> 添加
        </button>
      </div>
      <div v-if="basicInfo.awards.length === 0" class="text-sm text-gray-400 py-2">
        点击添加获奖经历
      </div>
      <div v-else class="space-y-2">
        <div v-for="(award, idx) in basicInfo.awards" :key="idx" class="flex gap-2 items-center">
          <input 
            class="hand-input flex-1" 
            placeholder="奖项名称" 
            :value="award.name"
            @input="updateAward(idx, 'name', ($event.target as HTMLInputElement).value)"
          />
          <select 
            class="hand-input w-20"
            :value="award.level"
            @change="updateAward(idx, 'level', ($event.target as HTMLSelectElement).value)"
          >
            <option>校级</option>
            <option>省级</option>
            <option>国家级</option>
          </select>
          <input 
            class="hand-input w-28" 
            placeholder="获奖日期" 
            :value="award.date"
            @input="updateAward(idx, 'date', ($event.target as HTMLInputElement).value)"
          />
          <button class="p-2 text-gray-400 hover:text-red-500" @click="removeAward(idx)">
            <X :size="16" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
