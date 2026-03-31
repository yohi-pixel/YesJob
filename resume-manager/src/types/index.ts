// ── Resume data types ──────────────────────────────────

export interface SkillItem {
  name: string
  level: string  // e.g. "精通", "熟练", "了解"
}

export interface AwardItem {
  name: string
  level: string  // e.g. "国家级", "省级", "校级"
  date: string
}

export interface BasicInfo {
  name: string
  phone: string
  email: string
  school: string
  degree: string
  major: string
  grade: string
  gpa: string
  rank: string
  courses: string[]
  skills: SkillItem[]
  awards: AwardItem[]
}

export interface ExperienceItem {
  id: string
  title: string
  role: string
  organization: string
  period: string
  techStack: string[]
  description: string
  tags: string[]  // job-position tags
}

export interface SelfDescription {
  selfEvaluation: string
  careerObjective: string
  personalSummary: string
  tags: string[]  // job-position tags
}

export interface Resume {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  basicInfo: BasicInfo
  experiences: ExperienceItem[]
  selfDescription: SelfDescription
}

// ── Delivery management ────────────────────────────────

export interface DeliveryRecord {
  id: string
  company: string
  position: string
  link: string
  date: string
  resumeId: string
  note: string
  createdAt: string
}

// ── API types ──────────────────────────────────────────

export interface ParseResumeResponse {
  experiences: ParseExperienceItem[]
  self_description: ParseSelfDescription
  parse_method: string
  raw_sections: Record<string, string>
}

export interface ParseExperienceItem {
  title: string
  role: string
  organization: string
  period: string
  tech_stack: string[]
  description: string
  tags: string[]
}

export interface ParseSelfDescription {
  self_evaluation: string
  career_objective: string
  personal_summary: string
  tags: string[]
}

export interface OptimizeRequest {
  content: string
  target_tag: string
  section_type: 'experience' | 'self_description'
}

export interface OptimizeResponse {
  optimized_content: string
  original_content: string
  target_tag: string
}
