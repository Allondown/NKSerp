import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('../views/auth/Login.vue') },
  {
    path: '/',
    component: () => import('../Layout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/dashboard/Dashboard.vue'), meta: { title: '仪表盘' } },
      { path: 'purchase', name: 'Purchase', component: () => import('../views/purchase/Purchase.vue'), meta: { title: '原材料采购入库' } },
      { path: 'issue', name: 'Issue', component: () => import('../views/issue/Issue.vue'), meta: { title: '原材料领用出库' } },
      { path: 'inventory', name: 'Inventory', component: () => import('../views/inventory/Inventory.vue'), meta: { title: '库存查询' } },
      { path: 'production/daily', name: 'DailyProduction', component: () => import('../views/production/DailyProduction.vue'), meta: { title: '生产日报' } },
      { path: 'post-process', name: 'PostProcess', component: () => import('../views/PostProcess.vue'), meta: { title: '后工序登记' } },
      { path: 'tool-purchase', name: 'ToolPurchase', component: () => import('../views/tool/ToolPurchase.vue'), meta: { title: '刀具采购' } },
      { path: 'warehouse-entry', name: 'WarehouseEntry', component: () => import('../views/warehouse/WarehouseEntry.vue'), meta: { title: '后工序入仓报表' } },
      { path: 'reports/cost', name: 'CostReport', component: () => import('../views/reports/CostReport.vue'), meta: { title: '成本报表' } },
      { path: 'reports/tool-purchase-cost', name: 'ToolPurchaseCostReport', component: () => import('../views/reports/ToolPurchaseCostReport.vue'), meta: { title: '刀具采购成本报表' } },
      { path: 'reports/tool-supplier-cost', name: 'ToolSupplierCostReport', component: () => import('../views/reports/ToolSupplierCostReport.vue'), meta: { title: '供应商成本报表' } },
      { path: 'reports/product', name: 'ProductAchieve', component: () => import('../views/reports/ProductAchieve.vue'), meta: { title: '产品达成率' } },
      { path: 'reports/team', name: 'TeamReport', component: () => import('../views/reports/TeamReport.vue'), meta: { title: '班组报表' } },
      { path: 'reports/employee', name: 'EmployeeReport', component: () => import('../views/reports/EmployeeReport.vue'), meta: { title: '员工报表' } },
      { path: 'reports/progress', name: 'ProgressReport', component: () => import('../views/reports/ProgressReport.vue'), meta: { title: '后工序完成进度报表' } },
      { path: 'reports/post-process-summary', name: 'PostProcessReport', component: () => import('../views/reports/PostProcessReport.vue'), meta: { title: '后工序统计报表' } },
      { path: 'settings/materials', name: 'Materials', component: () => import('../views/settings/Materials.vue'), meta: { title: '材料管理' } },
      { path: 'settings/machines', name: 'Machines', component: () => import('../views/settings/Machines.vue'), meta: { title: '机器管理' } },
      { path: 'settings/users', name: 'Users', component: () => import('../views/settings/Users.vue'), meta: { title: '系统账户管理' } },
      { path: 'settings/operators', name: 'Operators', component: () => import('../views/settings/Operators.vue'), meta: { title: '班组人员管理' } },
      { path: 'settings/products', name: 'Products', component: () => import('../views/settings/Products.vue'), meta: { title: '产品主数据' } },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
