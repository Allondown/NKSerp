<template>
  <v-card title="原材料领用出库">
    <v-card-text>
      <v-row>
        <v-col cols="2">
          <v-select v-model="filterYear" :items="yearOptions" label="年份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="filterMonth" :items="monthOptions" label="月份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-btn variant="outlined" size="small" @click="loadRecords">查询</v-btn>
        </v-col>
        <v-col cols="6" class="text-right">
          <v-btn color="warning" prepend-icon="mdi-plus" @click="dialog = true">新增领用</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead>
          <tr><th>日期</th><th>材料</th><th>重量</th><th>成本</th><th>领用人</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>{{ formatDate(r.issue_date) }}</td>
            <td>{{ r.material_spec }}</td>
            <td>{{ r.issue_weight_kg }}</td>
            <td>{{ r.total_cost }}</td>
            <td>{{ r.operator }}</td>
            <td>
              <v-btn icon size="small" color="error" @click="remove(r.id)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!records.length"><td colspan="6" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="500">
      <v-card title="领用出库登记">
        <v-card-text>
          <v-text-field v-model="form.issue_date" label="出库日期" type="date" density="compact" />
          <v-select v-model="form.machine" :items="machineList" label="加工机器" density="compact" />
          <v-text-field v-model="form.product_code" label="产品编号" density="compact" />
          <v-select v-model="form.material_spec" :items="materialList" label="材料规格" density="compact"
            @update:model-value="updateAvgPrice" />
          <v-text-field :model-value="currentAvgPrice" label="当前加权均价（元/kg）" readonly variant="plain" density="compact" />
          <v-text-field v-model="form.issue_rods" label="领用数量（根数）" type="number" density="compact" />
          <v-text-field v-model="form.issue_weight_kg" label="领用总重量（kg）" type="number" density="compact" />
          <v-text-field :model-value="autoCost" label="领用成本" readonly variant="plain" density="compact" />
          <v-select v-model="form.operator" :items="operatorList" label="领用人" density="compact" />
          <v-text-field v-model="form.remark" label="备注" density="compact" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="warning" :loading="loading" @click="submit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>确定删除该领用记录吗？此操作不可撤销。</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmDialog = false">取消</v-btn>
          <v-btn color="error" @click="confirmDelete">删除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { issues, machines, materials, users, inventory } from '../../api'
const confirmDialog = ref(false)
const pendingDelete = ref(null)

const initForm = () => ({
  issue_date: new Date().toISOString().slice(0, 10),
  machine: '', product_code: '', material_spec: '',
  issue_rods: 0, issue_weight_kg: 0, operator: '', remark: '',
})

const form = ref(initForm())
const machineList = ref([])
const materialList = ref([])
const operatorList = ref([])
const records = ref([])
const currentAvgPrice = ref(0)
const loading = ref(false)
const dialog = ref(false)
const now = new Date()
const filterYear = ref(now.getFullYear())
const filterMonth = ref(now.getMonth() + 1)
const yearOptions = [2025, 2026, 2027]
const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1)

const autoCost = computed(() =>
  (parseFloat(form.value.issue_weight_kg || 0) * currentAvgPrice.value).toFixed(2)
)

async function updateAvgPrice(spec) {
  if (!spec) { currentAvgPrice.value = 0; return }
  const data = await inventory.current(spec)
  currentAvgPrice.value = data?.[0]?.avg_price || 0
}

async function submit() {
  loading.value = true
  try {
    await issues.create({
      ...form.value,
      issue_rods: parseFloat(form.value.issue_rods),
      issue_weight_kg: parseFloat(form.value.issue_weight_kg),
    })
    form.value = initForm()
    currentAvgPrice.value = 0
    dialog.value = false
    await loadRecords()
  } catch (e) {
    console.error('保存失败', e)
    console.error('保存失败', e)
  } finally {
    loading.value = false
  }
}

function remove(id) {
  pendingDelete.value = id
  confirmDialog.value = true
}
async function confirmDelete() {
  confirmDialog.value = false
  try {
    await issues.delete(pendingDelete.value)
    pendingDelete.value = null
    await loadRecords()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}

async function loadRecords() {
  const year = filterYear.value
  const month = filterMonth.value
  const startDate = `${year}-${String(month).padStart(2, '0')}-01`
  const endDate = `${year}-${String(month).padStart(2, '0')}-${new Date(year, month, 0).getDate()}`
  const res = await issues.list({ page: 1, page_size: 100, start_date: startDate, end_date: endDate })
  records.value = res.items
}

onMounted(async () => {
  machineList.value = (await machines.list()).map(m => m.machine_name)
  materialList.value = (await materials.list()).map(m => m.material_spec)
  operatorList.value = (await users.list()).map(u => u.real_name)
  await loadRecords()
})
</script>
