<template>
  <v-card title="原材料采购入库">
    <v-card-text>
      <v-row>
        <v-col cols="2">
          <v-select v-model="filterYear" :items="yearOptions" label="年份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="filterMonth" :items="monthOptions" label="月份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-text-field v-model="searchSpec" label="按材料筛选" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-btn variant="outlined" size="small" @click="loadRecords">查询</v-btn>
        </v-col>
        <v-col cols="4" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增采购</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead>
          <tr><th>日期</th><th>材料</th><th>重量</th><th>单价</th><th>总价</th><th>备注</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredRecords" :key="r.id">
            <td>{{ formatDate(r.arrival_date) }}</td>
            <td>{{ r.material_spec }}</td>
            <td>{{ r.weight_kg }}</td>
            <td>{{ r.unit_price }}</td>
            <td>{{ r.total_price }}</td>
            <td>{{ r.remark }}</td>
            <td>
              <v-btn icon size="small" color="primary" class="mr-1" @click="openEdit(r)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.id)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!filteredRecords.length"><td colspan="7" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="500">
      <v-card :title="editingId ? '编辑采购记录' : '采购入库登记'">
        <v-card-text>
          <v-text-field v-model="form.arrival_date" label="到货时间" type="date" density="compact" />
          <v-select v-model="form.machine" :items="machineList" label="加工机器" density="compact" />
          <v-text-field v-model="form.product" label="产品名称" density="compact" />
          <v-text-field v-model="form.product_code" label="产品编号" density="compact" @blur="onProductCodeBlur" />
          <v-combobox v-model="form.material_spec" :items="materialList" label="材料规格" density="compact" />
          <v-text-field v-model="form.quantity_rods" label="入库数量（根数）" type="number" density="compact" />
          <v-text-field v-model="form.weight_kg" label="入库总重量（kg）" type="number" density="compact" />
          <v-text-field v-model="form.unit_price" label="实际单价（元/kg）" type="number" density="compact" />
          <v-text-field :model-value="autoTotalPrice" label="总价" readonly variant="plain" density="compact" />
          <v-text-field v-model="form.remark" label="备注" density="compact" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="primary" :loading="loading" @click="submit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>确定删除该采购记录吗？此操作不可撤销。</v-card-text>
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
import { purchases, machines, materials, products } from '../../api'
const initForm = () => ({
  arrival_date: new Date().toISOString().slice(0, 10),
  machine: '', product: '', product_code: '', material_spec: '',
  quantity_rods: null, weight_kg: null, unit_price: null, remark: '',
})

const form = ref(initForm())
const machineList = ref([])
const materialList = ref([])
const records = ref([])
const searchSpec = ref('')
const loading = ref(false)
const dialog = ref(false)
const editingId = ref(null)
const confirmDialog = ref(false)
const pendingDelete = ref(null)
const now = new Date()
const filterYear = ref(now.getFullYear())
const filterMonth = ref(now.getMonth() + 1)
const yearOptions = [2025, 2026, 2027]
const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1)

const autoTotalPrice = computed(() =>
  (parseFloat(form.value.weight_kg || 0) * parseFloat(form.value.unit_price || 0)).toFixed(2)
)

const filteredRecords = computed(() => {
  if (!searchSpec.value) return records.value
  return records.value.filter(r => r.material_spec.includes(searchSpec.value))
})

async function onProductCodeBlur() {
  if (!form.value.product_code) return
  try {
    const prod = await products.get(form.value.product_code)
    if (prod) {
      form.value.product = prod.product_name || ''
      form.value.material_spec = prod.material_spec || ''
    }
  } catch (_) { /* ignore */ }
}

function openAdd() {
  form.value = initForm()
  editingId.value = null
  dialog.value = true
}

function openEdit(r) {
  form.value = {
    arrival_date: toLocalDate(r.arrival_date),
    machine: r.machine || '',
    product: r.product || '',
    product_code: r.product_code || '',
    material_spec: r.material_spec || '',
    quantity_rods: r.quantity_rods,
    weight_kg: r.weight_kg,
    unit_price: r.unit_price,
    remark: r.remark || '',
  }
  editingId.value = r.id
  dialog.value = true
}

async function submit() {
  loading.value = true
  try {
    const payload = {
      ...form.value,
      weight_kg: parseFloat(form.value.weight_kg),
      unit_price: parseFloat(form.value.unit_price),
      quantity_rods: parseFloat(form.value.quantity_rods),
    }
    if (editingId.value) {
      await purchases.update(editingId.value, payload)
    } else {
      await purchases.create(payload)
    }
    form.value = initForm()
    editingId.value = null
    dialog.value = false
    await loadRecords()
  } catch (e) {
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
    await purchases.delete(pendingDelete.value)
    pendingDelete.value = null
    await loadRecords()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}

function toLocalDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}

async function loadRecords() {
  const year = filterYear.value
  const month = filterMonth.value
  const startDate = `${year}-${String(month).padStart(2, '0')}-01`
  const endDate = `${year}-${String(month).padStart(2, '0')}-${new Date(year, month, 0).getDate()}`
  const params = { page: 1, page_size: 100, start_date: startDate, end_date: endDate }
  const res = await purchases.list(params)
  records.value = res.items
}

onMounted(async () => {
  machineList.value = (await machines.list()).map(m => m.machine_name)
  materialList.value = (await materials.list()).map(m => m.material_spec)
  await loadRecords()
})
</script>
