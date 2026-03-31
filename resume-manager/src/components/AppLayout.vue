<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  FileText,
  BookOpen,
  Send,
  Menu,
  X,
  GraduationCap,
  User,
  Layers,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const sidebarOpen = ref(true)

const navItems = [
  { icon: FileText, label: '我的简历', route: '/' },
  { icon: Layers, label: '简历组装', route: '/resume/assemble' },
  { icon: User, label: '基本信息', route: '/basic-info' },
  { icon: BookOpen, label: '经历库', route: '/experience-library' },
  { icon: Send, label: '投递管理', route: '/delivery' },
]

function navigateTo(path: string) {
  router.push(path)
}

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/20 z-20 md:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed md:relative z-30 h-full flex flex-col transition-all duration-300',
        'bg-white border-r border-gray-200',
        sidebarOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full md:translate-x-0 md:w-0',
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center gap-2 px-5 py-5 border-b border-gray-100">
        <GraduationCap :size="28" class="text-indigo-500" />
        <span class="font-medium text-lg text-gray-900">简历管理</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 px-3 space-y-1">
        <button
          v-for="item in navItems"
          :key="item.route"
          :class="['sidebar-link w-full', isActive(item.route) && 'active']"
          @click="navigateTo(item.route)"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <!-- Footer -->
      <div class="px-5 py-4 border-t border-gray-100">
        <p class="text-xs text-gray-400">Resume Manager v1.0</p>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top bar -->
      <header class="flex items-center h-14 px-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
        <button
          class="p-2 md:hidden hover:bg-gray-100 rounded-lg transition-colors"
          @click="sidebarOpen = !sidebarOpen"
        >
          <component :is="sidebarOpen ? X : Menu" :size="20" />
        </button>
        <div class="flex-1" />
        <span class="text-sm text-gray-400 hidden sm:block">
          记录你的每一份成长
        </span>
      </header>

      <!-- Content -->
      <main class="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50">
        <router-view />
      </main>
    </div>
  </div>
</template>
