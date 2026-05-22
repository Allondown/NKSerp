<template>
  <v-row>
    <v-col cols="12" sm="6" md="3" v-for="card in kpiCards" :key="card.title">
      <v-card>
        <v-card-text class="text-center">
          <v-icon :color="card.color" size="40">{{ card.icon }}</v-icon>
          <div class="text-h5 font-weight-bold mt-2">{{ card.value }}</div>
          <div class="text-caption text-medium-emphasis">{{ card.title }}</div>
        </v-card-text>
      </v-card>
    </v-col>

    <v-col cols="12" md="6">
      <v-card title="本月采购趋势">
        <v-card-text>
          <v-table density="compact">
            <thead>
              <tr><th>材料规格</th><th>采购数量(kg)</th><th>采购金额(元)</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in purchaseSummary" :key="r._id">
                <td>{{ r._id }}</td><td>{{ r.qty.toFixed(1) }}</td><td>{{ r.amount.toFixed(2) }}</td>
              </tr>
              <tr v-if="!purchaseSummary.length"><td colspan="3" class="text-center">暂无数据</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>

    <v-col cols="12" md="6">
      <v-card title="库存概况">
        <v-card-text>
          <v-table density="compact">
            <thead>
              <tr><th>材料规格</th><th>库存(kg)</th><th>金额(元)</th><th>均价</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in inventoryData" :key="r.material_spec">
                <td>{{ r.material_spec }}</td>
                <td>{{ r.total_qty_kg.toFixed(1) }}</td>
                <td>{{ r.total_amount.toFixed(2) }}</td>
                <td>{{ r.avg_price.toFixed(2) }}</td>
              </tr>
              <tr v-if="!inventoryData.length"><td colspan="4" class="text-center">暂无数据</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { inventory, purchases } from '../../api'

const now = new Date()
const year = now.getFullYear()
const month = now.getMonth() + 1

const kpiCards = ref([
  { title: '本月采购额', icon: 'mdi-cart', color: 'primary', value: '加载中...' },
  { title: '库存总值', icon: 'mdi-warehouse', color: 'success', value: '加载中...' },
  { title: '库存项数', icon: 'mdi-shape', color: 'info', value: '加载中...' },
  { title: '整体合格率', icon: 'mdi-check-circle', color: 'accent', value: '加载中...' },
])

const purchaseSummary = ref([])
const inventoryData = ref([])

onMounted(async () => {
  try {
    const [invData, purchData] = await Promise.all([
      inventory.current(),
      purchases.list({ page: 1, page_size: 1000 }),
    ])
    inventoryData.value = invData || []

    // Aggregate purchase amounts by material
    const agg = {}
    let totalPurchaseAmount = 0
    let totalInventoryAmount = 0
    for (const r of purchData.items || []) {
      if (!agg[r.material_spec]) agg[r.material_spec] = { qty: 0, amount: 0 }
      agg[r.material_spec].qty += r.weight_kg || 0
      agg[r.material_spec].amount += r.total_price || 0
      totalPurchaseAmount += r.total_price || 0
    }
    purchaseSummary.value = Object.entries(agg).map(([k, v]) => ({ _id: k, ...v }))

    for (const r of invData || []) {
      totalInventoryAmount += r.total_amount || 0
    }

    kpiCards.value[0].value = `¥${totalPurchaseAmount.toFixed(0)}`
    kpiCards.value[1].value = `¥${totalInventoryAmount.toFixed(0)}`
    kpiCards.value[2].value = `${(invData || []).length} 项`
    kpiCards.value[3].value = `${purchData.total || 0} 条记录`
  } catch (e) {
    // silently fail
  }
})
</script>
