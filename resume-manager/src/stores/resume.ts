import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Resume, BasicInfo, ExperienceItem, SelfDescription, SkillItem, AwardItem } from '@/types'

const STORAGE_KEY = 'resume-manager-resumes'

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function emptyBasicInfo(): BasicInfo {
  return {
    name: '', phone: '', email: '',
    school: '', degree: '', major: '', grade: '',
    gpa: '', rank: '',
    courses: [], skills: [], awards: [],
  }
}

function emptySelfDescription(): SelfDescription {
  return { selfEvaluation: '', careerObjective: '', personalSummary: '', tags: [] }
}

export const useResumeStore = defineStore('resume', () => {
  // ── State ──────────────────────────────────────────
  const resumes = ref<Resume[]>(loadFromStorage())
  const currentResumeId = ref<string>('')

  // ── Getters ────────────────────────────────────────
  const currentResume = computed(() =>
    resumes.value.find(r => r.id === currentResumeId.value) ?? null
  )

  const allExperiences = computed(() => {
    const items: ExperienceItem[] = []
    for (const r of resumes.value) {
      for (const exp of r.experiences) {
        items.push(exp)
      }
    }
    return items
  })

  // ── Actions ────────────────────────────────────────
  function createResume(title?: string): Resume {
    const resume: Resume = {
      id: generateId(),
      title: title || '未命名简历',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      basicInfo: emptyBasicInfo(),
      experiences: [],
      selfDescription: emptySelfDescription(),
    }
    resumes.value.unshift(resume)
    persist()
    return resume
  }

  function updateResume(id: string, patch: Partial<Resume>) {
    const idx = resumes.value.findIndex(r => r.id === id)
    if (idx >= 0) {
      Object.assign(resumes.value[idx], patch, { updatedAt: new Date().toISOString() })
      persist()
    }
  }

  function deleteResume(id: string) {
    resumes.value = resumes.value.filter(r => r.id !== id)
    if (currentResumeId.value === id) currentResumeId.value = ''
    persist()
  }

  function duplicateResume(id: string): Resume | null {
    const src = resumes.value.find(r => r.id === id)
    if (!src) return null
    const copy: Resume = {
      ...JSON.parse(JSON.stringify(src)),
      id: generateId(),
      title: src.title + ' (副本)',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    resumes.value.unshift(copy)
    persist()
    return copy
  }

  // Experience helpers
  function addExperience(resumeId: string, item?: ExperienceItem) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.experiences.push(item || {
      id: generateId(),
      title: '', role: '', organization: '', period: '',
      techStack: [], description: '', tags: [],
    })
    persist()
  }

  function updateExperience(resumeId: string, expId: string, patch: Partial<ExperienceItem>) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    const exp = resume.experiences.find(e => e.id === expId)
    if (exp) Object.assign(exp, patch)
    persist()
  }

  function removeExperience(resumeId: string, expId: string) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.experiences = resume.experiences.filter(e => e.id !== expId)
    persist()
  }

  // Self-description helper
  function updateSelfDescription(resumeId: string, patch: Partial<SelfDescription>) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    Object.assign(resume.selfDescription, patch)
    persist()
  }

  // BasicInfo helpers
  function updateBasicInfo(resumeId: string, patch: Partial<BasicInfo>) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    Object.assign(resume.basicInfo, patch)
    persist()
  }

  // Skill / award helpers
  function addSkill(resumeId: string, skill?: SkillItem) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.basicInfo.skills.push(skill || { name: '', level: '熟练' })
    persist()
  }
  function removeSkill(resumeId: string, index: number) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.basicInfo.skills.splice(index, 1)
    persist()
  }

  function addAward(resumeId: string, award?: AwardItem) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.basicInfo.awards.push(award || { name: '', level: '校级', date: '' })
    persist()
  }
  function removeAward(resumeId: string, index: number) {
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) return
    resume.basicInfo.awards.splice(index, 1)
    persist()
  }

  function setCurrent(id: string) {
    currentResumeId.value = id
  }

  // ── Persistence ───────────────────────────────────
  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(resumes.value))
    } catch {
      // storage full or unavailable
    }
  }

  function loadFromStorage(): Resume[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  }

  return {
    resumes, currentResumeId, currentResume, allExperiences,
    createResume, updateResume, deleteResume, duplicateResume, setCurrent,
    addExperience, updateExperience, removeExperience,
    updateSelfDescription,
    updateBasicInfo,
    addSkill, removeSkill, addAward, removeAward,
  }
})
