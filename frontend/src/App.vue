<template>
  <el-container class="layout-container">
    <el-header height="60px">
      <el-menu
        mode="horizontal"
        :router="true"
        class="main-menu"
      >
        <el-menu-item index="/">Home</el-menu-item>
        <el-menu-item index="/about">About</el-menu-item>
        <el-menu-item index="/admin">Admin</el-menu-item>
      </el-menu>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <el-menu
          default-active="/plan"
          class="side-menu"
          :router="true"
        >
          <el-menu-item index="/plan">Plan</el-menu-item>
          <el-menu-item index="/do">Do</el-menu-item>
          <el-menu-item index="/check">Check</el-menu-item>
          <el-menu-item index="/adjust">Adjust</el-menu-item>
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
  background-color: #424249; /* Set menu background to match header */
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
</style>
