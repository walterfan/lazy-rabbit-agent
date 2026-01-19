<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'
import InputField from '@/components/forms/InputField.vue'
import ButtonComponent from '@/components/forms/ButtonComponent.vue'
import { validateEmail, validatePassword, validateFullName } from '@/utils/validators'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const fullName = ref('')
const emailError = ref<string | null>(null)
const passwordError = ref<string | null>(null)
const fullNameError = ref<string | null>(null)
const serverError = ref<string | null>(null)

const isFormValid = computed(() => {
  return (
    email.value &&
    password.value &&
    !emailError.value &&
    !passwordError.value &&
    !fullNameError.value
  )
})

const validateForm = () => {
  emailError.value = validateEmail(email.value)
  passwordError.value = validatePassword(password.value)
  fullNameError.value = validateFullName(fullName.value)
  return !emailError.value && !passwordError.value && !fullNameError.value
}

const handleSubmit = async () => {
  serverError.value = null

  if (!validateForm()) {
    return
  }

  try {
    await authStore.signup({
      email: email.value,
      password: password.value,
      full_name: fullName.value || undefined,
    })

    router.push('/profile')
  } catch (error: any) {
    serverError.value = error.message || 'Signup failed. Please try again.'
  }
}
</script>

<template>
  <AppLayout>
    <div class="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
      <div class="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 class="text-center text-3xl font-bold tracking-tight text-gray-900">
          Create your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Already have an account?
          <RouterLink to="/signin" class="font-medium text-primary-600 hover:text-primary-500">
            Sign in
          </RouterLink>
        </p>
      </div>

      <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div class="bg-white px-6 py-8 shadow sm:rounded-lg sm:px-10">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div v-if="serverError" class="rounded-md bg-red-50 p-4">
              <p class="text-sm text-red-800">{{ serverError }}</p>
            </div>

            <InputField
              v-model="email"
              label="Email"
              type="email"
              placeholder="you@example.com"
              :error="emailError"
              required
              @blur="emailError = validateEmail(email)"
            />

            <InputField
              v-model="fullName"
              label="Full Name"
              type="text"
              placeholder="John Doe"
              :error="fullNameError"
              @blur="fullNameError = validateFullName(fullName)"
            />

            <InputField
              v-model="password"
              label="Password"
              type="password"
              placeholder="••••••••"
              :error="passwordError"
              required
              @blur="passwordError = validatePassword(password)"
            />

            <ButtonComponent
              type="submit"
              :disabled="!isFormValid || authStore.loading"
              :loading="authStore.loading"
              full-width
            >
              Sign up
            </ButtonComponent>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>


