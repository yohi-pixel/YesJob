import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'resumes',
      component: () => import('@/views/ResumeList.vue'),
    },
    {
      path: '/basic-info',
      name: 'basic-info',
      component: () => import('@/views/BasicInfo.vue'),
    },
    {
      path: '/resume/assemble',
      name: 'resume-assemble',
      component: () => import('@/views/ResumeAssemble.vue'),
    },
    {
      path: '/resume/edit/:id',
      name: 'resume-edit',
      component: () => import('@/views/ResumeEdit.vue'),
      props: true,
    },
    {
      path: '/resume/export/:id',
      name: 'resume-export',
      component: () => import('@/views/ExportPreview.vue'),
      props: true,
    },
    {
      path: '/experience-library',
      name: 'experience-library',
      component: () => import('@/views/ExperienceLibrary.vue'),
    },
    {
      path: '/delivery',
      name: 'delivery',
      component: () => import('@/views/DeliveryManagement.vue'),
    },
  ],
})

export default router
