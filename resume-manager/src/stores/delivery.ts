import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DeliveryRecord } from '@/types'

const STORAGE_KEY = 'resume-manager-deliveries'

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

export const useDeliveryStore = defineStore('delivery', () => {
  const records = ref<DeliveryRecord[]>(loadFromStorage())

  function addRecord(data: Omit<DeliveryRecord, 'id' | 'createdAt'>) {
    records.value.unshift({
      ...data,
      id: generateId(),
      createdAt: new Date().toISOString(),
    })
    persist()
  }

  function updateRecord(id: string, patch: Partial<DeliveryRecord>) {
    const idx = records.value.findIndex(r => r.id === id)
    if (idx >= 0) {
      Object.assign(records.value[idx], patch)
      persist()
    }
  }

  function deleteRecord(id: string) {
    records.value = records.value.filter(r => r.id !== id)
    persist()
  }

  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(records.value))
    } catch {
      // storage full
    }
  }

  function loadFromStorage(): DeliveryRecord[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  }

  return { records, addRecord, updateRecord, deleteRecord }
})
