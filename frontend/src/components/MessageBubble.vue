<template>
  <!-- 消息气泡组件 -->
  <div :class="['flex mb-4', isUser ? 'justify-end' : 'justify-start']">
    <!-- 机器人头像 -->
    <div v-if="!isUser" class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm mr-2 flex-shrink-0 mt-1">
      🤖
    </div>

    <div :class="['max-w-[75%]', isUser ? 'items-end' : 'items-start', 'flex flex-col']">
      <!-- 消息内容 -->
      <div :class="[
        'px-4 py-3 rounded-2xl text-sm leading-relaxed break-words',
        isUser
          ? 'bg-blue-500 text-white rounded-tr-sm'
          : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-sm',
      ]">
        <!-- Markdown 渲染（AI回复） -->
        <div v-if="!isUser" v-html="renderedContent" class="prose prose-sm max-w-none"></div>
        <span v-else>{{ message.content }}</span>

        <!-- 流式光标 -->
        <span v-if="message.streaming" class="inline-block w-0.5 h-4 bg-blue-400 ml-0.5 animate-blink"></span>
      </div>

      <!-- 底部信息：意图标签 + 知识来源 + 反馈按钮 -->
      <div v-if="!isUser && !message.streaming" class="flex items-center gap-2 mt-1 px-1">
        <!-- 意图标签 -->
        <span v-if="message.intent" :class="intentClass" class="text-xs px-2 py-0.5 rounded-full">
          {{ intentLabel }}
        </span>

        <!-- 知识来源 -->
        <span v-if="message.sources?.length" class="text-xs text-gray-400">
          📚 {{ message.sources.slice(0, 2).join(' · ') }}
        </span>

        <!-- 点赞/踩 -->
        <div class="flex gap-1 ml-auto">
          <button @click="$emit('feedback', message.id, true)"
            class="text-gray-300 hover:text-green-500 transition-colors text-sm" title="有帮助">👍</button>
          <button @click="$emit('feedback', message.id, false)"
            class="text-gray-300 hover:text-red-400 transition-colors text-sm" title="没帮助">👎</button>
        </div>
      </div>
    </div>

    <!-- 用户头像 -->
    <div v-if="isUser" class="w-8 h-8 rounded-full bg-gray-400 flex items-center justify-center text-white text-sm ml-2 flex-shrink-0 mt-1">
      👤
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  message: { type: Object, required: true },
})
defineEmits(['feedback'])

const isUser = computed(() => props.message.role === 'user')

const renderedContent = computed(() => {
  try { return marked(props.message.content || '') }
  catch { return props.message.content || '' }
})

const INTENT_MAP = {
  inquiry:    { label: '咨询',   cls: 'bg-blue-50 text-blue-600' },
  complaint:  { label: '投诉',   cls: 'bg-red-50 text-red-600' },
  after_sales:{ label: '售后',   cls: 'bg-orange-50 text-orange-600' },
  chitchat:   { label: '闲聊',   cls: 'bg-gray-50 text-gray-500' },
  escalate:   { label: '转人工', cls: 'bg-purple-50 text-purple-600' },
  unknown:    { label: '未知',   cls: 'bg-gray-50 text-gray-400' },
}

const intentLabel = computed(() => INTENT_MAP[props.message.intent]?.label || '')
const intentClass = computed(() => INTENT_MAP[props.message.intent]?.cls || '')
</script>

<style scoped>
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.animate-blink { animation: blink 1s infinite; }
.prose :deep(p) { margin: 0.25rem 0; }
.prose :deep(ul), .prose :deep(ol) { padding-left: 1.25rem; }
.prose :deep(code) { background: #f3f4f6; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.85em; }
.prose :deep(pre) { background: #1e293b; color: #e2e8f0; padding: 0.75rem; border-radius: 6px; overflow-x: auto; }
</style>
