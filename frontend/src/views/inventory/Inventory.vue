<template>
  <v-card title="实时库存查询">
    <v-card-text>
      <v-text-field v-model="search" label="搜索材料规格" prepend-icon="mdi-magnify" density="compact" class="mb-3" />
      <v-table density="compact">
        <thead>
          <tr>
            <th>材料规格</th>
            <th>库存总量（kg）</th>
            <th>库存总金额（元）</th>
            <th>加权平均单价（元/kg）</th>
            <th>最后更新</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredData" :key="r.material_spec">
            <td>{{ r.material_spec }}</td>
            <td>{{ r.total_qty_kg?.toFixed(2) }}</td>
            <td>{{ r.total_amount?.toFixed(2) }}</td>
            <td>{{ r.avg_price?.toFixed(4) }}</td>
            <td>{{ formatDate(r.last_updated) }}</td>
          </tr>
          <tr v-if="!filteredData.length"><td colspan="5" class="text-center">暂无库存数据</td></tr>
        </tbody>
      </v-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, onDeactivated } from 'vue'
import { inventory } from '../../api'

const data = ref([])
const search = ref('')
let timer = null

const filteredData = computed(() => {
  if (!search.value) return []
  return data.value.filter(r => r.material_spec?.includes(search.value))
})

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN')
}

async function refresh() {
  data.value = await inventory.current()
}

function startPoll() {
  stopPoll()
  timer = setInterval(refresh, 15000)
}

function stopPoll() {
  if (timer) { clearInterval(timer); timer = null }
}

onMounted(refresh)
onActivated(() => { refresh(); startPoll() })
onDeactivated(stopPoll)
</script>
