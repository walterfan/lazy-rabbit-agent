<template>
  <div class="prompt-list-container">

      <div class="header">
        <div class="search-container">
            <el-input
            v-model="searchKeyword"
            placeholder="Search prompts by name, description or tags"
            clearable
            style="width: 500px"
            @keyup.enter="handleSearch"
            >
            <template #append>
                <el-button 
                type="primary"
                @click="handleSearch"
                :icon="Search"
                circle
                />
            </template>
            </el-input>
        </div>
         <div class="import-container">
          <el-upload
            action=""
            :show-file-list="false"
            :before-upload="handleBeforeUpload"
            accept=".csv,.json,.yaml,.yml"
          >
            <el-button
              type="primary"
              :icon="FolderOpened"
            ></el-button>
          </el-upload>
          <el-button
            type="success"
            @click="handleImport"
            :icon="Upload"
            :disabled="!selectedFile"
            style="margin-left: 10px"
          >Import</el-button>
        </div>

        <div class="action-buttons">
            <el-button
            type="primary"
            @click="showAddDialog"
            :icon="Plus"
            circle
            />
        </div>
      </div>




    <el-table :data="prompts" style="width: 100%, border: 1px solid #dcdfe6">
      <el-table-column prop="name" label="Name" width="180" />
      <el-table-column prop="description" label="Description" show-overflow-tooltip />
      <el-table-column prop="systemPrompt" label="systemPrompt" show-overflow-tooltip />
      <el-table-column prop="userPrompt" label="userPrompt" show-overflow-tooltip />
      <el-table-column label="Tags" width="200">
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags"
            :key="tag.id"
            size="small"
            class="tag"
          >
            {{ tag.category }}/{{ tag.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="120" fixed="right">
        <template #default="{ row }">
        <el-button
            size="small"
            @click="handleEdit(row)"
            :icon="Edit"
            circle
        />
        <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
            :icon="Delete"
            circle
        />
        </template>
    </el-table-column>
    </el-table>

    <div class="pagination">
        <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchPrompts"
        @current-change="fetchPrompts"
        />
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? 'Edit Prompt' : 'Add Prompt'"
      width="50%"
    >
      <PromptForm
        ref="promptForm"
        :initial-data="currentPrompt"
        @submit-success="handleSubmitSuccess"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, FolderOpened, Upload } from '@element-plus/icons-vue'
import PromptForm from './PromptForm.vue'
import { API_CONFIG } from '@/config'

const searchKeyword = ref('')
// Table data and pagination
const prompts = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Dialog control
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentPrompt = ref<any>(null)
const promptForm = ref()

// Fetch prompts
const fetchPrompts = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/prompt/api/v1/prompts`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        keyword: searchKeyword.value || undefined // Only send if not empty
      },
    })
    prompts.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('Failed to fetch prompts:', error)
    ElMessage.error('Failed to load prompts')
  }
}

// Handle search button click
const handleSearch = () => {
  currentPage.value = 1 // Reset to first page when searching
  fetchPrompts()
}

// Handle pagination changes
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchPrompts()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchPrompts()
}


// Add new prompt
const showAddDialog = () => {
  isEditMode.value = false
  currentPrompt.value = null
  dialogVisible.value = true
}

// Edit prompt
const handleEdit = (prompt: any) => {
  isEditMode.value = true
  currentPrompt.value = { ...prompt }
  dialogVisible.value = true
}

// Delete prompt
const handleDelete = async (prompt: any) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure to delete prompt "${prompt.name}"?`,
      'Warning',
      {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    await axios.delete(`${API_CONFIG.BASE_URL}/prompt/api/v1/prompts/${prompt.id}`)
    ElMessage.success('Prompt deleted successfully')
    fetchPrompts()
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

// Submit form from dialog
const submitForm = async () => {
  if (promptForm.value) {
    try {
      await promptForm.value.submitForm()
      await fetchPrompts() // Refresh the prompt list after successful submission
      dialogVisible.value = false
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }
}
// Handle form submission success
const handleSubmitSuccess = () => {
  dialogVisible.value = false
  fetchPrompts()
}

const selectedFile = ref<File | null>(null)

const handleBeforeUpload = (file: File) => {
  selectedFile.value = file
  return false // Prevent automatic upload
}

const handleImport = async () => {
  if (!selectedFile.value) return
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    await axios.post(`${API_CONFIG.BASE_URL}/prompt/api/v1/prompts/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    ElMessage.success('Prompts imported successfully')
    selectedFile.value = null
    fetchPrompts() // Refresh the list
  } catch (error) {
    console.error('Import failed:', error)
    ElMessage.error('Failed to import prompts')
  }
}

// Initial fetch
onMounted(fetchPrompts)
</script>

<style scoped>
.prompt-list-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.search-container {
  flex: 1; /* Takes remaining space */
  max-width: 500px;
}

.import-container {
  display: flex;
  gap: 8px;
  margin-left: 40px;
}

.action-buttons {
  margin-left: auto; /* Pushes button to the right */
  margin-right: 40px;
  flex-shrink: 0;
}

</style>