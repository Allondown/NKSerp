<template>
  <v-card title="班组达成率报表">
    <v-card-text>
      <v-row>
        <v-col cols="3"><v-select v-model="year" :items="years" label="年份" /></v-col>
        <v-col cols="3"><v-select v-model="month" :items="months" label="月份" /></v-col>
        <v-col cols="3"><v-btn color="primary" @click="loadData">查询</v-btn></v-col>
        <v-col cols="3"><v-btn color="success" variant="outlined" @click="exportExcel">导出Excel</v-btn></v-col>
      </v-row>
      <v-table density="compact">
        <thead>
          <tr><th>班组</th><th>理论产量</th><th>实绩数量</th><th>良品数量</th><th>达成率</th><th>合格率</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in data" :key="i">
            <td>{{ r.shift }}</td><td>{{ r.theoretical_qty }}</td><td>{{ r.actual_qty }}</td>
            <td>{{ r.good_qty }}</td>
            <td>{{ (r.achieve_rate * 100).toFixed(1) }}%</td>
            <td>{{ (r.qualified_rate * 100).toFixed(1) }}%</td>
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
const data = ref([])

async function loadData() {
  data.value = await reports.teamAchieve(year.value, month.value)
}
function exportExcel() {
  reports.export('team-achieve', year.value, month.value)
}
onMounted(loadData)
</script>
