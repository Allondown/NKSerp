import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const auth = {
  login: (data) => api.post('/auth/login', data).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
}

// Materials
export const materials = {
  list: () => api.get('/materials').then(r => r.data),
  create: (data) => api.post('/materials', data),
  update: (spec, data) => api.put(`/materials/${spec}`, data),
  delete: (spec) => api.delete(`/materials/${spec}`),
}

// Machines
export const machines = {
  list: () => api.get('/machines').then(r => r.data),
  create: (data) => api.post('/machines', data),
  delete: (name) => api.delete(`/machines/${name}`),
}

// Users
export const users = {
  list: (shift) => api.get('/users', { params: { shift } }).then(r => r.data),
  create: (data) => api.post('/users', data),
  update: (username, data) => api.put(`/users/${username}`, data),
  delete: (username) => api.delete(`/users/${username}`),
}

// Products
export const products = {
  list: (month, productCode) => api.get('/products', { params: { month, product_code: productCode || undefined } }).then(r => r.data),
  get: (code) => api.get(`/products/${code}`).then(r => r.data),
  create: (data) => api.post('/products', data),
  update: (data, originalCode, originalMonth) => api.put('/products', data, {
    params: { original_code: originalCode, original_month: originalMonth }
  }),
  delete: (code, month) => api.delete(`/products/${code}/${month}`),
}

// Purchases
export const purchases = {
  create: (data) => api.post('/purchases', data).then(r => r.data),
  list: (params) => api.get('/purchases', { params }).then(r => r.data),
  update: (id, data) => api.put(`/purchases/${id}`, data).then(r => r.data),
  delete: (id) => api.delete(`/purchases/${id}`),
}

// Issues
export const issues = {
  create: (data) => api.post('/issues', data).then(r => r.data),
  list: (params) => api.get('/issues', { params }).then(r => r.data),
  delete: (id) => api.delete(`/issues/${id}`),
}

// Inventory
export const inventory = {
  current: (spec) => api.get('/inventory/current', { params: { material_spec: spec } }).then(r => r.data),
}

// Production
export const production = {
  create: (data) => api.post('/production/daily', data).then(r => r.data),
  list: (params) => api.get('/production/daily', { params }).then(r => r.data),
  summary: (params) => api.get('/production/daily/summary', { params }).then(r => r.data),
  combinedCreate: (data) => api.post('/production/daily/combined', data).then(r => r.data),
  updateCombined: (data) => {
    const { original_date, original_machine, original_product_code, ...body } = data
    return api.put('/production/daily/combined', body, {
      params: { original_date, original_machine, original_product_code }
    }).then(r => r.data)
  },
  lastRecord: (productCode) => api.get(`/production/daily/last/${productCode}`).then(r => r.data),
  update: (id, data) => api.put(`/production/daily/${id}`, data),
  delete: (id) => api.delete(`/production/daily/${id}`),
  updateLossRemark: (data) => api.put('/production/daily/update-loss-remark', data).then(r => r.data),
  exportExcel: (params) => api.get('/production/daily/export', { params, responseType: 'blob' }).then(r => {
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `生产日报_${params.start_date || ''}_${params.end_date || ''}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }),
  exportExcelList: (params) => api.get('/production/daily/export/list', { params, responseType: 'blob' }).then(r => {
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `生产日报明细_${params.start_date || ''}_${params.end_date || ''}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }),
}

// Post-process
export const postProcess = {
  create: (data) => api.post('/post-process', data).then(r => r.data),
  list: (params) => api.get('/post-process', { params }).then(r => r.data),
  update: (id, data) => api.put(`/post-process/${id}`, data),
  delete: (id) => api.delete(`/post-process/${id}`),
  exportExcel: (params) => api.get('/post-process/export', { params, responseType: 'blob' }).then(r => {
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `后工序登记_${params.start_date || ''}_${params.end_date || ''}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }),
}

// Tool Purchases
export const toolPurchases = {
  create: (data) => api.post('/tool-purchases', data).then(r => r.data),
  list: (params) => api.get('/tool-purchases', { params }).then(r => r.data),
  update: (id, data) => api.put(`/tool-purchases/${id}`, data),
  delete: (id) => api.delete(`/tool-purchases/${id}`),
}

// Warehouse Entry
export const warehouseEntry = {
  create: (data) => api.post('/warehouse-entry', data).then(r => r.data),
  list: (params) => api.get('/warehouse-entry', { params }).then(r => r.data),
  update: (id, data) => api.put(`/warehouse-entry/${id}`, data),
  delete: (id) => api.delete(`/warehouse-entry/${id}`),
  exportExcel: (params) => api.get('/warehouse-entry/export', { params, responseType: 'blob' }).then(r => {
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `后工序入仓报表_${params.year || ''}${params.month ? String(params.month).padStart(2, '0') : ''}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }),
}

// Operators
export const operators = {
  list: () => api.get('/operators').then(r => r.data),
  create: (data) => api.post('/operators', data),
  update: (id, data) => api.put(`/operators/${id}`, data),
  delete: (id) => api.delete(`/operators/${id}`),
}

// Reports
export const reports = {
  cost: (year, month) => api.get('/reports/cost', { params: { year, month } }).then(r => r.data),
  productAchieve: (year, month) => api.get('/reports/product-achieve', { params: { year, month } }).then(r => r.data),
  teamAchieve: (year, month) => api.get('/reports/team-achieve', { params: { year, month } }).then(r => r.data),
  employee: (year, month) => api.get('/reports/employee', { params: { year, month } }).then(r => r.data),
  progress: (year, month, productCode) => api.get('/reports/progress', { params: { year, month, product_code: productCode || undefined } }).then(r => r.data),
  postProcessSummary: (year) => api.get('/reports/post-process-summary', { params: { year } }).then(r => r.data),
  export: (reportType, year, month, productCode) => api.get('/reports/export/excel', {
    params: { report_type: reportType, year, month, product_code: productCode || undefined },
    responseType: 'blob'
  }).then(r => {
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${reportType}_${year}_${month}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }),
}

export default api
