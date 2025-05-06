<template>
  <header class="header">
    <div class="left-section">
      <router-link to="/">首页</router-link>
      <router-link to="/game">探索</router-link>
      <router-link to="/rule">规则</router-link>
    </div>
    <div class="right-section">
      <router-link v-if="!isLoggedIn" :to="{ path: '/auth', query: { mode: 'login' } }">登录</router-link>
      <router-link v-if="!isLoggedIn" :to="{ path: '/auth', query: { mode: 'register' } }">注册</router-link>
      <div v-else class="user-info">
        <span>{{ username }}</span>
        <button @click="logout">退出</button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  data() {
    return {
      isLoggedIn: false, // This should be managed according to your auth system
      username: '' // This should be populated with actual user data
    }
  },
  methods: {
    logout() {
      // Implement logout logic here
    }
  }
}
</script>

<style scoped>
/* Component-specific styles only */
.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
