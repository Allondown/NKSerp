<template>
  <v-card title="后工序入仓报表">
    <v-card-text>
      <v-row>
        <v-col cols="2"><v-select v-model="year" :items="years" label="年份" density="compact" /></v-col>
        <v-col cols="2"><v-select v-model="month" :items="months" label="月份" density="compact" /></v-col>
        <v-col cols="2"><v-text-field v-model="filterProductCode" label="产品编号" density="compact" clearable hide-details /></v-col>
        <v-col cols="2"><v-btn color="primary" @click="loadRecords">查询</v-btn></v-col>
        <v-col cols="4" class="text-right">
          <v-btn color="success" variant="outlined" @click="exportExcel">导出Excel</v-btn>
        </v-col>
      </v-row>

      <v-table density="compact">
        <thead>
          <tr><th>入仓日期</th><th>产品编号</th><th>产品名称</th><th>入仓数量</th><th>物料编码</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>{{ formatDate(r.entry_date) }}</td>
            <td>{{ r.product_code }}</td>
            <td>{{ r.product_name }}</td>
            <td>{{ r.entry_qty }}</td>
            <td>{{ r.material_code }}</td>
          </tr>
          <tr v-if="!records.length"><td colspan="5" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { warehouseEntry } from '../../api'

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const years = [2025, 2026, 2027]
const months = Array.from({ length: 12 }, (_, i) => i + 1)

const records = ref([])
const filterProductCode = ref('')

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

function getFilterParams() {
  const params = { year: year.value, month: month.value }
  if (filterProductCode.value) params.product_code = filterProductCode.value
  return params
}

async function loadRecords() {
  const res = await warehouseEntry.list(getFilterParams())
  records.value = res.items || []
}

function exportExcel() {
  warehouseEntry.exportExcel(getFilterParams())
}

onMounted(loadRecords)
</script>
