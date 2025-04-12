<template>
    <div class="admin-container">
      <h1>Admin Panel</h1>
      <p>Manage your LLM agent settings and configurations.</p>
  
      <el-tabs type="border-card">
        <el-tab-pane label="Settings">
          <h3>Agent Settings</h3>
          <el-form :model="settings" label-width="120px">
            <el-form-item label="API Endpoint">
              <el-input v-model="settings.apiEndpoint" />
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="settings.apiKey" show-password />
            </el-form-item>
            <el-form-item label="Model">
              <el-select v-model="settings.model" placeholder="Select Model">
                <el-option label="GPT-3.5" value="gpt-3.5-turbo" />
                <el-option label="GPT-4" value="gpt-4" />
                <el-option label="Claude" value="claude" />
                <el-option label="Llama 2" value="llama-2" />
              </el-select>
            </el-form-item>
            <el-form-item label="Temperature">
              <el-slider v-model="settings.temperature" :min="0" :max="1" :step="0.1" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">Save Settings</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
  
        <el-tab-pane label="Commands">
          <h3>Custom Commands</h3>
          <el-table :data="commands" style="width: 100%">
            <el-table-column prop="name" label="Name" width="180" />
            <el-table-column prop="description" label="Description" />
            <el-table-column label="Operations" width="150">
              <template #default="scope">
                <el-button size="small" @click="editCommand(scope.row)">Edit</el-button>
                <el-button size="small" type="danger" @click="deleteCommand(scope.row)">Delete</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 20px">
            <el-button type="primary" @click="addCommand">Add Command</el-button>
          </div>
        </el-tab-pane>
  
        <el-tab-pane label="Logs">
          <h3>System Logs</h3>
          <el-input
            type="textarea"
            :rows="10"
            placeholder="No logs available"
            v-model="logs"
            readonly
          />
          <div style="margin-top: 10px">
            <el-button @click="refreshLogs">Refresh Logs</el-button>
            <el-button type="danger" @click="clearLogs">Clear Logs</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive } from 'vue'
  import { ElMessage } from 'element-plus'
  import { ElMessageBox } from 'element-plus'
  
  // Settings form
  const settings = reactive({
    apiEndpoint: 'http://localhost:8080/api/v1',
    apiKey: '',
    model: 'gpt-3.5-turbo',
    temperature: 0.7
  })
  
  // Commands table
  const commands = ref([
    { name: 'summarize', description: 'Summarize the given text' },
    { name: 'translate', description: 'Translate text to another language' },
    { name: 'analyze', description: 'Analyze sentiment of the text' }
  ])
  
  // Logs
  const logs = ref('')
  
  // Methods
  const saveSettings = () => {
    ElMessage.success('Settings saved successfully')
  }
  
  const addCommand = () => {
    ElMessageBox.prompt('Enter command name', 'Add Command', {
      confirmButtonText: 'Add',
      cancelButtonText: 'Cancel',
    }).then(({ value }) => {
      if (value) {
        commands.value.push({
          name: value,
          description: 'New command'
        })
        ElMessage.success(`Command ${value} added`)
      }
    })
  }
  
  const editCommand = (row: any) => {
    ElMessageBox.prompt('Edit command description', 'Edit Command', {
      confirmButtonText: 'Save',
      cancelButtonText: 'Cancel',
      inputValue: row.description
    }).then(({ value }) => {
      if (value) {
        row.description = value
        ElMessage.success(`Command ${row.name} updated`)
      }
    })
  }
  
  const deleteCommand = (row: any) => {
    ElMessageBox.confirm(
      `Are you sure to delete command ${row.name}?`,
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    ).then(() => {
      commands.value = commands.value.filter(cmd => cmd.name !== row.name)
      ElMessage.success(`Command ${row.name} deleted`)
    })
  }
  
  const refreshLogs = () => {
    logs.value = `[${new Date().toISOString()}] System logs refreshed\n` + logs.value
  }
  
  const clearLogs = () => {
    logs.value = ''
    ElMessage.success('Logs cleared')
  }
  </script>
  
  <style scoped>
  .admin-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
  }
  </style>