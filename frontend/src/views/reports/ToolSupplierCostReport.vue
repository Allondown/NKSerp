<template>
  <v-card title="供应商成本报表">
    <v-card-text>
      <v-row>
        <v-col cols="2"><v-select v-model="year" :items="years" label="年份" density="compact" /></v-col>
        <v-col cols="2"><v-select v-model="month" :items="months" label="月份" density="compact" /></v-col>
        <v-col cols="2"><v-btn color="primary" @click="loadData">查询</v-btn></v-col>
        <v-col cols="6" class="text-right">
          <v-btn color="success" variant="outlined" @click="exportExcel">导出Excel</v-btn>
        </v-col>
      </v-row>

      <v-table density="compact">
        <thead>
          <tr><th>供应商</th><th>采购笔数</th><th>采购金额</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in data.items" :key="r.supplier">
            <td>{{ r.supplier }}</td>
            <td>{{ r.count }}</td>
            <td>{{ r.total_cost }}</td>
          </tr>
          <tr v-if="data.items && data.items.length">
            <td><strong>合计</strong></td>
            <td />
            <td><strong>{{ data.grand_total }}</strong></td>
          </tr>
          <tr v-if="!data.items || !data.items.length">
            <td colspan="3" class="text-center">暂无数据</td>
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
const data = ref({ items: [], grand_total: 0 })

async function loadData() {
  data.value = await reports.toolSupplierCost(year.value, month.value)
}

function exportExcel() {
  reports.export('tool-supplier-cost', year.value, month.value)
}

onMounted(loadData)
</script>
