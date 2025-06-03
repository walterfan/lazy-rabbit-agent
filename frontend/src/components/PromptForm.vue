<template>
  <div class="prompt-form">
    <el-form :model="form" @submit.prevent="submitForm">
      <el-form-item label="Name">
        <el-input v-model="form.name" placeholder="Enter prompt name" />
      </el-form-item>

      <el-form-item label="Description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="Enter description"
        />
      </el-form-item>

      <el-form-item label="System Prompt">
        <el-input
          v-model="form.systemPrompt"
          type="textarea"
          :rows="4"
          placeholder="Enter system prompt"
        />
      </el-form-item>

      <el-form-item label="User Prompt">
        <el-input
          v-model="form.userPrompt"
          type="textarea"
          :rows="4"
          placeholder="Enter user prompt"
        />
      </el-form-item>

      <el-form-item label="Variables">
        <el-input
          v-model="form.variables"
          type="textarea"
          :rows="2"
          placeholder="Enter variables (comma separated)"
        />
      </el-form-item>

      <el-form-item label="Tags">
        <el-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          placeholder="Select or create tags"
          style="width: 100%"
        >
          <el-option
            v-for="tag in availableTags"
            :key="tag.id"
            :label="`${tag.name}`"
            :value="tag.id"
          />
        </el-select>
      </el-form-item>


    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { API_CONFIG } from '@/config'


const props = defineProps({
  initialData: {
    type: Object,
    default: null
  }
})

// Form data - initialize with props if available
const form = reactive({
  name: props.initialData?.name || '',
  description: props.initialData?.description || '',
  systemPrompt: props.initialData?.systemPrompt || '',
  userPrompt: props.initialData?.userPrompt || '',
  variables: props.initialData?.variables?.join(', ') || '',
  tags: props.initialData?.tags?.map(t => t.id) || [],
  created_by: props.initialData?.createdBy || 'admin'
})

// Watch for changes in initialData
watch(() => props.initialData, (newValue) => {
  if (newValue) {
    Object.assign(form, {
      name: newValue.name || '',
      description: newValue.description || '',
      systemPrompt: newValue.systemPrompt || '',
      userPrompt: newValue.userPrompt || '',
      variables: newValue.variables?.join(', ') || '',
      tags: newValue.tags?.map(t => t.id) || [],
      created_by: newValue.createdBy || 'admin'
    })
  }
}, { immediate: true })

// Available tags for selection
const availableTags = ref<Array<{id: number, category: string, name: string}>>([])
const loading = ref(false)

// Fetch available tags
const fetchTags = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/prompt/api/v1/tags`)
    availableTags.value = response.data
  } catch (error) {
    console.error('Failed to fetch tags:', error)
    ElMessage.error('Failed to load available tags')
  }
}

// Submit form
const submitForm = async () => {
  if (!form.name || !form.systemPrompt) {
    ElMessage.warning('Name and System Prompt are required')
    return
  }

  loading.value = true

  try {
    // First create any new tags that don't exist
    const newTags = form.tags.filter(tagId => 
      !availableTags.value.some(t => t.id === tagId)
    );
    
    if (newTags.length > 0) {
      await Promise.all(newTags.map(async (tagId) => {
        // Assuming tagId is actually the name for new tags
        // You may need to adjust this based on your actual tag structure
        const newTag = {
          category: 'prompt',
          name: tagId.toString()
        };
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}/prompt/api/v1/tags`,
          newTag
        );
        availableTags.value.push(response.data);
      }));
    }

    const requestData = {
      name: form.name,
      description: form.description,
      systemPrompt: form.systemPrompt,
      userPrompt: form.userPrompt,
      variables: form.variables.split(',').map(v => v.trim()).filter(Boolean),
      tags: form.tags.map(tagId => {
        const existingTag = availableTags.value.find(t => t.id === tagId);
        return {
          category: existingTag?.category || 'default',
          name: existingTag?.name || tagId.toString()
        };
      }),
      createdBy: form.created_by,
      updatedBy: form.created_by
    }

    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/prompt/api/v1/prompts`,
      requestData
    )

    ElMessage.success('Prompt created successfully')
    // Reset form after successful submission
    Object.assign(form, {
      name: '',
      description: '',
      systemPrompt: '',
      userPrompt: '',
      variables: '',
      tags: []
    })

    // Refresh available tags
    await fetchTags()
    
  } catch (error: any) {
    ElMessage.error(`Error: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

// Fetch tags when component mounts
onMounted(fetchTags)
// Expose submitForm for parent component
defineExpose({
  submitForm
})
</script>

<style scoped>
.prompt-form {
  max-width: 800px;
  margin: 0 auto;
}

.el-textarea,
.el-input {
  width: 100%;
}
</style>