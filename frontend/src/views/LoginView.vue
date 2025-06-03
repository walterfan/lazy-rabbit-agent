<template>
  <div class="login-container">
    <div class="login-form">
      <h2 class="login-title">Login</h2>
      <el-form
        :model="loginForm" 
        :rules="rules" 
        ref="loginFormRef"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Username"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="Password"
            type="password"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <div class="remember-forgot">
            <el-checkbox v-model="loginForm.rememberMe">Remember me</el-checkbox>
            <el-link type="primary" @click="handleForgotPassword">Forgot password?</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit"
            class="login-button"
            :loading="loading"
          >
            Login
          </el-button>
        </el-form-item>

        <div class="signup-link">
          Don't have an account? <el-link type="primary" @click="handleSignUp">Sign up</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { API_CONFIG } from '@/config'

const router = useRouter()


const loginForm = ref({
  username: '',
  password: '',
  rememberMe: false
})

const rules = ref<FormRules>({
  username: [
    { required: true, message: 'Please input username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please input password', trigger: 'blur' }
  ]
})

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const handleLogin = async () => {
  loginFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      
      try {
        const authStore = useAuthStore();
        const formData = new URLSearchParams();
        formData.append('username', loginForm.value.username);
        formData.append('password', loginForm.value.password);

        const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Login failed');
        }

        const data = await response.json();
        console.log('Login response:', data);
        authStore.login(data['access_token']);

        // Handle "Remember me" functionality
        if (loginForm.value.rememberMe) {
          localStorage.setItem('rememberedUser', loginForm.value.username);
        } else {
          localStorage.removeItem('rememberedUser');
        }

        ElMessage.success('Login successful');
        router.push('/');
      } catch (error) {
        console.error('Login error:', error);
        ElMessage.error('Invalid username or password');
      } finally {
        loading.value = false;
      }
    }
  });
};
const handleForgotPassword = () => {
  ElMessage.info('Forgot password feature coming soon')
  // router.push('/forgot-password') // You can implement this route later
}

const handleSignUp = () => {
  router.push('/signup') // You should create a SignUpView component
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  width: 400px;
  padding: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.remember-forgot {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.login-button {
  width: 100%;
}

.signup-link {
  text-align: center;
  margin-top: 20px;
  color: #606266;
}
</style>