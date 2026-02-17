<script setup lang="ts">
import { computed } from 'vue';
import type { ChatMessage } from '@/types/secretary';

const props = defineProps<{
  message: ChatMessage;
  isStreaming?: boolean;
}>();

const isUser = computed(() => props.message.role === 'user');
const isAssistant = computed(() => props.message.role === 'assistant');
const isTool = computed(() => props.message.role === 'tool');

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
});

const roleLabel = computed(() => {
  switch (props.message.role) {
    case 'user':
      return '你';
    case 'assistant':
      return '秘书';
    case 'tool':
      return `工具: ${props.message.tool_name}`;
    case 'system':
      return '系统';
    default:
      return props.message.role;
  }
});
</script>

<template>
  <div
    class="flex gap-3 p-4"
    :class="{
      'flex-row-reverse': isUser,
      'bg-gray-50': isUser,
    }"
  >
    <!-- Avatar -->
    <div
      class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-medium"
      :class="{
        'bg-blue-500': isUser,
        'bg-green-500': isAssistant,
        'bg-purple-500': isTool,
        'bg-gray-500': !isUser && !isAssistant && !isTool,
      }"
    >
      {{ isUser ? '我' : isAssistant ? 'AI' : '⚙' }}
    </div>

    <!-- Content -->
    <div class="flex-1 max-w-[80%]">
      <!-- Header -->
      <div
        class="flex items-center gap-2 mb-1"
        :class="{ 'justify-end': isUser }"
      >
        <span class="text-sm font-medium text-gray-700">{{ roleLabel }}</span>
        <span class="text-xs text-gray-400">{{ formattedTime }}</span>
        <span
          v-if="isStreaming"
          class="text-xs text-blue-500 animate-pulse"
        >
          正在输入...
        </span>
      </div>

      <!-- Message bubble -->
      <div
        class="rounded-lg p-3"
        :class="{
          'bg-blue-500 text-white': isUser,
          'bg-white border border-gray-200': !isUser,
        }"
      >
        <!-- Content -->
        <div
          v-if="message.content"
          class="whitespace-pre-wrap break-words"
          v-html="message.content"
        />

        <!-- Tool calls -->
        <div
          v-if="message.tool_calls && message.tool_calls.length > 0"
          class="mt-2 space-y-2"
        >
          <div
            v-for="(tc, idx) in message.tool_calls"
            :key="idx"
            class="text-sm bg-gray-100 rounded p-2"
          >
            <div class="font-mono text-purple-600">
              🔧 {{ tc.tool }}
            </div>
            <div
              v-if="tc.args && Object.keys(tc.args).length > 0"
              class="text-xs text-gray-500 mt-1"
            >
              参数: {{ JSON.stringify(tc.args) }}
            </div>
            <div
              v-if="tc.result"
              class="text-xs text-green-600 mt-1"
            >
              结果: {{ tc.result }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
