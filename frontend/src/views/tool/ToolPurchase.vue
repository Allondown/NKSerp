<template>
  <v-card title="刀具采购">
    <v-card-text>
      <v-row>
        <v-col cols="2">
          <v-select v-model="filterYear" :items="yearOptions" label="年份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="filterMonth" :items="monthOptions" label="月份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="filterStatus" :items="statusOptions" label="到货情况" density="compact" clearable />
        </v-col>
        <v-col cols="2">
          <v-btn variant="outlined" size="small" @click="loadRecords">查询</v-btn>
        </v-col>
        <v-col cols="6" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增刀具采购</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead>
          <tr>
            <th>下单日期</th><th>品名</th><th>规格</th><th>数量</th><th>单价（未税）</th><th>总金额（未税）</th>
            <th>加工产品</th><th>供应商</th><th>原料产地</th>
            <th>报价</th><th>到货日期</th><th>情况</th><th>备注</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>{{ formatDate(r.order_date) }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.spec }}</td>
            <td>{{ r.quantity }}</td>
            <td>{{ r.unit_price }}</td>
            <td>{{ r.total_amount }}</td>
            <td>{{ r.processed_product }}</td>
            <td>{{ r.supplier }}</td>
            <td>{{ r.material_origin }}</td>
            <td>{{ r.quotation }}</td>
            <td>{{ formatDate(r.arrival_date) }}</td>
            <td>{{ r.arrival_date ? '已到货' : '未到货' }}</td>
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
          <tr v-if="!records.length"><td colspan="14" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="600">
      <v-card :title="editingId ? '编辑刀具采购' : '新增刀具采购'">
        <v-card-text>
          <v-row dense>
            <v-col cols="6">
              <v-text-field v-model="form.order_date" label="下单日期" type="date" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.name" label="品名" density="compact" @blur="onNameBlur" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.spec" label="规格" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-text-field v-model="form.quantity" label="数量" type="number" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-text-field v-model="form.unit_price" label="单价（未税）" type="number" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-text-field :model-value="autoTotal" label="总金额（未税）" readonly variant="plain" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.processed_product" label="加工产品" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-select v-model="form.supplier" :items="supplierList" label="供应商" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-select v-model="form.material_origin" :items="originOptions" label="原料产地" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.quotation" label="报价" density="compact" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="form.arrival_date" label="到货日期" type="date" density="compact" />
            </v-col>
          </v-row>
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
        <v-card-text>确定删除该刀具采购记录吗？</v-card-text>
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
import { ref, computed, watch, onMounted } from 'vue'
import { toolPurchases, suppliers } from '../../api'

const initForm = () => ({
  name: '', spec: '', quantity: null, unit_price: null,
  processed_product: '', supplier: '', material_origin: '',
  order_date: new Date().toISOString().slice(0, 10),
  quotation: '', arrival_date: '', remark: '',
})

const form = ref(initForm())
const records = ref([])
const loading = ref(false)
const dialog = ref(false)
const editingId = ref(null)
const confirmDialog = ref(false)
const pendingDelete = ref(null)
const now = new Date()
const filterYear = ref(now.getFullYear())
const filterMonth = ref(now.getMonth() + 1)
const filterStatus = ref(null)
const yearOptions = [2025, 2026, 2027]
const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1)
const statusOptions = [
  { title: '已到货', value: 'arrived' },
  { title: '未到货', value: 'pending' },
]
const supplierList = ref([])
const originOptions = ['国产', '进口']

const autoTotal = computed(() =>
  (parseFloat(form.value.quantity || 0) * parseFloat(form.value.unit_price || 0)).toFixed(2)
)

watch(() => form.value.arrival_date, (val) => {
  if (val && !form.value.unit_price && form.value.quotation) {
    form.value.unit_price = parseFloat(form.value.quotation) || 0
  }
})

function toLocalDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

async function onNameBlur() {
  if (!form.value.name) return
  try {
    const last = await toolPurchases.lastByName(form.value.name)
    if (last) {
      if (!form.value.spec && last.spec) form.value.spec = last.spec
      if (!form.value.supplier && last.supplier) form.value.supplier = last.supplier
      if (!form.value.material_origin && last.material_origin) form.value.material_origin = last.material_origin
      if (!form.value.quotation && last.quotation) form.value.quotation = last.quotation
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
    name: r.name || '',
    spec: r.spec || '',
    quantity: r.quantity,
    unit_price: r.unit_price,
    processed_product: r.processed_product || '',
    supplier: r.supplier || '',
    material_origin: r.material_origin || '',
    order_date: toLocalDate(r.order_date),
    quotation: r.quotation || '',
    arrival_date: toLocalDate(r.arrival_date),
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
      quantity: parseFloat(form.value.quantity) || 0,
      unit_price: parseFloat(form.value.unit_price) || 0,
      arrival_date: form.value.arrival_date || null,
    }
    if (editingId.value) {
      await toolPurchases.update(editingId.value, payload)
    } else {
      await toolPurchases.create(payload)
    }
    dialog.value = false
    editingId.value = null
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
    await toolPurchases.delete(pendingDelete.value)
    pendingDelete.value = null
    await loadRecords()
  } catch (e) {
    console.error('删除失败', e)
  }
}

async function loadRecords() {
  const params = { year: filterYear.value, month: filterMonth.value, page_size: 200 }
  if (filterStatus.value) params.status = filterStatus.value
  const res = await toolPurchases.list(params)
  records.value = res.items || []
}

onMounted(async () => {
  supplierList.value = (await suppliers.list()).map(s => s.name)
  await loadRecords()
})
</script>
