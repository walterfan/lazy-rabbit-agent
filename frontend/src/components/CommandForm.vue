<template>
    <div class="command-form">
      <el-form :model="form" @submit.prevent="submitForm">
        <el-form-item label="Command">
          <el-autocomplete
            v-model="form.command"
            :fetch-suggestions="queryCommands"
            placeholder="Enter or select a command"
            class="command-input"
            clearable
          />
        </el-form-item>
  
        <el-form-item label="Input">
          <el-input
            v-model="form.input"
            type="textarea"
            :rows="6"
            placeholder="Enter your prompt here"
          />
        </el-form-item>
  
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">
            Submit
          </el-button>
        </el-form-item>
      </el-form>
  
      <div class="output-container">
        <h3>Output</h3>
        <div class="output" v-html="output"></div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive } from 'vue'
  import axios from 'axios'
  
  // Predefined commands
  const predefinedCommands = [
    { value: 'summarize', label: 'Summarize Text' },
    { value: 'translate', label: 'Translate Text' },
    { value: 'analyze', label: 'Analyze Sentiment' },
    { value: 'generate', label: 'Generate Content' },
    { value: 'extract', label: 'Extract Information' }
  ]
  
  // Form data
  const form = reactive({
    command: '',
    input: ''
  })
  
  // Loading state and output
  const loading = ref(false)
  const output = ref('')
  
  // Autocomplete suggestions
  const queryCommands = (queryString: string, cb: (arg: any[]) => void) => {
    const results = queryString
      ? predefinedCommands.filter(command =>
          command.value.toLowerCase().includes(queryString.toLowerCase()) ||
          command.label.toLowerCase().includes(queryString.toLowerCase())
        )
      : predefinedCommands
  
    cb(results)
  }
  
  // Submit form
  const submitForm = async () => {
    if (!form.command) {
      ElMessage.warning('Please enter a command')
      return
    }
  
    loading.value = true
    output.value = 'Processing...'
  
    try {
      const response = await axios.post('/api/v1/commands', {
        command: form.command,
        input: form.input
      })
  
      output.value = response.data.result || JSON.stringify(response.data, null, 2)
    } catch (error: any) {
      output.value = `Error: ${error.message}`
      if (error.response) {
        output.value += `<br>Details: ${JSON.stringify(error.response.data, null, 2)}`
      }
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .command-form {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .command-input {
    width: 100%;
  }
  
  .output-container {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #e6e6e6;
    border-radius: 4px;
    background-color: #f9f9f9;
  }
  
  .output {
    min-height: 100px;
    white-space: pre-wrap;
    font-family: monospace;
    padding: 10px;
    background-color: #fff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
  }
  </style>
