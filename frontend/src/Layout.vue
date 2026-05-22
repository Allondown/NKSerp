<template>
  <v-app>
    <v-navigation-drawer permanent width="200">
      <v-list-item prepend-icon="mdi-factory" title="NKSerp" subtitle="车间管理系统" />
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-view-dashboard" title="仪表盘" @click="go('/')" color="primary" :active="isActive('/')" />
        <v-list-item prepend-icon="mdi-cart-arrow-down" title="采购入库" @click="go('/purchase')" color="primary" :active="isActive('/purchase')" />
        <v-list-item prepend-icon="mdi-cart-arrow-up" title="领用出库" @click="go('/issue')" color="primary" :active="isActive('/issue')" />
        <v-list-item prepend-icon="mdi-warehouse" title="库存查询" @click="go('/inventory')" color="primary" :active="isActive('/inventory')" />
        <v-list-item prepend-icon="mdi-calendar-text" title="生产日报" @click="go('/production/daily')" color="primary" :active="isActive('/production/daily')" />
        <v-list-item prepend-icon="mdi-hand-extended" title="后工序登记" @click="go('/post-process')" color="primary" :active="isActive('/post-process')" />

        <v-divider />
        <v-list-subheader>统计报表</v-list-subheader>
        <v-list-item prepend-icon="mdi-chart-box" title="成本报表" @click="go('/reports/cost')" color="primary" :active="isActive('/reports/cost')" />
        <v-list-item prepend-icon="mdi-chart-bar" title="产品报表" @click="go('/reports/product')" color="primary" :active="isActive('/reports/product')" />
        <v-list-item prepend-icon="mdi-group" title="班组报表" @click="go('/reports/team')" color="primary" :active="isActive('/reports/team')" />
        <v-list-item prepend-icon="mdi-account" title="员工报表" @click="go('/reports/employee')" color="primary" :active="isActive('/reports/employee')" />
        <v-list-item prepend-icon="mdi-progress-check" title="后工序完成进度报表" @click="go('/reports/progress')" color="primary" :active="isActive('/reports/progress')" />

        <v-divider />
        <v-list-subheader>基础数据</v-list-subheader>
        <v-list-item prepend-icon="mdi-shape" title="材料管理" @click="go('/settings/materials')" color="primary" :active="isActive('/settings/materials')" />
        <v-list-item prepend-icon="mdi-engine" title="机器管理" @click="go('/settings/machines')" color="primary" :active="isActive('/settings/machines')" />
        <v-list-item prepend-icon="mdi-account-group" title="人员管理" @click="go('/settings/users')" color="primary" :active="isActive('/settings/users')" />
        <v-list-item prepend-icon="mdi-package" title="产品主数据" @click="go('/settings/products')" color="primary" :active="isActive('/settings/products')" />
      </v-list>
      <template v-slot:append>
        <v-list density="compact" nav>
          <v-list-item :title="auth.realName" :subtitle="auth.role" />
          <v-list-item prepend-icon="mdi-logout" title="退出" @click="logout" />
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-app-bar flat>
      <v-app-bar-title>{{ currentTitle }}</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <keep-alive>
          <router-view />
        </keep-alive>
      </v-container>
    </v-main>

  </v-app>
</template>

<style>
html { font-size: 13px; }
.v-text-field input { font-size: 13px !important; }
.v-card-title { color: rgb(var(--v-theme-primary)) !important; }
::-webkit-calendar-picker-indicator { filter: invert(30%) sepia(60%) saturate(2000%) hue-rotate(190deg) brightness(95%) contrast(90%); }
.v-btn--icon { width: 28px !important; height: 28px !important; }
.v-btn--icon .v-icon { font-size: 18px !important; }
</style>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const currentTitle = computed(() => route.meta?.title || 'NKSerp')

function go(path) {
  router.push(path)
}

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
