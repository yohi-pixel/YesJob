<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDeliveryStore } from '@/stores/delivery'
import { useResumeStore } from '@/stores/resume'
import {
  Plus,
  Search,
  Trash2,
  Edit3,
  ExternalLink,
  X,
  Save,
  FileText,
} from 'lucide-vue-next'

const deliveryStore = useDeliveryStore()
const resumeStore = useResumeStore()

const searchQuery = ref('')
const showForm = ref(false)
const editingId = ref<string | null>(null)

// Form fields
const formCompany = ref('')
const formPosition = ref('')
const formLink = ref('')
const formDate = ref(new Date().toISOString().slice(0, 10))
const formResumeId = ref('')
const formNote = ref('')

const filteredRecords = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return deliveryStore.records
  return deliveryStore.records.filter(
    r =>
      r.company.toLowerCase().includes(q) ||
      r.position.toLowerCase().includes(q) ||
      r.note.toLowerCase().includes(q)
  )
})

function openCreate() {
  editingId.value = null
  formCompany.value = ''
  formPosition.value = ''
  formLink.value = ''
  formDate.value = new Date().toISOString().slice(0, 10)
  formResumeId.value = resumeStore.currentResumeId || ''
  formNote.value = ''
  showForm.value = true
}

function openEdit(record: any) {
  editingId.value = record.id
  formCompany.value = record.company
  formPosition.value = record.position
  formLink.value = record.link
  formDate.value = record.date
  formResumeId.value = record.resumeId
  formNote.value = record.note
  showForm.value = true
}

function handleSave() {
  if (!formCompany.value.trim() || !formPosition.value.trim()) {
    alert('请至少填写公司和岗位')
    return
  }

  if (editingId.value) {
    deliveryStore.updateRecord(editingId.value, {
      company: formCompany.value.trim(),
      position: formPosition.value.trim(),
      link: formLink.value.trim(),
      date: formDate.value,
      resumeId: formResumeId.value,
      note: formNote.value.trim(),
    })
  } else {
    deliveryStore.addRecord({
      company: formCompany.value.trim(),
      position: formPosition.value.trim(),
      link: formLink.value.trim(),
      date: formDate.value,
      resumeId: formResumeId.value,
      note: formNote.value.trim(),
    })
  }

  showForm.value = false
}

function handleDelete(id: string) {
  if (confirm('确定删除这条投递记录吗？')) {
    deliveryStore.deleteRecord(id)
  }
}

function getResumeTitle(id: string) {
  const r = resumeStore.resumes.find(r => r.id === id)
  return r?.title || '未关联'
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="section-title">投递管理</h1>
      <button class="hand-btn hand-btn-primary text-xs" @click="openCreate">
        <Plus :size="14" />
        <span>新增投递</span>
      </button>
    </div>

    <!-- Search -->
    <div class="relative mb-4">
      <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-pencil-light" />
      <input
        v-model="searchQuery"
        class="hand-input pl-9"
        placeholder="搜索公司、岗位、备注..."
      />
    </div>

    <!-- Stats bar -->
    <div class="sticky-note note-yellow mb-4 p-3">
      <span class="font-hand text-sm text-ink">
        共 {{ deliveryStore.records.length }} 条投递记录
      </span>
    </div>

    <!-- Empty state -->
    <div v-if="deliveryStore.records.length === 0" class="text-center py-16">
      <div class="inline-block sticky-note note-pink p-8 max-w-md">
        <FileText :size="48" class="mx-auto mb-4 text-accent opacity-40" />
        <p class="font-hand text-lg text-ink-light">还没有投递记录~</p>
        <p class="text-sm text-pencil mt-1">点击「新增投递」开始记录</p>
      </div>
    </div>

    <!-- Records list -->
    <div v-else class="space-y-3">
      <div
        v-for="(record, idx) in filteredRecords"
        :key="record.id"
        class="sticky-note"
        :class="idx % 2 === 0 ? 'note-yellow' : 'note-blue'"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <!-- Company & Position -->
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-hand text-base text-ink truncate">{{ record.company }}</h3>
              <span class="tag text-xs shrink-0">{{ record.position }}</span>
            </div>

            <!-- Meta -->
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-pencil-light mb-1">
              <span v-if="record.date">📅 {{ record.date }}</span>
              <span>📄 {{ getResumeTitle(record.resumeId) }}</span>
            </div>

            <!-- Link -->
            <a
              v-if="record.link"
              :href="record.link"
              target="_blank"
              class="text-xs text-accent hover:underline inline-flex items-center gap-1"
            >
              <ExternalLink :size="10" />
              {{ record.link }}
            </a>

            <!-- Note -->
            <p v-if="record.note" class="text-sm text-ink-light mt-1">{{ record.note }}</p>
          </div>

          <!-- Actions -->
          <div class="flex gap-1 shrink-0 ml-2">
            <button
              class="p-1 hover:bg-white/60 rounded transition-colors"
              @click="openEdit(record)"
            >
              <Edit3 :size="14" class="text-accent" />
            </button>
            <button
              class="p-1 hover:bg-red-100 rounded transition-colors"
              @click="handleDelete(record.id)"
            >
              <Trash2 :size="14" class="text-red-400" />
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredRecords.length === 0 && searchQuery" class="text-center py-8">
        <p class="font-hand text-sm text-pencil-light">没有找到匹配的记录 😅</p>
      </div>
    </div>

    <!-- Form modal -->
    <div v-if="showForm" class="fixed inset-0 bg-paper/80 flex items-center justify-center z-50 p-4">
      <div class="sticky-note note-yellow w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-hand text-lg text-ink">{{ editingId ? '编辑投递' : '新增投递' }}</h3>
          <button class="p-1 hover:bg-white/60 rounded" @click="showForm = false">
            <X :size="16" class="text-pencil" />
          </button>
        </div>

        <div class="space-y-3">
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">公司名称 *</label>
            <input v-model="formCompany" class="hand-input" placeholder="如：字节跳动" />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">岗位名称 *</label>
            <input v-model="formPosition" class="hand-input" placeholder="如：后端开发工程师" />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">投递链接</label>
            <input v-model="formLink" class="hand-input" placeholder="https://..." />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">投递日期</label>
            <input v-model="formDate" type="date" class="hand-input" />
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">关联简历</label>
            <select v-model="formResumeId" class="hand-input">
              <option value="">不关联</option>
              <option v-for="r in resumeStore.resumes" :key="r.id" :value="r.id">
                {{ r.title }}
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs text-pencil font-medium mb-1 block">备注</label>
            <textarea v-model="formNote" class="hand-input min-h-[60px]" placeholder="如：内推、笔试时间等" />
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <button class="hand-btn text-xs flex-1" @click="showForm = false">取消</button>
          <button class="hand-btn hand-btn-primary text-xs flex-1" @click="handleSave">
            <Save :size="14" />
            <span>保存</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
