<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()

// Dropdown menu states
const adminMenuOpen = ref(false)
const aiAgentsMenuOpen = ref(false)
const aiToolsMenuOpen = ref(false)

// Timeout references for each menu
let adminCloseTimeout: ReturnType<typeof setTimeout> | null = null
let aiAgentsCloseTimeout: ReturnType<typeof setTimeout> | null = null
let aiToolsCloseTimeout: ReturnType<typeof setTimeout> | null = null

const handleLogout = () => {
  authStore.logout()
}

// Admin menu handlers
const toggleAdminMenu = () => {
  adminMenuOpen.value = !adminMenuOpen.value
}

const openAdminMenu = () => {
  if (adminCloseTimeout) {
    clearTimeout(adminCloseTimeout)
    adminCloseTimeout = null
  }
  adminMenuOpen.value = true
}

const closeAdminMenu = () => {
  adminMenuOpen.value = false
  if (adminCloseTimeout) {
    clearTimeout(adminCloseTimeout)
    adminCloseTimeout = null
  }
}

const startAdminCloseTimeout = () => {
  adminCloseTimeout = setTimeout(() => {
    adminMenuOpen.value = false
  }, 200)
}

// AI Agents menu handlers
const toggleAiAgentsMenu = () => {
  aiAgentsMenuOpen.value = !aiAgentsMenuOpen.value
}

const openAiAgentsMenu = () => {
  if (aiAgentsCloseTimeout) {
    clearTimeout(aiAgentsCloseTimeout)
    aiAgentsCloseTimeout = null
  }
  aiAgentsMenuOpen.value = true
}

const closeAiAgentsMenu = () => {
  aiAgentsMenuOpen.value = false
  if (aiAgentsCloseTimeout) {
    clearTimeout(aiAgentsCloseTimeout)
    aiAgentsCloseTimeout = null
  }
}

const startAiAgentsCloseTimeout = () => {
  aiAgentsCloseTimeout = setTimeout(() => {
    aiAgentsMenuOpen.value = false
  }, 200)
}

// AI Tools menu handlers
const toggleAiToolsMenu = () => {
  aiToolsMenuOpen.value = !aiToolsMenuOpen.value
}

const openAiToolsMenu = () => {
  if (aiToolsCloseTimeout) {
    clearTimeout(aiToolsCloseTimeout)
    aiToolsCloseTimeout = null
  }
  aiToolsMenuOpen.value = true
}

const closeAiToolsMenu = () => {
  aiToolsMenuOpen.value = false
  if (aiToolsCloseTimeout) {
    clearTimeout(aiToolsCloseTimeout)
    aiToolsCloseTimeout = null
  }
}

const startAiToolsCloseTimeout = () => {
  aiToolsCloseTimeout = setTimeout(() => {
    aiToolsMenuOpen.value = false
  }, 200)
}

// Check if current route is an admin route
const isAdminRoute = () => {
  return route.path.startsWith('/admin') || route.path.startsWith('/rbac')
}

// Check if current route is an AI Agents route
const isAiAgentsRoute = () => {
  return route.path.startsWith('/recommendations') ||
         route.path.startsWith('/secretary') ||
         route.path.startsWith('/learning') ||
         route.path.startsWith('/medical-paper') ||
         route.path.startsWith('/translation') ||
         route.path.startsWith('/philosophy')
}

// Check if current route is an AI Tools route
const isAiToolsRoute = () => {
  return route.path.startsWith('/weather') || 
         route.path.startsWith('/tools/')
}
</script>

<template>
  <header class="bg-white shadow-sm">
    <nav class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between items-center">
        <div class="flex items-center">
          <RouterLink to="/" class="text-2xl font-bold text-primary-600">
            Lazy Rabbit Agent
          </RouterLink>
        </div>

        <div class="flex items-center gap-4">
          <RouterLink
            v-if="!authStore.isAuthenticated"
            to="/signin"
            class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
          >
            Sign In
          </RouterLink>
          <RouterLink
            v-if="!authStore.isAuthenticated"
            to="/signup"
            class="bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 rounded-md text-sm font-medium"
          >
            Sign Up
          </RouterLink>

          <template v-if="authStore.isAuthenticated">
            <!-- AI Agents Dropdown Menu -->
            <div
              class="relative"
              @mouseenter="openAiAgentsMenu"
              @mouseleave="startAiAgentsCloseTimeout"
            >
              <button
                @click="toggleAiAgentsMenu"
                :class="[
                  'text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1',
                  isAiAgentsRoute() ? 'text-primary-600 font-semibold' : ''
                ]"
              >
                🤖 AI Agents
                <svg
                  class="w-4 h-4 transition-transform"
                  :class="{ 'rotate-180': aiAgentsMenuOpen }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- AI Agents Dropdown -->
              <div
                v-show="aiAgentsMenuOpen"
                class="absolute left-0 mt-0 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
                @mouseenter="openAiAgentsMenu"
                @mouseleave="startAiAgentsCloseTimeout"
              >
                <div class="py-1">
                  <RouterLink
                    to="/secretary"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🤖 Personal Secretary
                  </RouterLink>
                  <RouterLink
                    to="/learning"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📚 Learning History
                  </RouterLink>
                  <RouterLink
                    to="/medical-paper"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📄 Medical Paper
                  </RouterLink>
                  <RouterLink
                    to="/recommendations"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    👔 AI Dress Agent
                  </RouterLink>
                  <RouterLink
                    to="/translation"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🌐 Translation
                  </RouterLink>
                  <RouterLink
                    to="/philosophy"
                    @click="closeAiAgentsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🧠 Philosophy Master
                  </RouterLink>
                </div>
              </div>
            </div>

            <!-- AI Tools Dropdown Menu -->
            <div
              class="relative"
              @mouseenter="openAiToolsMenu"
              @mouseleave="startAiToolsCloseTimeout"
            >
              <button
                @click="toggleAiToolsMenu"
                :class="[
                  'text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1',
                  isAiToolsRoute() ? 'text-primary-600 font-semibold' : ''
                ]"
              >
                🛠️ AI Tools
                <svg
                  class="w-4 h-4 transition-transform"
                  :class="{ 'rotate-180': aiToolsMenuOpen }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- AI Tools Dropdown -->
              <div
                v-show="aiToolsMenuOpen"
                class="absolute left-0 mt-0 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
                @mouseenter="openAiToolsMenu"
                @mouseleave="startAiToolsCloseTimeout"
              >
                <div class="py-1">
                  <!-- Utility Tools -->
                  <div class="px-4 py-1 text-xs text-gray-500 font-semibold uppercase">Utility</div>
                  <RouterLink
                    to="/weather"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🌤️ Weather
                  </RouterLink>
                  <RouterLink
                    to="/tools/calculator"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🧮 Calculator
                  </RouterLink>
                  <RouterLink
                    to="/tools/datetime"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🕐 Date & Time
                  </RouterLink>
                  
                  <!-- Productivity Tools -->
                  <div class="px-4 py-1 mt-2 text-xs text-gray-500 font-semibold uppercase border-t">Productivity</div>
                  <RouterLink
                    to="/tools/notes"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📝 Notes
                  </RouterLink>
                  <RouterLink
                    to="/tools/tasks"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    ✅ Tasks
                  </RouterLink>
                  <RouterLink
                    to="/tools/reminders"
                    @click="closeAiToolsMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    ⏰ Reminders
                  </RouterLink>
                </div>
              </div>
            </div>
            
            <!-- Admin Dropdown Menu -->
            <div
              v-if="authStore.isAdmin"
              class="relative"
              @mouseenter="openAdminMenu"
              @mouseleave="startAdminCloseTimeout"
            >
              <button
                @click="toggleAdminMenu"
                :class="[
                  'text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1',
                  isAdminRoute() ? 'text-primary-600 font-semibold' : ''
                ]"
              >
                ⚙️ Admin
                <svg
                  class="w-4 h-4 transition-transform"
                  :class="{ 'rotate-180': adminMenuOpen }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- Dropdown Menu -->
              <div
                v-show="adminMenuOpen"
                class="absolute left-0 mt-0 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
                @mouseenter="openAdminMenu"
                @mouseleave="startAdminCloseTimeout"
              >
                <div class="py-1">
                  <RouterLink
                    v-if="authStore.isSuperAdmin"
                    to="/admin/users"
                    @click="closeAdminMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    👥 Users
                  </RouterLink>
                  <RouterLink
                    v-if="authStore.isAdmin"
                    to="/admin/email-management"
                    @click="closeAdminMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    📧 Email Settings
                  </RouterLink>
                  <RouterLink
                    v-if="authStore.isSuperAdmin"
                    to="/rbac/roles"
                    @click="closeAdminMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🔐 Roles
                  </RouterLink>
                  <RouterLink
                    v-if="authStore.isSuperAdmin"
                    to="/rbac/permissions"
                    @click="closeAdminMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    🔑 Permissions
                  </RouterLink>
                </div>
              </div>
            </div>
            
            <RouterLink
              to="/profile"
              class="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Profile
            </RouterLink>
            <button
              @click="handleLogout"
              class="text-gray-700 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </template>
        </div>
      </div>
    </nav>
  </header>
</template>


