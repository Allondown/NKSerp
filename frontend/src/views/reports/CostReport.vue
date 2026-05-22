<template>
  <v-card title="月度成本报表">
    <v-card-text>
      <v-row>
        <v-col cols="3"><v-select v-model="year" :items="years" label="年份" /></v-col>
        <v-col cols="3"><v-select v-model="month" :items="months" label="月份" /></v-col>
        <v-col cols="3"><v-btn color="primary" @click="loadData">查询</v-btn></v-col>
        <v-col cols="3"><v-btn color="success" variant="outlined" @click="exportExcel">导出Excel</v-btn></v-col>
      </v-row>

      <v-table density="compact">
        <thead>
          <tr><th>材料规格</th><th>期初数量</th><th>期初金额</th><th>采购数量</th><th>采购金额</th><th>领用数量</th><th>领用成本</th><th>期末数量</th><th>期末金额</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in data.details" :key="r.material_spec">
            <td>{{ r.material_spec }}</td>
            <td>{{ r.begin_qty }}</td><td>{{ r.begin_amount }}</td>
            <td>{{ r.purchase_qty }}</td><td>{{ r.purchase_amount }}</td>
            <td>{{ r.issue_qty }}</td><td>{{ r.issue_cost }}</td>
            <td>{{ r.end_qty }}</td><td>{{ r.end_amount }}</td>
          </tr>
          <tr v-if="data.summary">
            <td><strong>合计</strong></td><td></td><td></td><td></td>
            <td><strong>{{ data.summary.total_purchase_amount }}</strong></td><td></td>
            <td><strong>{{ data.summary.total_issue_cost }}</strong></td><td></td>
            <td><strong>{{ data.summary.total_inventory_amount }}</strong></td>
          </tr>
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
const years = [2025, 2026, 2027]
const months = Array.from({ length: 12 }, (_, i) => i + 1)
const data = ref({ details: [], summary: null })

async function loadData() {
  data.value = await reports.cost(year.value, month.value)
}
function exportExcel() {
  reports.export('cost', year.value, month.value)
}

onMounted(loadData)
</script>
