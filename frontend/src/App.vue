<template>
  <router-view />
  <v-snackbar
    v-for="toast in toasts"
    :key="toast.id"
    :model-value="true"
    :color="toast.type"
    :timeout="toast.timeout"
    location="top"
    transition="slide-y-transition"
    @update:model-value="onClose(toast.id)"
  >
    {{ toast.text }}
  </v-snackbar>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from './store/toast'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)

function onClose(id) {
  toastStore.remove(id)
}
</script>
