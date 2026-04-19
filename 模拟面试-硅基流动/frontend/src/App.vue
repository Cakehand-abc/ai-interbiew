<template>
  <router-view />
</template>

<script setup lang="ts">
// App.vue 应该保持尽可能的简洁，只作为路由的渲染入口。
</script>

<style>
/* 在这里可以放置一些真正的全局样式，例如重置 body 的 margin */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #f9fafb;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
