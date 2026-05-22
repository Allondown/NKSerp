<template>
  <v-app>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card>
            <v-card-title class="text-center">
              <v-icon large start>mdi-factory</v-icon>
              机加工车间管理系统
            </v-card-title>
            <v-card-text>
              <v-text-field v-model="username" label="用户名" prepend-icon="mdi-account" />
              <v-text-field v-model="password" label="密码" prepend-icon="mdi-lock"
                type="password" @keyup.enter="handleLogin" />
              <v-alert v-if="error" type="error" :text="error" closable class="mb-2" />
              <v-btn block color="primary" size="large" :loading="loading" @click="handleLogin">
                登录
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
