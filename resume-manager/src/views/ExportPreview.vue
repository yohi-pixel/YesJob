<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResumeStore } from '@/stores/resume'
import { ArrowLeft, Download, Loader2, Palette } from 'lucide-vue-next'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const props = defineProps<{ id: string }>()

const router = useRouter()
const store = useResumeStore()
const exporting = ref(false)

type Template = 'hand-drawn' | 'clean-table'
const activeTemplate = ref<Template>('hand-drawn')

const templates: { key: Template; label: string; icon: string }[] = [
  { key: 'hand-drawn', label: '校园手绘风', icon: '🎨' },
  { key: 'clean-table', label: '简洁表格', icon: '📊' },
]

const resume = computed(() => store.resumes.find(r => r.id === props.id) ?? null)

const hasContent = computed(() => {
  if (!resume.value) return false
  const r = resume.value
  return !!(r.basicInfo.name || r.experiences.length || r.selfDescription.selfEvaluation)
})

onMounted(() => {
  if (!resume.value) router.replace('/')
})

function goBack() {
  router.push({ name: 'resume-edit', params: { id: props.id } })
}

async function exportPDF() {
  if (!resume.value || !hasContent.value) return
  exporting.value = true

  try {
    await nextTick()
    const el = document.getElementById('resume-preview-content')
    if (!el) throw new Error('Preview element not found')

    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth - 20
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let position = 10
    let remainingHeight = imgHeight

    // Multi-page support
    while (remainingHeight > 0) {
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight)
      remainingHeight -= (pageHeight - 20)
      if (remainingHeight > 0) {
        pdf.addPage()
        position = -(imgHeight - remainingHeight) + 10
      }
    }

    const filename = `${resume.value.title || '简历'}.pdf`
    pdf.save(filename)
  } catch (err: any) {
    alert('导出失败：' + (err.message || '未知错误'))
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div v-if="resume" class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-4">
      <button class="hand-btn text-xs" @click="goBack">
        <ArrowLeft :size="14" />
        <span>返回编辑</span>
      </button>
      <h1 class="section-title flex-1">导出预览</h1>
      <button
        class="hand-btn hand-btn-primary text-xs"
        :disabled="!hasContent || exporting"
        @click="exportPDF"
      >
        <Loader2 v-if="exporting" :size="14" class="animate-spin" />
        <Download v-else :size="14" />
        <span>{{ exporting ? '生成中...' : '下载 PDF' }}</span>
      </button>
    </div>

    <!-- Template selector -->
    <div class="flex items-center gap-2 mb-4">
      <Palette :size="16" class="text-pencil" />
      <span class="text-sm text-pencil-light mr-1">模板：</span>
      <button
        v-for="tpl in templates"
        :key="tpl.key"
        :class="[
          'hand-btn text-xs',
          activeTemplate === tpl.key ? 'hand-btn-primary' : '',
        ]"
        @click="activeTemplate = tpl.key"
      >
        <span>{{ tpl.icon }}</span>
        <span>{{ tpl.label }}</span>
      </button>
    </div>

    <!-- No content -->
    <div v-if="!hasContent" class="sticky-note note-blue p-8 text-center">
      <p class="font-hand text-lg text-ink-light">简历内容为空，请先填写信息再导出~</p>
    </div>

    <!-- Preview area -->
    <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div
        id="resume-preview-content"
        class="p-8 max-w-[210mm] mx-auto"
        :class="activeTemplate === 'hand-drawn' ? 'preview-hand-drawn' : 'preview-clean'"
      >
        <!-- ===== HAND-DRAWN TEMPLATE ===== -->
        <template v-if="activeTemplate === 'hand-drawn'">
          <!-- Name & Contact -->
          <div v-if="resume.basicInfo.name" class="text-center mb-6">
            <h1 style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 28px; color: #3e2723;">
              {{ resume.basicInfo.name }}
            </h1>
            <div style="font-size: 13px; color: #8d6e63; margin-top: 4px;">
              <span v-if="resume.basicInfo.phone">{{ resume.basicInfo.phone }}</span>
              <span v-if="resume.basicInfo.phone && resume.basicInfo.email"> · </span>
              <span v-if="resume.basicInfo.email">{{ resume.basicInfo.email }}</span>
            </div>
          </div>

          <!-- School -->
          <div v-if="resume.basicInfo.school" style="text-align: center; margin-bottom: 20px; font-size: 14px; color: #5d4037;">
            {{ resume.basicInfo.school }}
            <span v-if="resume.basicInfo.major"> · {{ resume.basicInfo.major }}</span>
            <span v-if="resume.basicInfo.degree"> · {{ resume.basicInfo.degree }}</span>
            <span v-if="resume.basicInfo.grade"> · {{ resume.basicInfo.grade }}</span>
          </div>

          <!-- GPA -->
          <div v-if="resume.basicInfo.gpa || resume.basicInfo.rank" style="text-align: center; margin-bottom: 16px; font-size: 12px; color: #8d6e63;">
            <span v-if="resume.basicInfo.gpa">GPA: {{ resume.basicInfo.gpa }}</span>
            <span v-if="resume.basicInfo.gpa && resume.basicInfo.rank"> | </span>
            <span v-if="resume.basicInfo.rank">排名: {{ resume.basicInfo.rank }}</span>
          </div>

          <!-- Courses -->
          <div v-if="resume.basicInfo.courses.length" style="margin-bottom: 16px;">
            <div style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 16px; color: #5c6bc0; border-bottom: 2px dashed #bcaaa4; padding-bottom: 4px; margin-bottom: 6px;">
              📚 相关课程
            </div>
            <div style="font-size: 12px; color: #5d4037; line-height: 1.8;">
              {{ resume.basicInfo.courses.join('、') }}
            </div>
          </div>

          <!-- Skills -->
          <div v-if="resume.basicInfo.skills.length" style="margin-bottom: 16px;">
            <div style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 16px; color: #5c6bc0; border-bottom: 2px dashed #bcaaa4; padding-bottom: 4px; margin-bottom: 6px;">
              🛠️ 技能与掌握程度
            </div>
            <div style="font-size: 12px; color: #5d4037; line-height: 1.8;">
              <span v-for="(skill, i) in resume.basicInfo.skills" :key="i">
                {{ skill.name }}<span style="color: #8d6e63;">（{{ skill.level }}）</span><span v-if="i < resume.basicInfo.skills.length - 1">、</span>
              </span>
            </div>
          </div>

          <!-- Awards -->
          <div v-if="resume.basicInfo.awards.length" style="margin-bottom: 16px;">
            <div style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 16px; color: #5c6bc0; border-bottom: 2px dashed #bcaaa4; padding-bottom: 4px; margin-bottom: 6px;">
              🏆 获奖与比赛
            </div>
            <div v-for="(award, i) in resume.basicInfo.awards" :key="i" style="font-size: 12px; color: #5d4037; line-height: 1.8;">
              {{ award.name }}
              <span v-if="award.level" style="color: #ff8a65;">（{{ award.level }}）</span>
              <span v-if="award.date" style="color: #8d6e63;"> {{ award.date }}</span>
            </div>
          </div>

          <!-- Experiences -->
          <div v-if="resume.experiences.length" style="margin-bottom: 16px;">
            <div style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 16px; color: #5c6bc0; border-bottom: 2px dashed #bcaaa4; padding-bottom: 4px; margin-bottom: 8px;">
              💼 经历与项目
            </div>
            <div v-for="(exp, i) in resume.experiences" :key="exp.id" style="margin-bottom: 12px; padding: 8px; background: #fdf6e3; border-radius: 8px; border-left: 3px solid #5c6bc0;">
              <div style="font-size: 14px; font-weight: bold; color: #3e2723;">{{ exp.title }}</div>
              <div style="font-size: 12px; color: #8d6e63; margin-top: 2px;">
                {{ exp.role }}<span v-if="exp.organization"> · {{ exp.organization }}</span>
                <span v-if="exp.period"> · {{ exp.period }}</span>
              </div>
              <div v-if="exp.techStack.length" style="font-size: 11px; color: #5c6bc0; margin-top: 4px;">
                {{ exp.techStack.join(' · ') }}
              </div>
              <div style="font-size: 12px; color: #5d4037; margin-top: 6px; white-space: pre-line; line-height: 1.6;">{{ exp.description }}</div>
            </div>
          </div>

          <!-- Self description -->
          <div v-if="resume.selfDescription.selfEvaluation || resume.selfDescription.careerObjective || resume.selfDescription.personalSummary">
            <div style="font-family: 'ZCOOL KuaiLe', cursive; font-size: 16px; color: #5c6bc0; border-bottom: 2px dashed #bcaaa4; padding-bottom: 4px; margin-bottom: 8px;">
              ✏️ 自我描述
            </div>
            <div v-if="resume.selfDescription.careerObjective" style="font-size: 12px; color: #5d4037; margin-bottom: 6px;">
              <strong style="color: #3e2723;">求职意向：</strong>{{ resume.selfDescription.careerObjective }}
            </div>
            <div v-if="resume.selfDescription.selfEvaluation" style="font-size: 12px; color: #5d4037; margin-bottom: 6px; white-space: pre-line; line-height: 1.6;">
              <strong style="color: #3e2723;">自我评价：</strong>{{ resume.selfDescription.selfEvaluation }}
            </div>
            <div v-if="resume.selfDescription.personalSummary" style="font-size: 12px; color: #5d4037; white-space: pre-line; line-height: 1.6;">
              <strong style="color: #3e2723;">个人总结：</strong>{{ resume.selfDescription.personalSummary }}
            </div>
          </div>
        </template>

        <!-- ===== CLEAN TABLE TEMPLATE ===== -->
        <template v-else>
          <!-- Header bar -->
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #3949ab; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
              <h1 style="font-size: 26px; font-weight: bold; color: #1a1a2e;">{{ resume.basicInfo.name || '未命名' }}</h1>
            </div>
            <div style="font-size: 12px; color: #666; text-align: right; line-height: 1.6;">
              <div v-if="resume.basicInfo.phone">{{ resume.basicInfo.phone }}</div>
              <div v-if="resume.basicInfo.email">{{ resume.basicInfo.email }}</div>
            </div>
          </div>

          <!-- Education row -->
          <table v-if="resume.basicInfo.school" style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
            <tr>
              <td style="font-size: 13px; font-weight: bold; color: #3949ab; padding: 4px 8px; border: 1px solid #e0e0e0; background: #f5f5f5; width: 80px;">教育背景</td>
              <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0;">
                {{ resume.basicInfo.school }}
                <span v-if="resume.basicInfo.major"> · {{ resume.basicInfo.major }}</span>
                <span v-if="resume.basicInfo.degree"> · {{ resume.basicInfo.degree }}</span>
                <span v-if="resume.basicInfo.grade"> · {{ resume.basicInfo.grade }}</span>
                <span v-if="resume.basicInfo.gpa" style="color: #888;"> | GPA: {{ resume.basicInfo.gpa }}</span>
                <span v-if="resume.basicInfo.rank" style="color: #888;"> | {{ resume.basicInfo.rank }}</span>
              </td>
            </tr>
          </table>

          <!-- Skills table -->
          <table v-if="resume.basicInfo.skills.length" style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
            <tr>
              <td style="font-size: 13px; font-weight: bold; color: #3949ab; padding: 4px 8px; border: 1px solid #e0e0e0; background: #f5f5f5; width: 80px;">专业技能</td>
              <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; line-height: 1.8;">
                <span v-for="(skill, i) in resume.basicInfo.skills" :key="i">
                  {{ skill.name }}（{{ skill.level }}）<span v-if="i < resume.basicInfo.skills.length - 1">、</span>
                </span>
              </td>
            </tr>
          </table>

          <!-- Courses -->
          <table v-if="resume.basicInfo.courses.length" style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
            <tr>
              <td style="font-size: 13px; font-weight: bold; color: #3949ab; padding: 4px 8px; border: 1px solid #e0e0e0; background: #f5f5f5; width: 80px;">相关课程</td>
              <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0;">{{ resume.basicInfo.courses.join('、') }}</td>
            </tr>
          </table>

          <!-- Awards -->
          <table v-if="resume.basicInfo.awards.length" style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
            <tr>
              <td style="font-size: 13px; font-weight: bold; color: #3949ab; padding: 4px 8px; border: 1px solid #e0e0e0; background: #f5f5f5; width: 80px;">获奖经历</td>
              <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0;">
                <div v-for="(award, i) in resume.basicInfo.awards" :key="i" style="line-height: 1.8;">
                  {{ award.name }}<span v-if="award.level" style="color: #888;">（{{ award.level }}）</span><span v-if="award.date"> {{ award.date }}</span>
                </div>
              </td>
            </tr>
          </table>

          <!-- Experiences -->
          <div v-if="resume.experiences.length" style="margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: bold; color: #3949ab; border-left: 4px solid #3949ab; padding-left: 8px; margin-bottom: 8px;">项目 / 实习经历</div>
            <div v-for="exp in resume.experiences" :key="exp.id" style="margin-bottom: 10px; padding-left: 12px; border-left: 2px solid #e0e0e0;">
              <div style="display: flex; justify-content: space-between;">
                <div>
                  <span style="font-size: 13px; font-weight: bold; color: #333;">{{ exp.title }}</span>
                  <span v-if="exp.role" style="font-size: 12px; color: #666;"> - {{ exp.role }}</span>
                  <span v-if="exp.organization" style="font-size: 12px; color: #888;"> | {{ exp.organization }}</span>
                </div>
                <span v-if="exp.period" style="font-size: 12px; color: #888;">{{ exp.period }}</span>
              </div>
              <div v-if="exp.techStack.length" style="font-size: 11px; color: #3949ab; margin-top: 2px;">{{ exp.techStack.join(' · ') }}</div>
              <div style="font-size: 12px; color: #555; margin-top: 4px; white-space: pre-line; line-height: 1.6;">{{ exp.description }}</div>
            </div>
          </div>

          <!-- Self description -->
          <div v-if="resume.selfDescription.careerObjective || resume.selfDescription.selfEvaluation || resume.selfDescription.personalSummary">
            <div style="font-size: 14px; font-weight: bold; color: #3949ab; border-left: 4px solid #3949ab; padding-left: 8px; margin-bottom: 8px;">自我描述</div>
            <table style="width: 100%; border-collapse: collapse;">
              <tr v-if="resume.selfDescription.careerObjective">
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; background: #fafafa; width: 70px;">求职意向</td>
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0;">{{ resume.selfDescription.careerObjective }}</td>
              </tr>
              <tr v-if="resume.selfDescription.selfEvaluation">
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; background: #fafafa;">自我评价</td>
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; white-space: pre-line; line-height: 1.6;">{{ resume.selfDescription.selfEvaluation }}</td>
              </tr>
              <tr v-if="resume.selfDescription.personalSummary">
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; background: #fafafa;">个人总结</td>
                <td style="font-size: 13px; color: #333; padding: 4px 8px; border: 1px solid #e0e0e0; white-space: pre-line; line-height: 1.6;">{{ resume.selfDescription.personalSummary }}</td>
              </tr>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
