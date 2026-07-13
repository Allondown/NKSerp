<template>
  <v-card title="刀具采购成本报表">
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
          <tr>
            <th>品名</th><th>规格</th><th>数量</th><th>单价</th><th>总金额</th>
            <th>加工产品</th><th>供应商</th><th>下单日期</th><th>到货日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in data.items" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.spec }}</td>
            <td>{{ r.quantity }}</td>
            <td>{{ r.unit_price }}</td>
            <td>{{ r.total_amount }}</td>
            <td>{{ r.processed_product }}</td>
            <td>{{ r.supplier }}</td>
            <td>{{ formatDate(r.order_date) }}</td>
            <td>{{ formatDate(r.arrival_date) }}</td>
          </tr>
          <tr v-if="data.items && data.items.length">
            <td colspan="4" class="text-right"><strong>合计</strong></td>
            <td><strong>{{ data.total_cost }}</strong></td>
            <td colspan="4" />
          </tr>
          <tr v-if="!data.items || !data.items.length">
            <td colspan="9" class="text-center">暂无数据</td>
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
const data = ref({ items: [], total_cost: 0 })

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

async function loadData() {
  data.value = await reports.toolPurchaseCost(year.value, month.value)
}

function exportExcel() {
  reports.export('tool-purchase-cost', year.value, month.value)
}

onMounted(loadData)
</script>
