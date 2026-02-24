<template>
  <!-- 聊天主窗口 -->
  <div class="flex flex-col h-screen bg-gray-50">

    <!-- 顶部导航栏 -->
    <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🤖</span>
        <div>
          <h1 class="font-semibold text-gray-800">智能客服</h1>
          <p class="text-xs text-green-500">● 在线服务中</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="store.currentUser" class="text-sm text-gray-600">
          {{ store.currentUser.username }}
        </span>
        <button @click="store.clearConversation"
          class="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 px-2 py-1 rounded-lg transition-colors">
          🗑 清空对话
        </button>
        <button v-if="store.isLoggedIn" @click="store.logout"
          class="text-xs text-gray-400 hover:text-red-500 transition-colors">
          退出
        </button>
      </div>
    </header>

    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto px-4 py-4 space-y-1">
      <!-- 欢迎消息 -->
      <div v-if="!store.messages.length" class="flex flex-col items-center justify-center h-full text-center text-gray-400 space-y-3">
        <div class="text-5xl">🤖</div>
        <h2 class="text-lg font-medium text-gray-600">您好，我是智能客服助手</h2>
        <p class="text-sm">有任何问题都可以向我咨询，我会尽力帮助您！</p>
        <!-- 快捷问题 -->
        <div class="flex flex-wrap gap-2 justify-center mt-4">
          <button v-for="q in quickQuestions" :key="q"
            @click="sendQuick(q)"
            class="text-xs bg-white border border-blue-200 text-blue-600 px-3 py-1.5 rounded-full hover:bg-blue-50 transition-colors">
            {{ q }}
          </button>
        </div>
      </div>

      <MessageBubble
        v-for="msg in store.messages"
        :key="msg.id"
        :message="msg"
        @feedback="handleFeedback"
      />

      <!-- 加载动画 -->
      <div v-if="store.isLoading && !store.isStreaming" class="flex justify-start mb-4">
        <div class="bg-white border border-gray-100 shadow-sm px-4 py-3 rounded-2xl rounded-tl-sm">
          <div class="flex gap-1 items-center">
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="bg-white border-t border-gray-200 px-4 py-3">
      <div class="flex items-end gap-2 max-w-4xl mx-auto">
        <div class="flex-1 relative">
          <textarea
            v-model="inputText"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact="inputText += '\n'"
            placeholder="请输入您的问题... (Enter 发送，Shift+Enter 换行)"
            rows="1"
            class="w-full resize-none border border-gray-300 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent max-h-32 overflow-y-auto"
            :disabled="store.isLoading || store.isStreaming"
            @input="autoResize"
            ref="textareaRef"
          ></textarea>
        </div>
        <button
          @click="sendMessage"
          :disabled="!inputText.trim() || store.isLoading || store.isStreaming"
          class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-2xl px-5 py-3 text-sm font-medium transition-colors flex-shrink-0"
        >
          {{ store.isStreaming ? '⏳' : '发送' }}
        </button>
      </div>
      <p class="text-center text-xs text-gray-300 mt-1">AI 生成内容仅供参考，重要决策请咨询专业人员</p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../store/chat.js'
import MessageBubble from './MessageBubble.vue'

const store = useChatStore()
const inputText = ref('')
const messageContainer = ref(null)
const textareaRef = ref(null)

const quickQuestions = [
  '如何申请退款？',
  '你们的售后政策是什么？',
  '如何联系人工客服？',
  '产品质量问题怎么处理？',
]

// 自动滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动
watch(() => store.messages.length, scrollToBottom)
watch(() => store.isStreaming, (val) => { if (val) scrollToBottom() })

// 发送消息（WebSocket 流式）
function sendMessage() {
  const text = inputText.value.trim()
  if (!text || store.isLoading || store.isStreaming) return
  inputText.value = ''
  resetTextarea()

  store.sendMessageStream(
    text,
    () => scrollToBottom(),        // onToken
    () => scrollToBottom(),        // onDone
    (err) => { console.error(err); alert('发送失败：' + err) }  // onError
  )
}

function sendQuick(q) {
  inputText.value = q
  sendMessage()
}

function handleFeedback(msgId, isHelpful) {
  console.log('feedback', msgId, isHelpful)
  // 可在此调用 store.submitFeedback
}

// textarea 自适应高度
function autoResize() {
  const ta = textareaRef.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 128) + 'px'
}

function resetTextarea() {
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
}
</script>
