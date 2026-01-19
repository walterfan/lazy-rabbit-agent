<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'
import ButtonComponent from '@/components/forms/ButtonComponent.vue'

const authStore = useAuthStore()
</script>

<template>
  <AppLayout>
    <div class="text-center py-12">
      <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl mb-4">
        AI-Powered AI Recommendations
      </h1>
      <p class="text-lg leading-8 text-gray-600 max-w-2xl mx-auto mb-8">
        Get personalized outfit suggestions based on weather conditions, your style preferences,
        and daily recommendations delivered right to your inbox.
      </p>

      <div class="flex gap-4 justify-center">
        <RouterLink v-if="!authStore.isAuthenticated" to="/signup">
          <ButtonComponent>Get Started</ButtonComponent>
        </RouterLink>
        <RouterLink v-if="authStore.isAuthenticated" to="/profile">
          <ButtonComponent>Go to Profile</ButtonComponent>
        </RouterLink>
      </div>

      <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <RouterLink
          :to="authStore.isAuthenticated ? '/weather' : '/signin'"
          class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
        >
          <div class="text-4xl mb-4">🌤️</div>
          <h3 class="text-lg font-semibold mb-2">Weather-Based</h3>
          <p class="text-gray-600">
            Recommendations tailored to current and forecasted weather conditions
          </p>
          <div v-if="authStore.isAuthenticated" class="mt-4 text-blue-600 text-sm font-medium">
            View Weather →
          </div>
        </RouterLink>

        <RouterLink
          :to="authStore.isAuthenticated ? '/recommendations' : '/signin'"
          class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
        >
          <div class="text-4xl mb-4">🤖</div>
          <h3 class="text-lg font-semibold mb-2">AI-Powered</h3>
          <p class="text-gray-600">
            Advanced AI analyzes your preferences to suggest perfect outfits
          </p>
          <div v-if="authStore.isAuthenticated" class="mt-4 text-blue-600 text-sm font-medium">
            Get AI Recommendations →
          </div>
        </RouterLink>

        <div class="bg-white p-6 rounded-lg shadow">
          <div class="text-4xl mb-4">📧</div>
          <h3 class="text-lg font-semibold mb-2">Daily Emails</h3>
          <p class="text-gray-600">
            Receive personalized recommendations delivered to your inbox every morning
          </p>
          <div class="mt-4 text-gray-400 text-sm">
            Coming Soon
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>


