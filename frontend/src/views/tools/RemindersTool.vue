<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import api from '@/services/api';

const reminderTitle = ref('');
const reminderTime = ref('');
const reminderRepeat = ref('none');
const result = ref<string | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const activeTab = ref<'list' | 'create'>('list');

const repeatOptions = [
  { value: 'none', label: '不重复' },
  { value: 'daily', label: '每天' },
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' },
];

async function createReminder() {
  if (!reminderTitle.value.trim() || !reminderTime.value) return;
  
  loading.value = true;
  error.value = null;
  result.value = null;
  
  try {
    let message = `设置提醒：${reminderTitle.value}，时间${reminderTime.value}`;
    if (reminderRepeat.value !== 'none') {
      const repeatLabel = repeatOptions.find(o => o.value === reminderRepeat.value)?.label;
      message += `，${repeatLabel}重复`;
    }
    
    const response = await api.post('/secretary/chat', { message });
    result.value = response.data.content;
    reminderTitle.value = '';
    reminderTime.value = '';
    reminderRepeat.value = 'none';
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to create reminder';
  } finally {
    loading.value = false;
  }
}

async function listReminders() {
  loading.value = true;
  error.value = null;
  result.value = null;
  
  try {
    const response = await api.post('/secretary/chat', {
      message: '显示我的提醒列表',
    });
    result.value = response.data.content;
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to list reminders';
  } finally {
    loading.value = false;
  }
}

async function listUpcomingReminders() {
  loading.value = true;
  error.value = null;
  result.value = null;
  
  try {
    const response = await api.post('/secretary/chat', {
      message: '显示今天的提醒',
    });
    result.value = response.data.content;
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to get upcoming reminders';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  listReminders();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    
    <div class="max-w-2xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-800 mb-2">⏰ Reminders Tool</h1>
      <p class="text-gray-600 mb-6">
        Set and manage your reminders.
      </p>
      
      <!-- Tabs -->
      <div class="flex gap-2 mb-6">
        <button
          v-for="tab in (['list', 'create'] as const)"
          :key="tab"
          type="button"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="{
            'bg-blue-500 text-white': activeTab === tab,
            'bg-white text-gray-700 hover:bg-gray-100': activeTab !== tab,
          }"
          @click="activeTab = tab"
        >
          {{ tab === 'list' ? '📋 List Reminders' : '➕ Create Reminder' }}
        </button>
      </div>
      
      <!-- Create Reminder -->
      <div v-if="activeTab === 'create'" class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Reminder Title</label>
          <input
            v-model="reminderTitle"
            type="text"
            placeholder="What to remember?"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Time</label>
            <input
              v-model="reminderTime"
              type="datetime-local"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Repeat</label>
            <select
              v-model="reminderRepeat"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="opt in repeatOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>
        <button
          type="button"
          :disabled="loading || !reminderTitle.trim() || !reminderTime"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="createReminder"
        >
          {{ loading ? 'Creating...' : 'Create Reminder' }}
        </button>
      </div>
      
      <!-- List Reminders -->
      <div v-if="activeTab === 'list'" class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex gap-2">
          <button
            type="button"
            :disabled="loading"
            class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="listReminders"
          >
            {{ loading ? 'Loading...' : 'All Reminders' }}
          </button>
          <button
            type="button"
            :disabled="loading"
            class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="listUpcomingReminders"
          >
            Today's Reminders
          </button>
        </div>
      </div>
      
      <!-- Result -->
      <div v-if="result || error" class="bg-white rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 mb-2">Result</h3>
        <div v-if="error" class="text-red-600">{{ error }}</div>
        <div v-else class="text-gray-800 whitespace-pre-wrap">{{ result }}</div>
      </div>
    </div>
  </div>
</template>
