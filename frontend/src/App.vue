<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <!-- 未登录：登录/注册页 -->
    <div v-if="!store.isLoggedIn && showAuth" class="min-h-screen flex items-center justify-center">
      <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-sm">
        <div class="text-center mb-6">
          <div class="text-4xl mb-2">🤖</div>
          <h2 class="text-xl font-bold text-gray-800">智能客服系统</h2>
          <p class="text-sm text-gray-500 mt-1">请登录以继续使用</p>
        </div>

        <div class="flex gap-2 mb-5">
          <button @click="authMode = 'login'" :class="authMode === 'login' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'" class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors">登录</button>
          <button @click="authMode = 'register'" :class="authMode === 'register' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'" class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors">注册</button>
        </div>

        <div class="space-y-3">
          <input v-model="form.username" type="text" placeholder="用户名"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          <input v-if="authMode === 'register'" v-model="form.email" type="email" placeholder="邮箱"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          <input v-model="form.password" type="password" placeholder="密码"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            @keyup.enter="submitAuth" />
        </div>

        <p v-if="authError" class="text-red-500 text-xs mt-2 text-center">{{ authError }}</p>

        <button @click="submitAuth" :disabled="authLoading"
          class="w-full mt-4 bg-blue-500 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-600 disabled:bg-gray-300 transition-colors">
          {{ authLoading ? '处理中...' : (authMode === 'login' ? '登录' : '注册') }}
        </button>

        <!-- 游客模式 -->
        <button @click="guestMode" class="w-full mt-2 text-sm text-gray-400 hover:text-gray-600 py-2">
          以游客身份继续 →
        </button>
      </div>
    </div>

    <!-- 已登录：主界面 -->
    <div v-else class="flex h-screen">
      <!-- 侧边栏（管理员显示） -->
      <aside v-if="store.currentUser?.role === 'admin'" class="w-48 bg-white border-r flex flex-col">
        <div class="p-4 border-b">
          <p class="font-semibold text-gray-700 text-sm">管理面板</p>
        </div>
        <nav class="flex-1 p-2 space-y-1">
          <button @click="currentView = 'chat'" :class="currentView === 'chat' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'" class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors">💬 对话</button>
          <button @click="currentView = 'admin'" :class="currentView === 'admin' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'" class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors">📚 知识库管理</button>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="flex-1 overflow-hidden">
        <ChatWindow v-if="currentView === 'chat'" />
        <KnowledgeAdmin v-else-if="currentView === 'admin'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from './store/chat.js'
import { authAPI } from './api/index.js'
import ChatWindow from './components/ChatWindow.vue'
import KnowledgeAdmin from './components/KnowledgeAdmin.vue'

const store = useChatStore()
const showAuth = ref(true)
const authMode = ref('login')
const authLoading = ref(false)
const authError = ref('')
const currentView = ref('chat')

const form = ref({ username: '', email: '', password: '' })

onMounted(async () => {
  if (store.accessToken) {
    await store.fetchMe()
    if (store.isLoggedIn) showAuth.value = false
  }
})

async function submitAuth() {
  authError.value = ''
  authLoading.value = true
  try {
    if (authMode.value === 'login') {
      await store.login(form.value.username, form.value.password)
    } else {
      await authAPI.register(form.value)
      await store.login(form.value.username, form.value.password)
    }
    showAuth.value = false
  } catch (e) {
    authError.value = typeof e === 'string' ? e : '操作失败，请重试'
  } finally {
    authLoading.value = false
  }
}

function guestMode() {
  showAuth.value = false
}
</script>
