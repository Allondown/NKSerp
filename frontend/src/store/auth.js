import { defineStore } from 'pinia'
import { auth as authApi } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.user?.role || '',
    username: (state) => state.user?.username || '',
    realName: (state) => state.user?.real_name || '',
  },
  actions: {
    async login(username, password) {
      const res = await authApi.login({ username, password })
      this.token = res.access_token
      this.user = { username: res.username, role: res.role, real_name: res.real_name }
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
