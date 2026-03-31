<script setup lang="ts">
import { ref, watch } from 'vue'
import { useResumeStore } from '@/stores/resume'
import { Plus, X, Save } from 'lucide-vue-next'
import type { BasicInfo } from '@/types'

const store = useResumeStore()

// Local state for basic info - will sync to all resumes
const localInfo = ref<BasicInfo>({
  name: '',
  phone: '',
  email: '',
  school: '',
  degree: '',
  major: '',
  grade: '',
  gpa: '',
  rank: '',
  courses: [],
  skills: [],
  awards: [],
})

// Load from first resume if exists
function loadFromResume() {
  if (store.resumes.length > 0) {
    const first = store.resumes[0].basicInfo
    localInfo.value = { ...first }
  }
}

loadFromResume()

function update(field: keyof BasicInfo, value: any) {
  (localInfo.value as any)[field] = value
}

function updateCourses(value: string) {
  localInfo.value.courses = value.split('\n').map(s => s.trim()).filter(Boolean)
}

function addSkill() {
  localInfo.value.skills.push({ name: '', level: '熟悉' })
}

function removeSkill(index: number) {
  localInfo.value.skills.splice(index, 1)
}

function updateSkill(index: number, field: 'name' | 'level', value: string) {
  localInfo.value.skills[index][field] = value
}

function addAward() {
  localInfo.value.awards.push({ name: '', level: '校级', date: '' })
}

function removeAward(index: number) {
  localInfo.value.awards.splice(index, 1)
}

function updateAward(index: number, field: 'name' | 'level' | 'date', value: string) {
  localInfo.value.awards[index][field] = value
}

// Apply to all resumes
function applyToAllResumes() {
  if (store.resumes.length === 0) {
    alert('请先创建一份简历')
    return
  }
  
  if (confirm(`确定将基本信息应用到所有 ${store.resumes.length} 份简历吗？`)) {
    for (const resume of store.resumes) {
      store.updateBasicInfo(resume.id, { ...localInfo.value })
    }
    alert('已应用到所有简历')
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="section-title">基本信息</h1>
        <p class="text-sm text-gray-500 mt-1">统一管理你的基本信息，一键应用到所有简历</p>
      </div>
      <button 
        class="hand-btn hand-btn-primary flex items-center gap-2"
        :disabled="store.resumes.length === 0"
        @click="applyToAllResumes"
      >
        <Save :size="16" />
        <span>应用到全部简历</span>
      </button>
    </div>

    <!-- No resumes yet -->
    <div v-if="store.resumes.length === 0" class="card p-8 text-center">
      <p class="text-gray-500 mb-4">请先在「我的简历」中创建一份简历</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Core info -->
      <div class="card p-5">
        <h3 class="font-medium text-gray-900 mb-4">基本信息</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">姓名 *</label>
            <input 
              class="hand-input" 
              placeholder="你的姓名" 
              :value="localInfo.name"
              @input="update('name', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">手机号</label>
            <input 
              class="hand-input" 
              placeholder="138xxxxxxxx" 
              :value="localInfo.phone"
              @input="update('phone', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">邮箱</label>
            <input 
              class="hand-input" 
              placeholder="xx@xx.com" 
              :value="localInfo.email"
              @input="update('email', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">学校</label>
            <input 
              class="hand-input" 
              placeholder="XX大学" 
              :value="localInfo.school"
              @input="update('school', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">学历</label>
            <select 
              class="hand-input"
              :value="localInfo.degree"
              @change="update('degree', ($event.target as HTMLSelectElement).value)"
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
              :value="localInfo.major"
              @input="update('major', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">年级</label>
            <input 
              class="hand-input" 
              placeholder="2025届 / 大三" 
              :value="localInfo.grade"
              @input="update('grade', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">GPA</label>
            <input 
              class="hand-input" 
              placeholder="3.8/4.0" 
              :value="localInfo.gpa"
              @input="update('gpa', ($event.target as HTMLInputElement).value)" 
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 font-medium mb-1.5 block">排名</label>
            <input 
              class="hand-input" 
              placeholder="5/100" 
              :value="localInfo.rank"
              @input="update('rank', ($event.target as HTMLInputElement).value)" 
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
          :value="localInfo.courses.join('\n')"
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
        <div v-if="localInfo.skills.length === 0" class="text-sm text-gray-400 py-2">
          点击添加技能
        </div>
        <div v-else class="space-y-2">
          <div v-for="(skill, idx) in localInfo.skills" :key="idx" class="flex gap-2 items-center">
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
        <div v-if="localInfo.awards.length === 0" class="text-sm text-gray-400 py-2">
          点击添加获奖经历
        </div>
        <div v-else class="space-y-2">
          <div v-for="(award, idx) in localInfo.awards" :key="idx" class="flex gap-2 items-center">
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
  </div>
</template>
