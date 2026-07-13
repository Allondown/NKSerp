<template>
  <v-app>
    <v-navigation-drawer permanent width="250">
      <v-list-item prepend-icon="mdi-factory" title="NKSerp" subtitle="车间管理系统" />
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-view-dashboard" title="仪表盘" @click="go('/')" color="primary" :active="isActive('/')" />
        <v-list-item prepend-icon="mdi-cart-arrow-down" title="原材料采购入库" @click="go('/purchase')" color="primary" :active="isActive('/purchase')" />
        <v-list-item prepend-icon="mdi-cart-arrow-up" title="原材料领用出库" @click="go('/issue')" color="primary" :active="isActive('/issue')" />
        <v-list-item prepend-icon="mdi-warehouse" title="库存查询" @click="go('/inventory')" color="primary" :active="isActive('/inventory')" />
        <v-list-item prepend-icon="mdi-wrench" title="刀具采购" @click="go('/tool-purchase')" color="primary" :active="isActive('/tool-purchase')" />
        <v-list-item prepend-icon="mdi-calendar-text" title="生产日报" @click="go('/production/daily')" color="primary" :active="isActive('/production/daily')" />
        <v-list-item prepend-icon="mdi-hand-extended" title="后工序登记" @click="go('/post-process')" color="primary" :active="isActive('/post-process')" />


        <v-divider />
        <v-list-subheader>统计报表</v-list-subheader>
        <v-list-item prepend-icon="mdi-chart-box" title="成本报表" @click="go('/reports/cost')" color="primary" :active="isActive('/reports/cost')" />
        <v-list-group value="tool-purchase-report-group">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-wrench" title="刀具采购报表" />
          </template>
          <v-list-item prepend-icon="mdi-chart-bell-curve" title="刀具采购成本报表" @click="go('/reports/tool-purchase-cost')" color="primary" :active="isActive('/reports/tool-purchase-cost')" />
          <v-list-item prepend-icon="mdi-store" title="供应商成本报表" @click="go('/reports/tool-supplier-cost')" color="primary" :active="isActive('/reports/tool-supplier-cost')" />
        </v-list-group>
        <v-list-group value="production-report-group">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-chart-line" title="生产数据统计报表" />
          </template>
          <v-list-item prepend-icon="mdi-chart-bar" title="产品报表" @click="go('/reports/product')" color="primary" :active="isActive('/reports/product')" />
          <v-list-item prepend-icon="mdi-group" title="班组报表" @click="go('/reports/team')" color="primary" :active="isActive('/reports/team')" />
          <v-list-item prepend-icon="mdi-account" title="员工报表" @click="go('/reports/employee')" color="primary" :active="isActive('/reports/employee')" />
        </v-list-group>
        <v-list-group value="post-process-report-group">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-folder-open" title="后工序报表" />
          </template>
          <v-list-item prepend-icon="mdi-progress-check" title="后工序完成进度报表" @click="go('/reports/progress')" color="primary" :active="isActive('/reports/progress')" />
          <v-list-item prepend-icon="mdi-archive-arrow-down" title="后工序入仓报表" @click="go('/warehouse-entry')" color="primary" :active="isActive('/warehouse-entry')" />
          <v-list-item prepend-icon="mdi-clipboard-text" title="后工序统计报表" @click="go('/reports/post-process-summary')" color="primary" :active="isActive('/reports/post-process-summary')" />
        </v-list-group>

        <v-divider />
        <v-list-subheader>基础数据</v-list-subheader>
        <v-list-item prepend-icon="mdi-shape" title="材料管理" @click="go('/settings/materials')" color="primary" :active="isActive('/settings/materials')" />
        <v-list-item prepend-icon="mdi-engine" title="机器管理" @click="go('/settings/machines')" color="primary" :active="isActive('/settings/machines')" />
        <v-list-item prepend-icon="mdi-package" title="产品主数据" @click="go('/settings/products')" color="primary" :active="isActive('/settings/products')" />
        <v-list-item prepend-icon="mdi-account-tie" title="班组人员管理" @click="go('/settings/operators')" color="primary" :active="isActive('/settings/operators')" />
        <v-list-item prepend-icon="mdi-store" title="刀具采购供应商管理" @click="go('/settings/suppliers')" color="primary" :active="isActive('/settings/suppliers')" />
        <v-list-item prepend-icon="mdi-account-group" title="系统账户管理" @click="go('/settings/users')" color="primary" :active="isActive('/settings/users')" />
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
