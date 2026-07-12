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
            <th>累计送出</th><th>未完成数量</th><th>操作</th>
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
            <td>{{ r.total_send_qty || 0 }}</td>
            <td>{{ Math.max(0, (r.received_qty || 0) - (r.total_send_qty || 0)) }}</td>
            <td>
              <v-btn icon size="small" color="primary" @click="openEdit(r)" class="mr-1">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.id)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!records.length"><td colspan="9" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="550">
      <v-card :title="editingId ? '编辑后工序登记' : '新增后工序登记'">
        <v-card-text>
          <v-text-field v-model="form.received_date" label="机加送入日期" type="date" density="compact" />
          <v-text-field v-model="form.product_code" label="产品编号" density="compact" @blur="onProductCodeBlur" />
          <v-text-field v-model="form.product_name" label="产品名称" density="compact" />
          <v-text-field v-model="form.received_qty" label="送入数量" type="number" density="compact" />
          <v-select v-model="form.shift" :items="['A班', 'B班']" label="班组" density="compact" />
          <v-select v-model="form.operator" :items="filteredOperators" label="操作员" :disabled="!form.shift" density="compact" />

          <v-divider class="my-2" />
          <div class="text-subtitle-2 mb-2">送出记录</div>
          <div v-for="(send, idx) in form.sends" :key="idx" class="d-flex align-start ga-2 mb-1">
            <v-text-field v-model="send.send_date" label="送出日期" type="date"
              density="compact" style="max-width:160px"
              :rules="[v => !!v || '送出日期不能为空']" />
            <v-text-field v-model="send.send_qty" label="送出数量" type="number"
              density="compact" style="max-width:140px"
              :rules="sendQtyRules(idx)" />
            <v-btn icon size="small" color="error" variant="text" class="mt-2" @click="form.sends.splice(idx, 1)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
          <v-btn size="small" variant="outlined" color="primary" prepend-icon="mdi-plus"
            @click="form.sends.push({send_date: '', send_qty: null})">
            添加送出记录
          </v-btn>

          <v-divider class="my-2" />
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
import { postProcess, operators, products } from '../api'
const confirmDialog = ref(false)
const pendingDelete = ref(null)

const initForm = () => ({
  received_date: toLocalDate(new Date()),
  product_code: '', product_name: '',
  received_qty: null, shift: '', operator: '',
  sends: [],
  remark: '',
})

const form = ref(initForm())
const records = ref([])
const operatorList = ref([])
const loading = ref(false)
const dialog = ref(false)
const editingId = ref(null)
const filterStartDate = ref(toLocalDate(new Date()))
const filterEndDate = ref(toLocalDate(new Date()))
const filterProductCode = ref('')

const filteredOperators = computed(() => {
  if (!form.value.shift) return operatorList.value.map(o => o.name)
  return operatorList.value.filter(o => o.shift === form.value.shift).map(o => o.name)
})

function sendQtyRules(idx) {
  return [
    v => (v !== null && v !== '' && v !== undefined) || '送出数量不能为空',
    v => Number(v) >= 0 || '送出数量不能小于0',
    v => {
      const received = Number(form.value.received_qty) || 0
      let total = 0
      form.value.sends.forEach((s, i) => {
        total += Number(i === idx ? v : s.send_qty) || 0
      })
      return total <= received || `累计送出(${total})不能大于送入数量(${received})`
    },
  ]
}

function toLocalDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
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
    sends: (r.sends || []).map(s => ({
      send_date: toLocalDate(s.send_date),
      send_qty: s.send_qty || 0,
    })),
    remark: r.remark || '',
  }
  editingId.value = r.id
  dialog.value = true
}

async function submit() {
  loading.value = true
  try {
    const payload = {
      received_date: form.value.received_date,
      product_code: form.value.product_code,
      product_name: form.value.product_name,
      received_qty: parseInt(form.value.received_qty) || 0,
      shift: form.value.shift,
      operator: form.value.operator,
      sends: form.value.sends
        .filter(s => s.send_date || (Number(s.send_qty) > 0))
        .map(s => ({
          send_date: s.send_date || null,
          send_qty: Math.max(0, parseInt(s.send_qty) || 0),
        })),
      remark: form.value.remark || '',
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
    await postProcess.delete(pendingDelete.value)
    pendingDelete.value = null
    await loadRecords()
  } catch (e) {
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
  operatorList.value = await operators.list()
})
</script>
