import { defineStore } from 'pinia'

let nextId = 1

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [],
  }),
  actions: {
    show(text, type = 'info', timeout = 3000) {
      const id = nextId++
      this.toasts.push({ id, text, type, timeout })
      return id
    },
    success(text) {
      return this.show(text, 'success')
    },
    error(text) {
      return this.show(text, 'error', 5000)
    },
    warning(text) {
      return this.show(text, 'warning', 4000)
    },
    info(text) {
      return this.show(text, 'info')
    },
    remove(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
  },
})
