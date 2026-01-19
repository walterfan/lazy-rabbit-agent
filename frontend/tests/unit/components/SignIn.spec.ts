import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import SignIn from '@/views/auth/SignIn.vue'

describe('SignIn Component', () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/signin', component: SignIn },
      { path: '/signup', component: { template: '<div>SignUp</div>' } },
    ],
  })

  it('should render sign in form', () => {
    const wrapper = mount(SignIn, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.find('h2').text()).toContain('Sign in')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })
})


