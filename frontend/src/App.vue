<template>
    <el-container class="main-container">
      <!-- Top Navigation Menu -->
      <el-header>
        <el-menu
          mode="horizontal"
          :default-active="activeTopMenu"
          class="top-menu"
        >
          <el-menu-item index="1">Home</el-menu-item>
          <el-menu-item index="2">Task</el-menu-item>
          <el-menu-item index="3">About</el-menu-item>
          <el-menu-item index="4">Admin</el-menu-item>
          <el-menu-item index="5">SignIn/SignUp</el-menu-item>
        </el-menu>
      </el-header>
  
      <el-container>
        <!-- Left Sub Menu -->
        <el-aside width="200px">
          <el-menu
            :default-active="activeSubMenu"
            class="sub-menu"
          >
            <el-menu-item index="1">List</el-menu-item>
            <el-menu-item index="2">Plan</el-menu-item>
            <el-menu-item index="3">Do</el-menu-item>
            <el-menu-item index="4">Check</el-menu-item>
            <el-menu-item index="5">Act</el-menu-item>
          </el-menu>
        </el-aside>
  
        <!-- Main Content -->
        <el-main>
          <el-form :model="form" label-position="top" class="task-form">
            <!-- Task Name -->
            <el-form-item label="Task Name">
              <el-select
                v-model="form.task_name"
                filterable
                allow-create
                placeholder="Select or input task"
              >
                <el-option
                  v-for="item in predefinedTasks"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
  
            <!-- Parameters -->
            <el-form-item label="Parameters">
              <el-input
                v-model="form.parameters"
                type="textarea"
                :rows="3"
                placeholder="Enter parameters"
              />
            </el-form-item>
  
            <!-- Prompt -->
            <el-form-item label="Prompt">
              <el-input
                v-model="form.prompt"
                type="textarea"
                :rows="3"
                placeholder="Enter prompt"
              />
            </el-form-item>
  
            <!-- Priority and Difficulty -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Priority">
                  <el-select v-model="form.priority" placeholder="Select priority">
                    <el-option
                      v-for="item in priorities"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Difficulty">
                  <el-select v-model="form.difficulty" placeholder="Select difficulty">
                    <el-option
                      v-for="item in difficulties"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
  
            <!-- Duration -->
            <el-form-item label="Duration">
              <el-input-group>
                <el-input v-model="form.duration" placeholder="Enter duration" />
                <el-select v-model="form.durationUnit" style="width: 120px">
                  <el-option label="Minutes" value="minute" />
                  <el-option label="Hours" value="hour" />
                  <el-option label="Days" value="day" />
                </el-select>
              </el-input-group>
            </el-form-item>
  
            <!-- Time Inputs -->
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="Schedule Time">
                  <el-date-picker
                    v-model="form.scheduleTime"
                    type="datetime"
                    placeholder="Select date"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Start Time">
                  <el-date-picker
                    v-model="form.startTime"
                    type="datetime"
                    placeholder="Select date"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="End Time">
                  <el-date-picker
                    v-model="form.endTime"
                    type="datetime"
                    placeholder="Select date"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Deadline">
                  <el-date-picker
                    v-model="form.deadline"
                    type="datetime"
                    placeholder="Select date"
                  />
                </el-form-item>
              </el-col>
            </el-row>
  
            <!-- Output -->
            <el-form-item label="Output">
              <el-input
                v-model="form.output"
                type="textarea"
                :rows="5"
                readonly
                placeholder="Task output will appear here"
              />
            </el-form-item>
  
            <!-- Buttons -->
            <el-form-item>
              <el-button type="primary" @click="submitForm">Submit</el-button>
              <el-button @click="autoFill">Auto Fill</el-button>
            </el-form-item>
          </el-form>
        </el-main>
      </el-container>
    </el-container>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive } from 'vue'
  import { ElMessage } from 'element-plus'
  import axios from 'axios'
  
  interface TaskForm {
    task_name: string
    parameters: string
    prompt: string
    priority: string
    difficulty: string
    duration: string
    durationUnit: string
    scheduleTime: Date | null
    startTime: Date | null
    endTime: Date | null
    deadline: Date | null
    output: string
  }
  
  const form = reactive<TaskForm>({
    task_name: '',
    parameters: '',
    prompt: '',
    priority: '',
    difficulty: '',
    duration: '',
    durationUnit: 'hour',
    scheduleTime: null,
    startTime: null,
    endTime: null,
    deadline: null,
    output: ''
  })
  
  const predefinedTasks = ref([
    'Research Task',
    'Development Task',
    'Testing Task',
    'Documentation Task'
  ])
  
  const priorities = ref(['Must Have', 'Should Have', 'Could Have', "Won't Have"])
  const difficulties = ref(['Hard', 'Medium', 'Easy'])
  
  const submitForm = async () => {
    try {
      const response = await axios.post('/api/tasks', form)
      form.output = JSON.stringify(response.data, null, 2)
      ElMessage.success('Task submitted successfully!')
    } catch (error) {
      ElMessage.error('Error submitting task')
      console.error('Submission error:', error)
    }
  }
  
  const autoFill = () => {
    form.task_name = 'Sample Task'
    form.parameters = 'param1: value1\nparam2: value2'
    form.prompt = 'Please generate a sample response'
    form.priority = 'Should Have'
    form.difficulty = 'Medium'
    form.duration = '2'
    form.durationUnit = 'hour'
    form.scheduleTime = new Date()
    form.startTime = new Date()
    form.endTime = new Date(Date.now() + 3600 * 1000 * 2)
    form.deadline = new Date(Date.now() + 3600 * 1000 * 24)
    form.output = 'Auto-filled sample data'
  }
  </script>
  
  <style scoped>
  .main-container {
    height: 100vh;
  }
  
  .top-menu {
    height: 100%;
  }
  
  .sub-menu {
    height: 100%;
  }
  
  .task-form {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .el-date-editor {
    width: 100%;
  }
  </style>