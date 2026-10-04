<script setup lang="ts">
import { chatStore } from '../../stores/chat'

const store = chatStore
</script>

<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="logo">🎓</div>
      <h1>校园学生智能体</h1>
      <p class="subtitle">探索更自然的校园信息交互方式</p>
      <input v-model="store.state.username" placeholder="用户名" />
      <input v-model="store.state.password" type="password" placeholder="密码" @keyup.enter="store.authenticate('login')" />
      <button @click="store.authenticate('login')">登录</button>
      <button class="ghost" @click="store.authenticate('register')">注册并登录</button>
      <p v-if="store.state.authError" class="error">{{ store.state.authError }}</p>
    </div>
  </div>
</template>
