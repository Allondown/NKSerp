<template>
  <v-card title="后工序完成进度报表">
    <v-card-text>
      <v-row>
        <v-col cols="2"><v-select v-model="year" :items="years" label="年份" density="compact" /></v-col>
        <v-col cols="2"><v-select v-model="month" :items="months" label="月份" density="compact" /></v-col>
        <v-col cols="2"><v-text-field v-model="productCode" label="产品编号" density="compact" clearable hide-details /></v-col>
        <v-col cols="3"><v-btn color="primary" size="small" @click="loadData">查询</v-btn></v-col>
        <v-col cols="3" class="text-right"><v-btn color="success" size="small" variant="outlined" @click="exportExcel">导出</v-btn></v-col>
      </v-row>
      <v-table density="compact">
        <thead>
          <tr><th>产品编号</th><th>产品名称</th><th>A班总数</th><th>B班总数</th><th>AB班完成总数</th><th>未完成总数</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in data" :key="i">
            <td>{{ r.product_code }}</td>
            <td>{{ r.product_name }}</td>
            <td>{{ r.a_total }}</td>
            <td>{{ r.b_total }}</td>
            <td>{{ r.ab_total }}</td>
            <td>{{ r.uncompleted }}</td>
          </tr>
          <tr v-if="!data.length"><td colspan="6" class="text-center">暂无数据</td></tr>
        </tbody>
      </v-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reports } from '../../api'

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const productCode = ref('')
const years = [2025, 2026, 2027]
const months = Array.from({ length: 12 }, (_, i) => i + 1)
const data = ref([])

async function loadData() {
  data.value = await reports.progress(year.value, month.value, productCode.value)
}
function exportExcel() {
  reports.export('progress', year.value, month.value, productCode.value)
}
onMounted(loadData)
</script>
<style scoped>
.v-table {
  overflow: auto;
  max-height: calc(100vh - 180px);
}
thead {
  position: sticky;
  top: 0;
  z-index: 2;
}
thead th {
  background-color: #E3F2FD !important;
  color: #1565C0 !important;
  font-weight: 700;
  font-size: 1.08em;
}
th, td {
  border-bottom: 1px solid #ddd !important;
}
tbody tr {
  cursor: pointer;
  transition: background-color 0.15s;
}
tbody tr:hover {
  background-color: #E3F2FD !important;
}
</style>
