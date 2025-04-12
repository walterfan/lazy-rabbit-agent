<template>
  <div class="about-container">
    <h1>About LLM Agent</h1>
    <p>This application provides a user-friendly interface to interact with your LLM (Large Language Model) agent.</p>

    <el-divider />

    <h2>Features</h2>
    <el-descriptions border>
      <el-descriptions-item label="Plan">Create and organize your LLM tasks</el-descriptions-item>
      <el-descriptions-item label="Do">Execute commands and interact with the LLM</el-descriptions-item>
      <el-descriptions-item label="Check">Verify results and analyze performance</el-descriptions-item>
      <el-descriptions-item label="Adjust">Fine-tune parameters and optimize your agent</el-descriptions-item>
    </el-descriptions>

    <el-divider />

    <h2>Technology Stack</h2>
    <el-tag>Vue.js 3</el-tag>
    <el-tag>TypeScript</el-tag>
    <el-tag>Element Plus</el-tag>
    <el-tag>Vite</el-tag>
  </div>
</template>

<style scoped>
.about-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.el-tag {
  margin-right: 10px;
}
</style>