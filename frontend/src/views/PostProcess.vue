<template>
  <v-card title="后工序物料进出登记">
    <v-card-text>
      <v-row>
        <v-col cols="3">
          <v-text-field v-model="filterStartDate" label="起始日期" type="date" density="compact" />
        </v-col>
        <v-col cols="3">
          <v-text-field v-model="filterEndDate" label="结束日期" type="date" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-text-field v-model="filterProductCode" label="产品编号" density="compact" clearable hide-details />
        </v-col>
        <v-col cols="1">
          <v-btn color="primary" variant="outlined" size="small" @click="loadRecords">查询</v-btn>
        </v-col>
        <v-col cols="2" class="text-right">
          <v-btn color="success" variant="outlined" @click="exportExcel" class="mr-2">导出Excel</v-btn>
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增登记</v-btn>
        </v-col>
      </v-row>

      <v-table density="compact">
        <thead>
          <tr>
            <th>机加送入日期</th><th>产品编号</th><th>产品名称</th>
            <th>送入数量</th><th>操作员</th><th>班组</th>
            <th>后工序完成送出日期</th><th>送出数量</th><th>未完成数量</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, idx) in records" :key="r.id">
            <td>{{ formatDate(r.received_date) }}</td>
            <td>{{ r.product_code }}</td>
            <td>{{ r.product_name }}</td>
            <td>{{ r.received_qty }}</td>
            <td>{{ r.operator }}</td>
            <td>{{ r.shift }}</td>
            <td>
              <v-text-field type="date"
                :model-value="formatDateISO(r.send_date)"
                @update:model-value="v => updateSendDate(r, v)"
                density="compact" hide-details style="min-width:160px" />
            </td>
            <td>
              <v-text-field type="number"
                :model-value="r.send_qty"
                @update:model-value="v => updateSendQty(r, v)"
                density="compact" hide-details style="width:100px" />
            </td>
            <td>{{ Math.max(0, (r.received_qty || 0) - (r.send_qty || 0)) }}</td>
            <td>
              <v-btn icon size="small" color="primary" @click="openEdit(r)" class="mr-1">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.id)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!records.length"><td colspan="10" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="500">
      <v-card :title="editingId ? '编辑后工序登记' : '新增后工序登记'">
        <v-card-text>
          <v-text-field v-model="form.received_date" label="机加送入日期" type="date" density="compact" />
          <v-text-field v-model="form.product_code" label="产品编号" density="compact" @blur="onProductCodeBlur" />
          <v-text-field v-model="form.product_name" label="产品名称" density="compact" />
          <v-text-field v-model="form.received_qty" label="送入数量" type="number" density="compact" />
          <v-select v-model="form.shift" :items="['A班', 'B班']" label="班组" density="compact" />
          <v-select v-model="form.operator" :items="operatorList" label="操作员" :disabled="!form.shift" density="compact" />
          <v-text-field v-model="form.send_date" label="后工序完成送出日期" type="date" density="compact" />
          <v-text-field v-model="form.send_qty" label="送出数量" type="number" density="compact" />
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
        <v-card-text>确定删除该后工序记录吗？此操作不可撤销。</v-card-text>
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
import { postProcess, users, products } from '../api'
const confirmDialog = ref(false)
const pendingDelete = ref(null)

const initForm = () => ({
  received_date: toLocalDate(new Date()),
  product_code: '', product_name: '',
  received_qty: 0, shift: '', operator: '',
  send_date: '', send_qty: 0, remark: '',
})

const form = ref(initForm())
const records = ref([])
const allOperators = ref([])
const loading = ref(false)
const dialog = ref(false)
const editingId = ref(null)
const filterStartDate = ref('')
const filterEndDate = ref('')
const filterProductCode = ref('')

const operatorList = computed(() => {
  if (!form.value.shift) return allOperators.value.map(u => u.real_name)
  return allOperators.value.filter(u => u.shift === form.value.shift).map(u => u.real_name)
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

function formatDateISO(d) {
  if (!d) return ''
  return toLocalDate(d)
}

async function onProductCodeBlur() {
  if (!form.value.product_code) return
  try {
    const prod = await products.get(form.value.product_code)
    if (prod) {
      form.value.product_name = prod.product_name || ''
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
    received_date: toLocalDate(r.received_date),
    product_code: r.product_code,
    product_name: r.product_name,
    received_qty: r.received_qty,
    shift: r.shift,
    operator: r.operator,
    send_date: toLocalDate(r.send_date),
    send_qty: r.send_qty || 0,
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
      received_qty: parseInt(form.value.received_qty),
      send_qty: parseInt(form.value.send_qty || 0),
      send_date: form.value.send_date || null,
    }
    if (editingId.value) {
      await postProcess.update(editingId.value, payload)
    } else {
      await postProcess.create(payload)
    }
    dialog.value = false
    editingId.value = null
    await loadRecords()
  } catch (e) {
    console.error('保存失败', e)
    console.error('保存失败', e)
  } finally {
    loading.value = false
  }
}

let debounceTimers = {}

async function updateSendQty(record, val) {
  const qty = parseInt(val) || 0
  if (qty < 0) return
  if (debounceTimers[record.id]) clearTimeout(debounceTimers[record.id])
  debounceTimers[record.id] = setTimeout(async () => {
    try {
      await postProcess.updateSend(record.id, { send_qty: qty })
      record.send_qty = qty
    } catch (e) {
      console.error('更新送出数量失败', e)
    }
  }, 500)
}

async function updateSendDate(record, val) {
  if (!val) return
  try {
    await postProcess.updateSend(record.id, {
      send_qty: record.send_qty || 0,
      send_date: val,
    })
    record.send_date = val
  } catch (e) {
    console.error('更新送出日期失败', e)
  }
}

function remove(id) {
  pendingDelete.value = id
  confirmDialog.value = true
}
async function confirmDelete() {
  confirmDialog.value = false
  try {
    await postProcess.delete(pendingDelete.value)
    pendingDelete.value = null
    await loadRecords()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}

function getFilterParams() {
  const params = {}
  if (filterStartDate.value) params.start_date = filterStartDate.value
  if (filterEndDate.value) params.end_date = filterEndDate.value
  if (filterProductCode.value) params.product_code = filterProductCode.value
  return params
}

async function loadRecords() {
  const params = { page: 1, page_size: 200, ...getFilterParams() }
  const res = await postProcess.list(params)
  records.value = res.items || []
}

function exportExcel() {
  postProcess.exportExcel(getFilterParams())
}

onMounted(async () => {
  allOperators.value = await users.list()
})
</script>
