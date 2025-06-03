import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

import { useAuthStore } from '@/stores/auth'
import App from './App.vue'
import router from './router'

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const app = createApp(App)
const pinia = createPinia()

app.use(createPinia())

app.use(pinia)
app.use(router)

app.use(ElementPlus)

//initialize auth state
const authStore = useAuthStore()
authStore.checkAuth()

app.mount('#app')