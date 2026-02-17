<script setup lang="ts">
import type { ToolInfo } from '@/types/secretary';

const props = defineProps<{
  tools: ToolInfo[];
}>();

const emit = defineEmits<{
  (e: 'select', tool: ToolInfo): void;
}>();

const toolIcons: Record<string, string> = {
  learn_word: '📝',
  learn_sentence: '📖',
  learn_topic: '🎓',
  learn_article: '📰',
  answer_question: '❓',
  plan_idea: '💡',
  get_weather: '🌤️',
  calculate: '🔢',
  get_datetime: '📅',
};

function getIcon(toolName: string): string {
  return toolIcons[toolName] || '🔧';
}

function getCategoryLabel(category: string): string {
  switch (category) {
    case 'learning':
      return '学习工具';
    case 'utility':
      return '实用工具';
    default:
      return category;
  }
}

// Group tools by category
const groupedTools = computed(() => {
  const groups: Record<string, ToolInfo[]> = {};
  for (const tool of props.tools) {
    if (!groups[tool.category]) {
      groups[tool.category] = [];
    }
    groups[tool.category].push(tool);
  }
  return groups;
});

import { computed } from 'vue';
</script>

<template>
  <div class="p-4">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">
      可用工具
    </h3>
    
    <div
      v-if="tools.length === 0"
      class="text-gray-500 text-center py-4"
    >
      加载工具列表...
    </div>
    
    <div
      v-else
      class="space-y-4"
    >
      <div
        v-for="(categoryTools, category) in groupedTools"
        :key="category"
      >
        <h4 class="text-sm font-medium text-gray-600 mb-2">
          {{ getCategoryLabel(category) }}
        </h4>
        
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="tool in categoryTools"
            :key="tool.name"
            type="button"
            class="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
            @click="emit('select', tool)"
          >
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ getIcon(tool.name) }}</span>
              <span class="text-sm font-medium text-gray-700">
                {{ tool.name.replace(/_/g, ' ') }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-1 line-clamp-2">
              {{ tool.description }}
            </p>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
