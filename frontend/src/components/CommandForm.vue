<template>
    <div class="command-form">
      <el-form :model="form" @submit.prevent="submitForm">
        <el-form-item label="Command" class="form-row">
          <el-autocomplete
            v-model="form.command"
            :fetch-suggestions="queryCommands"
            placeholder="Enter or select a command"
            class="command-input"
            clearable
          />
        </el-form-item>

        <el-form-item label="System Prompt"  class="form-row">
          <el-input
            v-model="form.systemPrompt"
            type="textarea"
            :rows="2"
            placeholder="Enter your prompt here"
          />
        </el-form-item>

        <el-form-item label="User Prompt"  class="form-row">
          <el-input
            v-model="form.userPrompt"
            type="textarea"
            :rows="6"
            placeholder="Enter your prompt here"
          />
        </el-form-item>

        <el-form-item label="Input Source" class="form-row">
            <el-select v-model="form.inputSource" placeholder="Select input type" style="width: 100px; margin-right: 10px">
              <el-option
                v-for="type in inputSources"
                :key="type"
                :label="type"
                :value="type"
              />
            </el-select>
          <div class="language-selectors">
            Computer Language:
            <el-select v-model="form.computerLanguage" placeholder="Select" style="width: 100px; margin-right: 10px">
              <el-option
                v-for="lang in computerLanguages"
                :key="lang"
                :label="lang"
                :value="lang"
              />
            </el-select>
            Output Language:
            <el-select v-model="form.outputLanguage" placeholder="Select" style="width: 100px; margin-right: 10px">
              <el-option
                v-for="lang in outputLanguages"
                :key="lang"
                :label="lang"
                :value="lang"
              />
            </el-select>
            Model:
            <el-select v-model="form.model" placeholder="Select" style="width: 250px">
              <el-option
                v-for="lang in models"
                :key="lang"
                :label="lang"
                :value="lang"
              />
            </el-select>
          </div>
        </el-form-item>

        <el-form-item label="Input Content"  class="form-row">
          <el-upload
            action=""
            :show-file-list="false"
            :before-upload="handleBeforeUpload"
            accept=".csv,.json,.yaml,.yml"
          >

          <el-input
            v-model="form.inputContent"
            type="textarea"
            :rows="5"
            placeholder="Enter your prompt here"
            style="width: 800px; margin-right: 10px"
          />
          <el-button
              type="primary"
              :icon="FolderOpened"
            >Upload</el-button>
          </el-upload>
        </el-form-item>


      <el-form-item class="form-row">
        <div class="button-group">

          <el-button
            type="success"
            @click="submitForm" 
            :loading="loading"
            style="margin-left: 10px"
          >
            Submit
          </el-button>
        </div>
      </el-form-item>

      </el-form>

      <div class="output-container">
        <h3>Output</h3>
        <div class="output" v-html="output"></div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive, onMounted, watch } from 'vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  import { FolderOpened } from '@element-plus/icons-vue'

  const computerLanguages = ['Java', 'Golang', 'C++', 'JavaScript', 'Python', 'TypeScript', 'Lua', 'Rust']
  const outputLanguages = ['Chinese', 'English']
  const models = ['DeepSeek-R1-Distill-Qwen-32B', 'DeepSeek-R1-Distill-Llama-70B', 'Qwen3-235B-A22B']
  // Predefined commands
  const predefinedCommands = ref<Array<{value: string, label: string, rawData: object}>>([])

  // Form data
  const form = reactive({
    command: '',
    systemPrompt: '',
    userPrompt: '',
    model: "DeepSeek-R1-Distill-Qwen-32B",
    tags: [],
    computerLanguage: 'Java',     // Default value
    outputLanguage: 'Chinese',    // Default value
    inputSource: 'text',
    inputContent: '',
  })
  
  // Loading state and output
  const loading = ref(false)
  const output = ref('')

  const selectedFile = ref<File | null>(null)
  const inputSources = ['text', 'file', 'url', 'gitlab', 'github']

  // Fetch commands when component is mounted
  onMounted(async () => {
    try {
      const response = await axios.get('http://localhost:8000/prompt/api/v1/prompts?tagNames=code')

      // Transform API response to the format expected by el-autocomplete
      predefinedCommands.value = response.data.items.map((item: any) => ({
        value: item.name,                      // Use name as the command value
        label: `${item.name} - ${item.description}`, // Combine name and description for display
        rawData: item                          // Keep original data for reference
      }))

      // If no commands found, use fallback
      if (predefinedCommands.value.length === 0) {
        throw new Error('No commands found with code tag')
      }
      
    } catch (error) {
      console.error('Failed to fetch commands:', error)
      // Fallback to default commands if API fails or returns empty
      predefinedCommands.value = [
        { value: 'summarize', label: 'Summarize Text' },
        { value: 'translate', label: 'Translate Text' },
        { value: 'analyze', label: 'Analyze Sentiment' },
        { value: 'generate', label: 'Generate Content' },
        { value: 'extract', label: 'Extract Information' }
      ]
      ElMessage.warning('Using default commands as fallback')
    }
  })

  watch(() => form.command, (newCommand) => {
    if (!newCommand) return

    // Find the selected command in predefinedCommands
    const selectedCommand = predefinedCommands.value.find(cmd => cmd.value === newCommand)

    if (selectedCommand?.rawData) {
      // Fill the form with the command's prompt data
      form.systemPrompt = selectedCommand.rawData.systemPrompt || ''
      form.userPrompt = selectedCommand.rawData.userPrompt || ''
    }
  })
  const handleBeforeUpload = (file: File) => {
    selectedFile.value = file
    return false // Prevent automatic upload
  }

  // Modify queryCommands to use the dynamic predefinedCommands
  const queryCommands = (queryString: string, cb: (arg: any[]) => void) => {
    const results = queryString
      ? predefinedCommands.value.filter(command =>
          command.value.toLowerCase().includes(queryString.toLowerCase()) ||
          command.label.toLowerCase().includes(queryString.toLowerCase())
        )
      : predefinedCommands.value

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
      // Create WebSocket connection
      const socket = new WebSocket('ws://localhost:8000/ws') // Adjust URL as needed

      socket.onopen = () => {
        // Prepare messages array according to PromptRequest.Message model
        const messages = [
          {
            role: 'system',
            content: form.systemPrompt
          },
          {
            role: 'user',
            content: form.userPrompt
          }
        ].filter(msg => msg.content) // Filter out empty messages

        // Construct request payload matching PromptRequest model
        const requestData = {
          model: form.model,
          messages: messages,
          temperature: 0.7,
          maxTokens: 4096,
          computerLanguage: form.computerLanguage,
          outputLanguage: form.outputLanguage,
          inputSource: form.inputSource,
          inputContent: form.inputContent,
          trackId: generateUniqueId(), // Implement this function
          sessionId: getSessionId()    // Implement this function
        }

        // Send the data
        socket.send(JSON.stringify(requestData))
      }

      socket.onmessage = (event) => {
        const response = JSON.parse(event.data)
        output.value = response.result || JSON.stringify(response, null, 2)
        loading.value = false
        socket.close()
      }

      socket.onerror = (error) => {
        output.value = `WebSocket Error: ${error}`
        loading.value = false
        socket.close()
      }

    } catch (error: any) {
      output.value = `Error: ${error.message}`
      loading.value = false
    }
}

// Helper function examples (implement according to your needs)
function generateUniqueId(): string {
  return Math.random().toString(36).substring(2, 15)
}

function getSessionId(): string {
  // Get from localStorage or generate new
  return localStorage.getItem('sessionId') || generateUniqueId()
}
</script>

  <style scoped>
.command-form {
  max-width: 1200px;
  margin: 0 auto;
}

/* Form layout */
.el-form {
  display: grid;
  gap: 20px;
}


.form-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 10px;
}

.form-row:last-child {
  grid-template-columns: 120px auto;
  justify-items: start;
}

/* Input styling */
.command-input {
  width: 100%;
}

.input-textarea {
  width: 100%;
}

/* Output styling */
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

/* Align button with inputs */
.el-form-item:last-child {
  margin-left: 120px;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 10px; /* Modern way to add spacing between flex items */
}

/* OR for older browser support */
.button-group {
  display: flex;
  align-items: center;
}

.button-group > * {
  margin-right: 10px;
}

.button-group > *:last-child {
  margin-right: 0;
}

.language-selectors {
  display: flex;
  align-items: center;
  gap: 10px;
}


</style>

