<template>
  <el-container class="layout-container">
    <el-header height="60px" class="header">

      <el-menu
        mode="horizontal"
        :router="true"
        class="main-menu"
        active-text-color="#ffd04b"
        @select="handleSelect"
      > <el-menu-item index="1"><h2><b>Lazy Rabbit Agent</b></h2></el-menu-item>
        <el-menu-item index="2">Home</el-menu-item>
        <el-menu-item index="/prompt">Prompts</el-menu-item>
        <el-menu-item index="/conversation">Conversation</el-menu-item>
        <el-sub-menu index="/tools">
          <template #title>Tools</template>
          <el-menu-item index="/tools/encoding-conversion">Encoding conversion</el-menu-item>
          <el-menu-item index="/tools/regular-expression">Regular expression test</el-menu-item>
          <el-menu-item index="/tools/random-generation">Generate random text</el-menu-item>
          <el-menu-item index="/tools/cron-expression">Cron expression test</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/knowledge">Knowledge</el-menu-item>
        <el-menu-item index="/about">About</el-menu-item>
        <el-menu-item index="/admin">Admin</el-menu-item>
        <!-- Right-aligned spacer -->
        <div class="menu-spacer"></div>
        <el-menu-item index="/login"  v-if="!authStore.isAuthenticated">
          Login
        </el-menu-item>

        <el-menu-item
          index="/logout"
          v-else
          @click="handleLogout"
        >
          Logout
        </el-menu-item>
      </el-menu>

    </el-header>
    <el-container>
      <el-aside width="180px">
        <el-menu
          default-active="/plan"
          class="side-menu"
          :router="true"
        >
          <el-menu-item index="/adjust"><el-icon><Monitor /></el-icon><span>编程</span></el-menu-item>
          <el-menu-item index="/plan"><el-icon><Bell /></el-icon><span>计划</span></el-menu-item>
          <el-menu-item index="/do"><el-icon><Document /></el-icon><span>写作</span></el-menu-item>
          <el-menu-item index="/check"><el-icon><Notebook /></el-icon><span>读书</span></el-menu-item>

        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-header {
  padding: 0;
  border-bottom: 1px solid #e6e6e6;
}

.main-menu {
  height: 100%;

  background-color: #545c64;
  color: #fff;

}

/* Style menu items to be visible against the blue background */
:deep(.main-menu .el-menu-item) {
  color: white;
}

/* Style active menu item */
:deep(.main-menu .el-menu-item.is-active) {
  color: #ffd04b;
  background-color: gray;
}

/* Change hover effect */
:deep(.main-menu .el-menu-item:hover) {
  background-color: #0d3672;
}

.el-aside {
  border-right: 1px solid #e6e6e6;
}

.side-menu {
  height: 100%;
}

/* Add these styles to your existing ones */
.menu-spacer {
  flex-grow: 1;
}

/* Ensure menu items maintain proper alignment */
:deep(.el-menu--horizontal) {
  display: flex;
  width: 100%;
}

:deep(.el-menu--horizontal > .el-menu-item) {
  flex-shrink: 0;
}

/* Style submenu titles */
:deep(.main-menu .el-sub-menu__title) {
  color: white;
}

/* Style submenu items */
:deep(.main-menu .el-menu--inline .el-menu-item) {
  color: white;
  background-color: #393e46 !important;
}

/* Hover effect for submenu items */
:deep(.main-menu .el-menu--inline .el-menu-item:hover) {
  background-color: #0d3672 !important;
}

/* Active state for submenu items */
:deep(.main-menu .el-menu--inline .el-menu-item.is-active) {
  color: #ffd04b;
  background-color: gray !important;
}
</style>
<script lang="ts" setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import {
  Monitor,
  Menu as IconMenu,
  Document, Notebook, Memo, Bell,
  Location,
  Setting,
} from '@element-plus/icons-vue'

const activeIndex = ref('1')
const activeIndex2 = ref('1')
const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>