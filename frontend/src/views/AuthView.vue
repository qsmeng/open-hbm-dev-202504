<template>
  <div class="auth-view">
    <Header />
    <div class="auth-content">
      <div class="auth-container">
        <h2 class="auth-title">{{ isLogin ? '用户登录' : '用户注册' }}</h2>
        <form @submit.prevent="handleAuth" class="auth-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" v-model="username" required placeholder="请输入用户名">
          </div>
          <div v-if="!isLogin" class="form-group">
            <label for="email">邮箱</label>
            <input type="email" id="email" v-model="email" required placeholder="请输入邮箱">
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" v-model="password" required placeholder="请输入密码">
          </div>
          <div v-if="!isLogin" class="form-group">
            <label for="confirm-password">确认密码</label>
            <input type="password" id="confirm-password" v-model="confirmPassword" required placeholder="请再次输入密码">
          </div>
          <button type="submit" class="auth-button">{{ isLogin ? '登录' : '注册' }}</button>
        </form>
        <div class="auth-options">
          <a href="#" @click="toggleAuthMode" class="auth-link">
            {{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}
          </a>
          <a href="#" @click="handleForgotPassword" class="auth-link">忘记密码？</a>
        </div>
        <div class="form-group">
          <router-link to="/" class="back-button">返回首页</router-link>
        </div>
      </div>
    </div>
  </div>
  <Footer />
</template>

<script setup>
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const authMode = ref(route.query.mode || 'login') // 'login' | 'register' | 'forgot'
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const router = useRouter()

// 动态获取 API 基础路径
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/'

const isLogin = computed(() => authMode.value === 'login')
const isRegister = computed(() => authMode.value === 'register')

const toggleAuthMode = () => {
  authMode.value = isLogin.value ? 'register' : 'login'
}

// 处理忘记密码
const handleForgotPassword = async () => {
  const email = prompt('请输入注册邮箱')
  if (!email) return
  
  try {
    await axios.post(`${apiBaseUrl}/auth/reset-password`, { email })
    alert('密码重置链接已发送至您的邮箱')
  } catch (error) {
    console.error('密码重置失败:', error)
    alert(error.response?.data?.detail || '密码重置请求失败')
  }
}

// 表单验证
const validateForm = () => {
  if (!isLogin.value && password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return false
  }
  return true
}

// 处理登录/注册
const handleAuth = async () => {
  if (!validateForm()) return

  const endpoint = isLogin.value ? 'login' : 'register'
  const payload = {
    username: username.value,
    password: password.value,
    ...(isRegister.value && { email: email.value })
  }

  try {
    let response;
    if (isLogin.value) {
      const formData = new FormData();
      formData.append('username', username.value);
      formData.append('password', password.value);
      response = await axios.post(`${apiBaseUrl}/auth/token`, formData);
      
      // 存储JWT令牌
      localStorage.setItem('auth_token', response.data.access_token);
      router.push('/');
    } else {
      response = await axios.post(`${apiBaseUrl}/auth/register`, {
        username: username.value,
        email: email.value,
        password: password.value
      });
      alert('注册成功，请登录');
      toggleAuthMode();
    }
  } catch (error) {
    console.error('请求失败:', error)
    alert(error.response?.data?.detail || '请求失败，请稍后重试')
  }
}
</script>

<style scoped>
.auth-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.auth-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.auth-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.auth-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.auth-button:hover {
  background-color: #218838;
}

.auth-options {
  margin-top: 1rem;
  text-align: center;
}

.auth-link {
  color: #007bff;
  text-decoration: none;
  display: block;
  margin: 0.5rem 0;
}

.auth-link:hover {
  text-decoration: underline;
}

.back-button {
  display: inline-block;
  margin-top: 1rem;
  color: #6c757d;
  text-decoration: none;
}

.back-button:hover {
  color: #5a6268;
}
</style>