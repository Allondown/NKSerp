<template>
  <v-card title="日报列表">
    <v-card-text>
      <v-row>
        <v-col cols="3">
          <v-text-field v-model="filterStartDate" label="起始日期" type="date" density="compact" />
        </v-col>
        <v-col cols="3">
          <v-text-field v-model="filterEndDate" label="结束日期" type="date" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="filterMachine" :items="machineList" label="机器" density="compact" clearable />
        </v-col>
        <v-col cols="1">
          <v-btn variant="outlined" size="small" @click="loadSummary">查询</v-btn>
        </v-col>
        <v-col cols="3" class="text-right">
          <v-btn variant="outlined" @click="exportExcel" class="mr-2">导出Excel</v-btn>
          <v-btn color="success" prepend-icon="mdi-plus" @click="openAdd">新增日报</v-btn>
        </v-col>
      </v-row>

      <v-table density="compact">
        <thead>
          <tr>
            <th rowspan="2">日期</th>
            <th rowspan="2">机器</th>
            <th rowspan="2">产品编号</th>
            <th rowspan="2">产品名称</th>
            <th colspan="8">A班</th>
            <th colspan="8">B班</th>
            <th rowspan="2">计划产量</th>
            <th rowspan="2">完成数量</th>
            <th rowspan="2">操作</th>
          </tr>
          <tr>
            <th>节拍</th><th>生产时间</th><th>理论产量</th><th>实绩</th><th>良品</th><th>不良</th><th>合格率</th><th>损失备注</th>
            <th>节拍</th><th>生产时间</th><th>理论产量</th><th>实绩</th><th>良品</th><th>不良</th><th>合格率</th><th>损失备注</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in displayData" :key="r.production_date + r.machine + r.product_code">
            <td>{{ formatDate(r.production_date) }}</td>
            <td>{{ r.machine }}</td>
            <td>{{ r.product_code }}</td>
            <td>{{ r.product_name }}</td>
            <td>{{ r.a_cycle_sec }}</td>
            <td>{{ r.a_work_time_sec }}</td>
            <td>{{ r.a_theoretical_qty }}</td>
            <td>{{ r.a_actual }}</td>
            <td>{{ r.a_good }}</td>
            <td>{{ r.a_bad }}</td>
            <td>{{ (r.a_qualified_rate * 100).toFixed(1) }}%</td>
            <td>
              <v-text-field
                :model-value="r.a_loss_remark"
                @update:model-value="v => updateLossRemark(r, 'A班', v)"
                density="compact" hide-details
                style="min-width:100px" />
            </td>
            <td>{{ r.b_cycle_sec }}</td>
            <td>{{ r.b_work_time_sec }}</td>
            <td>{{ r.b_theoretical_qty }}</td>
            <td>{{ r.b_actual }}</td>
            <td>{{ r.b_good }}</td>
            <td>{{ r.b_bad }}</td>
            <td>{{ (r.b_qualified_rate * 100).toFixed(1) }}%</td>
            <td>
              <v-text-field
                :model-value="r.b_loss_remark"
                @update:model-value="v => updateLossRemark(r, 'B班', v)"
                density="compact" hide-details
                style="min-width:100px" />
            </td>
            <td>{{ r.plan_qty }}</td>
            <td>{{ r.completion_qty }}</td>
            <td>
              <v-btn icon size="small" color="primary" class="mr-1" @click="openEdit(r)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" color="error" @click="removeSummary(r)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!displayData.length"><td colspan="23" class="text-center">暂无记录</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="700">
      <v-card :title="editingKey ? '编辑生产日报' : '生产日报录入（AB班同时填写）'">
        <v-card-text>
          <v-row>
            <v-col cols="4">
              <v-text-field v-model="form.production_date" label="生产日期" type="date" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-select v-model="form.machine" :items="machineList" label="机器" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-text-field v-model="form.product_code" label="产品编号" density="compact"
                @blur="onProductCodeBlur" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="4">
              <v-text-field v-model="form.product_name" label="产品名称" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-select v-model="form.material_spec" :items="materialList" label="材料规格" density="compact" />
            </v-col>
            <v-col cols="4">
              <v-text-field v-model="form.plan_qty" label="计划产量" type="number" density="compact" />
            </v-col>
          </v-row>

          <v-card variant="outlined" class="pa-2 mb-2">
            <v-row class="text-subtitle-2 font-weight-bold text-center">
              <v-col cols="1">班组</v-col>
              <v-col cols="1">节拍</v-col>
              <v-col cols="1">生产时间</v-col>
              <v-col cols="1">理论产量</v-col>
              <v-col cols="2">实绩</v-col>
              <v-col cols="2">良品</v-col>
              <v-col cols="2">操作工</v-col>
              <v-col cols="2">损失备注</v-col>
            </v-row>
            <v-row class="text-center">
              <v-col cols="1"><strong>A班</strong></v-col>
              <v-col cols="1"><v-text-field v-model.number="form.a_cycle_sec" type="number" density="compact" hide-details /></v-col>
              <v-col cols="1"><v-text-field v-model.number="form.a_work_time_sec" type="number" density="compact" hide-details /></v-col>
              <v-col cols="1"><span class="text-caption">{{ aTheoreticalQty }}</span></v-col>
              <v-col cols="2"><v-text-field v-model.number="form.a_actual_qty" type="number" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-text-field v-model.number="form.a_good_qty" type="number" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-select v-model="form.a_operator" :items="aOperatorList" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-text-field v-model="form.a_loss_remark" density="compact" hide-details /></v-col>
            </v-row>
            <v-row class="text-center">
              <v-col cols="1"><strong>B班</strong></v-col>
              <v-col cols="1"><v-text-field v-model.number="form.b_cycle_sec" type="number" density="compact" hide-details /></v-col>
              <v-col cols="1"><v-text-field v-model.number="form.b_work_time_sec" type="number" density="compact" hide-details /></v-col>
              <v-col cols="1"><span class="text-caption">{{ bTheoreticalQty }}</span></v-col>
              <v-col cols="2"><v-text-field v-model.number="form.b_actual_qty" type="number" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-text-field v-model.number="form.b_good_qty" type="number" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-select v-model="form.b_operator" :items="bOperatorList" density="compact" hide-details /></v-col>
              <v-col cols="2"><v-text-field v-model="form.b_loss_remark" density="compact" hide-details /></v-col>
            </v-row>
          </v-card>

          <v-card variant="outlined" class="pa-3">
            <v-row>
              <v-col cols="4"><strong>A不良：</strong>{{ aBad }}</v-col>
              <v-col cols="4"><strong>B不良：</strong>{{ bBad }}</v-col>
              <v-col cols="4"><strong>合格率：</strong>{{ autoQualifiedRate }}</v-col>
            </v-row>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="success" :loading="loading" @click="submit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>{{ confirmMessage }}</v-card-text>
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
import { production, machines, materials, users, products } from '../../api'
const initForm = () => ({
  production_date: new Date().toISOString().slice(0, 10),
  machine: '', product_name: '', product_code: '', material_spec: '',
  cycle_sec: 0, work_time_sec: 0, plan_qty: 0, loss_time_min: 0,
  a_cycle_sec: 0, a_work_time_sec: 0,
  b_cycle_sec: 0, b_work_time_sec: 0,
  a_actual_qty: 0, a_good_qty: 0, a_operator: '', a_loss_remark: '',
  b_actual_qty: 0, b_good_qty: 0, b_operator: '', b_loss_remark: '',
})

const form = ref(initForm())
const machineList = ref([])
const materialList = ref([])
const allOperators = ref([])
const summaryData = ref([])
const filterStartDate = ref('')
const filterEndDate = ref('')
const filterMachine = ref('')
const loading = ref(false)
const dialog = ref(false)
const editingKey = ref(null)
const confirmDialog = ref(false)
const confirmMessage = ref('')
const pendingDelete = ref(null)

const aOperatorList = computed(() =>
  allOperators.value.filter(u => u.shift === 'A班').map(u => u.real_name)
)

const bOperatorList = computed(() =>
  allOperators.value.filter(u => u.shift === 'B班').map(u => u.real_name)
)

const aTheoreticalQty = computed(() => {
  if (form.value.a_work_time_sec && form.value.a_cycle_sec) {
    return (form.value.a_work_time_sec / form.value.a_cycle_sec).toFixed(2)
  }
  return '0'
})

const bTheoreticalQty = computed(() => {
  if (form.value.b_work_time_sec && form.value.b_cycle_sec) {
    return (form.value.b_work_time_sec / form.value.b_cycle_sec).toFixed(2)
  }
  return '0'
})

const aBad = computed(() =>
  Math.max(0, parseInt(form.value.a_actual_qty || 0) - parseInt(form.value.a_good_qty || 0))
)

const bBad = computed(() =>
  Math.max(0, parseInt(form.value.b_actual_qty || 0) - parseInt(form.value.b_good_qty || 0))
)

const autoQualifiedRate = computed(() => {
  const total = parseInt(form.value.a_actual_qty || 0) + parseInt(form.value.b_actual_qty || 0)
  const good = parseInt(form.value.a_good_qty || 0) + parseInt(form.value.b_good_qty || 0)
  if (total > 0) return ((good / total) * 100).toFixed(1) + '%'
  return '0%'
})

const displayData = computed(() => {
  const sorted = [...summaryData.value].sort((a, b) =>
    new Date(a.production_date) - new Date(b.production_date)
  )
  let runningTotal = 0
  return sorted.map(r => {
    runningTotal += (r.a_good || 0) + (r.b_good || 0)
    return { ...r, completion_qty: runningTotal }
  })
})

function openAdd() {
  form.value = initForm()
  editingKey.value = null
  dialog.value = true
}

async function onProductCodeBlur() {
  if (!form.value.product_code) return
  try {
    const prod = await products.get(form.value.product_code)
    if (prod) {
      form.value.product_name = prod.product_name || ''
      form.value.material_spec = prod.material_spec || ''
      form.value.cycle_sec = prod.cycle_sec || 0
      form.value.work_time_sec = prod.work_time_sec || 0
      // 默认 A/B 班使用相同节拍，生产时间各半
      if (!form.value.a_cycle_sec) form.value.a_cycle_sec = prod.cycle_sec || 0
      if (!form.value.b_cycle_sec) form.value.b_cycle_sec = prod.cycle_sec || 0
      if (!form.value.a_work_time_sec) form.value.a_work_time_sec = Math.round((prod.work_time_sec || 0) / 2)
      if (!form.value.b_work_time_sec) form.value.b_work_time_sec = Math.round((prod.work_time_sec || 0) / 2)
      if (!form.value.plan_qty || form.value.plan_qty === 0) form.value.plan_qty = prod.monthly_plan || 0
      if (prod.loss_remark) {
        form.value.a_loss_remark = prod.loss_remark
        form.value.b_loss_remark = prod.loss_remark
      }
    }
    if (!form.value.a_loss_remark && !form.value.b_loss_remark) {
      try {
        const last = await production.lastRecord(form.value.product_code)
        if (last) {
          if (last.a_loss_remark && !form.value.a_loss_remark) form.value.a_loss_remark = last.a_loss_remark
          if (last.b_loss_remark && !form.value.b_loss_remark) form.value.b_loss_remark = last.b_loss_remark
        }
      } catch (_) { /* ignore */ }
    }
  } catch (e) {
    // ignore
  }
}

async function openEdit(r) {
  editingKey.value = { date: r.production_date, machine: r.machine, product_code: r.product_code }
  try {
    const res = await production.list({
      start_date: r.production_date,
      end_date: r.production_date,
      machine: r.machine,
      product_code: r.product_code,
      page: 1, page_size: 10,
    })
    const items = res.items || []
    const aRec = items.find(i => i.shift === 'A班')
    const bRec = items.find(i => i.shift === 'B班')
    form.value = {
      production_date: r.production_date,
      machine: r.machine,
      product_name: r.product_name,
      product_code: r.product_code,
      material_spec: aRec?.material_spec || bRec?.material_spec || '',
      cycle_sec: r.cycle_sec,
      work_time_sec: r.work_time_sec,
      plan_qty: r.plan_qty,
      loss_time_min: r.loss_time_min || 0,
      a_cycle_sec: aRec?.cycle_sec || r.cycle_sec || 0,
      a_work_time_sec: aRec?.work_time_sec || 0,
      b_cycle_sec: bRec?.cycle_sec || r.cycle_sec || 0,
      b_work_time_sec: bRec?.work_time_sec || 0,
      a_actual_qty: aRec?.actual_qty || 0,
      a_good_qty: aRec?.good_qty || 0,
      a_operator: aRec?.operator || '',
      a_loss_remark: aRec?.loss_remark || '',
      b_actual_qty: bRec?.actual_qty || 0,
      b_good_qty: bRec?.good_qty || 0,
      b_operator: bRec?.operator || '',
      b_loss_remark: bRec?.loss_remark || '',
    }
    dialog.value = true
  } catch (e) {
    console.error('加载编辑数据失败', e)
  }
}

async function submit() {
  loading.value = true
  try {
    const payload = {
      ...form.value,
      cycle_sec: parseFloat(form.value.cycle_sec),
      work_time_sec: parseFloat(form.value.work_time_sec),
      a_cycle_sec: parseFloat(form.value.a_cycle_sec || 0),
      a_work_time_sec: parseFloat(form.value.a_work_time_sec || 0),
      b_cycle_sec: parseFloat(form.value.b_cycle_sec || 0),
      b_work_time_sec: parseFloat(form.value.b_work_time_sec || 0),
      loss_time_min: parseInt(form.value.loss_time_min || 0),
      a_actual_qty: parseInt(form.value.a_actual_qty || 0),
      a_good_qty: parseInt(form.value.a_good_qty || 0),
      b_actual_qty: parseInt(form.value.b_actual_qty || 0),
      b_good_qty: parseInt(form.value.b_good_qty || 0),
      plan_qty: parseInt(form.value.plan_qty || 0),
    }
    if (editingKey.value) {
      await production.updateCombined({
        ...payload,
        original_date: editingKey.value.date,
        original_machine: editingKey.value.machine,
        original_product_code: editingKey.value.product_code,
      })
    } else {
      await production.combinedCreate(payload)
    }
    form.value = initForm()
    editingKey.value = null
    dialog.value = false
    await loadSummary()
  } catch (e) {
    console.error('保存失败', e)
  } finally {
    loading.value = false
  }
}

function removeSummary(r) {
  pendingDelete.value = r
  confirmMessage.value = `确定删除 ${r.production_date} ${r.machine} ${r.product_name} 的日报？`
  confirmDialog.value = true
}
async function confirmDelete() {
  const r = pendingDelete.value
  confirmDialog.value = false
  if (!r) return
  try {
    const params = {
      start_date: r.production_date,
      end_date: r.production_date,
      machine: r.machine,
      product_code: r.product_code,
    }
    const res = await production.list({ ...params, page: 1, page_size: 50 })
    for (const rec of res.items || []) {
      await production.delete(rec.id)
    }
    pendingDelete.value = null
    await loadSummary()
  } catch (e) {
    console.error('删除失败', e)
  }
}

let debounceTimers = {}

async function updateLossRemark(r, shift, val) {
  const key = r.production_date + r.machine + r.product_code + shift
  if (debounceTimers[key]) clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    try {
      await production.updateLossRemark({
        production_date: r.production_date,
        machine: r.machine,
        product_code: r.product_code,
        shift: shift,
        loss_remark: val,
      })
      if (shift === 'A班') r.a_loss_remark = val
      else r.b_loss_remark = val
    } catch (e) {
      console.error('更新损失备注失败', e.response?.data || e.message)
    }
  }, 500)
}

function formatDate(d) {
  if (!d) return '-'
  const dt = new Date(d)
  return dt.toLocaleDateString('zh-CN')
}

async function loadSummary() {
  const params = {}
  if (filterStartDate.value) params.start_date = filterStartDate.value
  if (filterEndDate.value) params.end_date = filterEndDate.value
  if (filterMachine.value) params.machine = filterMachine.value
  summaryData.value = await production.summary(params)
}

function getFilterParams() {
  const params = {}
  if (filterStartDate.value) params.start_date = filterStartDate.value
  if (filterEndDate.value) params.end_date = filterEndDate.value
  if (filterMachine.value) params.machine = filterMachine.value
  return params
}

function exportExcel() {
  production.exportExcel(getFilterParams())
}

onMounted(async () => {
  machineList.value = (await machines.list()).map(m => m.machine_name)
  materialList.value = (await materials.list()).map(m => m.material_spec)
  allOperators.value = await users.list()
})
</script>
