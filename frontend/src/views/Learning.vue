<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { marked } from 'marked';
import { useLearningStore } from '@/stores/learning';
import AppHeader from '@/components/layout/AppHeader.vue';
import type { LearningRecord, LearningRecordType } from '@/types/secretary';

const learningStore = useLearningStore();

const selectedRecord = ref<LearningRecord | null>(null);
const searchInput = ref('');

const typeLabels: Record<LearningRecordType, string> = {
  word: '单词',
  sentence: '句子',
  topic: '主题',
  article: '文章',
  question: '问答',
  idea: '想法',
};

const typeIcons: Record<LearningRecordType, string> = {
  word: '📝',
  sentence: '📖',
  topic: '🎓',
  article: '📰',
  question: '❓',
  idea: '💡',
};

const typeOptions: LearningRecordType[] = ['word', 'sentence', 'topic', 'article', 'question', 'idea'];

// Configure marked for safe rendering
marked.setOptions({
  breaks: true,
  gfm: true,
});

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Extract content from response_payload and convert to markdown
function getContentAsMarkdown(record: LearningRecord): string {
  if (!record.response_payload) return '';
  
  const payload = record.response_payload;
  
  // If payload has a 'content' field, use it directly
  if (typeof payload.content === 'string') {
    return payload.content;
  }
  
  // Otherwise, format the JSON nicely as markdown
  let content = '';
  
  for (const [key, value] of Object.entries(payload)) {
    if (value === null || value === undefined) continue;
    
    const label = formatKeyLabel(key);
    
    if (typeof value === 'string') {
      content += `### ${label}\n\n${value}\n\n`;
    } else if (Array.isArray(value)) {
      content += `### ${label}\n\n`;
      value.forEach((item, index) => {
        if (typeof item === 'string') {
          content += `${index + 1}. ${item}\n`;
        } else if (typeof item === 'object') {
          content += `${index + 1}. ${JSON.stringify(item)}\n`;
        }
      });
      content += '\n';
    } else if (typeof value === 'object') {
      content += `### ${label}\n\n`;
      for (const [subKey, subValue] of Object.entries(value)) {
        content += `- **${formatKeyLabel(subKey)}**: ${subValue}\n`;
      }
      content += '\n';
    } else {
      content += `### ${label}\n\n${value}\n\n`;
    }
  }
  
  return content;
}

function formatKeyLabel(key: string): string {
  // Convert snake_case or camelCase to readable format
  const keyMap: Record<string, string> = {
    content: '内容',
    word: '单词',
    pronunciation: '发音',
    meaning: '含义',
    example: '例句',
    examples: '例句',
    translation: '翻译',
    explanation: '解释',
    grammar: '语法',
    usage: '用法',
    summary: '摘要',
    mindmap: '思维导图',
    key_points: '要点',
    steps: '步骤',
    tags: '标签',
  };
  
  return keyMap[key] || key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
}

// Render markdown to HTML
const renderedContent = computed(() => {
  if (!selectedRecord.value) return '';
  const markdown = getContentAsMarkdown(selectedRecord.value);
  return marked(markdown);
});

async function handleSearch() {
  if (searchInput.value.trim()) {
    await learningStore.searchRecords(searchInput.value.trim());
  } else {
    await learningStore.listRecords(1);
  }
}

async function handleTypeFilter(type: LearningRecordType | null) {
  await learningStore.setTypeFilter(type);
}

async function handleToggleFavorites() {
  await learningStore.setFavoritesOnly(!learningStore.favoritesOnly);
}

async function handleToggleFavorite(record: LearningRecord) {
  await learningStore.toggleFavorite(record.id);
}

async function handleDelete(record: LearningRecord) {
  if (confirm('确定要删除这条学习记录吗？')) {
    await learningStore.deleteRecord(record.id);
    if (selectedRecord.value?.id === record.id) {
      selectedRecord.value = null;
    }
  }
}

async function handleMarkReviewed(record: LearningRecord) {
  await learningStore.markReviewed(record.id);
}

function handleSelectRecord(record: LearningRecord) {
  selectedRecord.value = record;
}

function handleCloseDetail() {
  selectedRecord.value = null;
}

async function handlePageChange(page: number) {
  if (learningStore.searchQuery) {
    await learningStore.searchRecords(learningStore.searchQuery, page);
  } else {
    await learningStore.listRecords(page);
  }
}

// Initialize
onMounted(async () => {
  await learningStore.listRecords(1);
  await learningStore.loadStatistics();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Top Navigation -->
    <AppHeader />
    
    <div class="min-h-[calc(100vh-64px)] bg-gray-100">
      <div class="max-w-7xl mx-auto p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-800">学习记录</h1>
            <p class="text-gray-500 mt-1">
              共 {{ learningStore.totalRecords }} 条记录
            </p>
          </div>
          
          <router-link
            to="/secretary"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            返回对话
          </router-link>
        </div>

        <!-- Statistics -->
        <div
          v-if="learningStore.statistics"
          class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
        >
          <div class="bg-white rounded-lg p-4 shadow-sm">
            <div class="text-2xl font-bold text-blue-600">
              {{ learningStore.statistics.total }}
            </div>
            <div class="text-sm text-gray-500">总记录</div>
          </div>
          <div class="bg-white rounded-lg p-4 shadow-sm">
            <div class="text-2xl font-bold text-yellow-500">
              {{ learningStore.statistics.favorites }}
            </div>
            <div class="text-sm text-gray-500">收藏</div>
          </div>
          <div class="bg-white rounded-lg p-4 shadow-sm">
            <div class="text-2xl font-bold text-green-600">
              {{ learningStore.statistics.total_reviews }}
            </div>
            <div class="text-sm text-gray-500">总复习次数</div>
          </div>
          <div class="bg-white rounded-lg p-4 shadow-sm">
            <div class="text-2xl font-bold text-purple-600">
              {{ Object.keys(learningStore.statistics.by_type).length }}
            </div>
            <div class="text-sm text-gray-500">类型数</div>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-lg p-4 shadow-sm mb-6">
          <div class="flex flex-wrap gap-4 items-center">
            <!-- Search -->
            <div class="flex-1 min-w-[200px]">
              <div class="relative">
                <input
                  v-model="searchInput"
                  type="text"
                  placeholder="搜索..."
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @keyup.enter="handleSearch"
                />
                <svg
                  class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>

            <!-- Type filter -->
            <div class="flex gap-2 flex-wrap">
              <button
                type="button"
                class="px-3 py-1.5 text-sm rounded-lg transition-colors"
                :class="{
                  'bg-blue-500 text-white': !learningStore.typeFilter,
                  'bg-gray-100 text-gray-700 hover:bg-gray-200': learningStore.typeFilter,
                }"
                @click="handleTypeFilter(null)"
              >
                全部
              </button>
              <button
                v-for="type in typeOptions"
                :key="type"
                type="button"
                class="px-3 py-1.5 text-sm rounded-lg transition-colors"
                :class="{
                  'bg-blue-500 text-white': learningStore.typeFilter === type,
                  'bg-gray-100 text-gray-700 hover:bg-gray-200': learningStore.typeFilter !== type,
                }"
                @click="handleTypeFilter(type)"
              >
                {{ typeIcons[type] }} {{ typeLabels[type] }}
              </button>
            </div>

            <!-- Favorites toggle -->
            <button
              type="button"
              class="px-3 py-1.5 text-sm rounded-lg transition-colors"
              :class="{
                'bg-yellow-500 text-white': learningStore.favoritesOnly,
                'bg-gray-100 text-gray-700 hover:bg-gray-200': !learningStore.favoritesOnly,
              }"
              @click="handleToggleFavorites"
            >
              ⭐ 只看收藏
            </button>
          </div>
        </div>

        <!-- Records list -->
        <div class="mb-6">
          <div
            v-if="learningStore.loading"
            class="text-center py-8 text-gray-500"
          >
            加载中...
          </div>
          
          <div
            v-else-if="learningStore.records.length === 0"
            class="text-center py-8 text-gray-500 bg-white rounded-lg shadow-sm"
          >
            暂无学习记录
          </div>
          
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            <div
              v-for="record in learningStore.records"
              :key="record.id"
              class="bg-white rounded-lg p-4 shadow-sm cursor-pointer hover:shadow-md transition-all"
              :class="{
                'ring-2 ring-blue-500 shadow-md': selectedRecord?.id === record.id,
              }"
              @click="handleSelectRecord(record)"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-xl">{{ typeIcons[record.input_type] }}</span>
                  <span class="text-sm text-gray-500">{{ typeLabels[record.input_type] }}</span>
                </div>
                
                <div class="flex items-center gap-1">
                  <button
                    type="button"
                    class="p-1 hover:bg-gray-100 rounded text-sm"
                    :class="{ 'text-yellow-500': record.is_favorite }"
                    @click.stop="handleToggleFavorite(record)"
                  >
                    {{ record.is_favorite ? '⭐' : '☆' }}
                  </button>
                  <button
                    type="button"
                    class="p-1 text-gray-400 hover:text-red-500 hover:bg-gray-100 rounded text-sm"
                    @click.stop="handleDelete(record)"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div class="mt-2 text-gray-800 font-medium line-clamp-2">
                {{ record.user_input }}
              </div>
              
              <div class="mt-2 flex items-center gap-3 text-xs text-gray-500">
                <span>{{ formatDate(record.created_at) }}</span>
                <span>复习 {{ record.review_count }} 次</span>
              </div>
              
              <div
                v-if="record.tags && record.tags.length > 0"
                class="mt-2 flex gap-1 flex-wrap"
              >
                <span
                  v-for="tag in record.tags.slice(0, 3)"
                  :key="tag"
                  class="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div
            v-if="learningStore.totalPages > 1"
            class="mt-6 flex justify-center gap-2"
          >
            <button
              type="button"
              :disabled="learningStore.currentPage === 1"
              class="px-3 py-1.5 rounded-lg bg-white border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              @click="handlePageChange(learningStore.currentPage - 1)"
            >
              上一页
            </button>
            <span class="px-3 py-1.5 text-gray-600">
              {{ learningStore.currentPage }} / {{ learningStore.totalPages }}
            </span>
            <button
              type="button"
              :disabled="learningStore.currentPage === learningStore.totalPages"
              class="px-3 py-1.5 rounded-lg bg-white border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              @click="handlePageChange(learningStore.currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>

        <!-- Detail panel (below the list) -->
        <div
          v-if="selectedRecord"
          class="bg-white rounded-lg shadow-sm"
        >
          <!-- Header -->
          <div class="p-4 border-b border-gray-200 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ typeIcons[selectedRecord.input_type] }}</span>
              <div>
                <span class="text-sm text-gray-500">{{ typeLabels[selectedRecord.input_type] }}</span>
                <h3 class="font-semibold text-gray-800 text-lg">{{ selectedRecord.user_input }}</h3>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="px-3 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors"
                @click="handleMarkReviewed(selectedRecord)"
              >
                标记已复习
              </button>
              <button
                type="button"
                class="px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                :class="{ 'text-yellow-500': selectedRecord.is_favorite }"
                @click="handleToggleFavorite(selectedRecord)"
              >
                {{ selectedRecord.is_favorite ? '⭐ 已收藏' : '☆ 收藏' }}
              </button>
              <button
                type="button"
                class="p-2 hover:bg-gray-100 rounded-lg text-gray-500"
                @click="handleCloseDetail"
              >
                ✕
              </button>
            </div>
          </div>
          
          <!-- Content (Markdown rendered) -->
          <div class="p-6">
            <div 
              class="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-600 prose-li:text-gray-600 prose-strong:text-gray-700"
              v-html="renderedContent"
            ></div>
          </div>
          
          <!-- Footer with meta info -->
          <div class="px-6 py-4 bg-gray-50 rounded-b-lg border-t border-gray-100">
            <div class="flex flex-wrap gap-4 text-sm text-gray-500">
              <span>创建时间: {{ formatDate(selectedRecord.created_at) }}</span>
              <span>复习次数: {{ selectedRecord.review_count }}</span>
              <span v-if="selectedRecord.last_reviewed_at">
                上次复习: {{ formatDate(selectedRecord.last_reviewed_at) }}
              </span>
              <span v-if="selectedRecord.tags && selectedRecord.tags.length > 0">
                标签: {{ selectedRecord.tags.join(', ') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Markdown content styling */
:deep(.prose h3) {
  @apply text-base font-semibold mt-4 mb-2 text-gray-800;
}

:deep(.prose p) {
  @apply my-2;
}

:deep(.prose ul) {
  @apply list-disc list-inside my-2;
}

:deep(.prose ol) {
  @apply list-decimal list-inside my-2;
}

:deep(.prose code) {
  @apply bg-gray-100 px-1.5 py-0.5 rounded text-sm;
}

:deep(.prose pre) {
  @apply bg-gray-100 p-4 rounded-lg overflow-x-auto my-4;
}

:deep(.prose pre code) {
  @apply bg-transparent p-0;
}

:deep(.prose blockquote) {
  @apply border-l-4 border-blue-500 pl-4 italic my-4 text-gray-600;
}
</style>
