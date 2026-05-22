<template>
  <v-card title="产品主数据管理">
    <v-card-text>
      <v-row>
        <v-col cols="2">
          <v-select v-model="currentMonth" :items="monthOptions" label="月份" density="compact" clearable />
        </v-col>
        <v-col cols="2">
          <v-text-field v-model="filterProductCode" label="产品编号" density="compact" clearable hide-details @keyup.enter="load" />
        </v-col>
        <v-col cols="1">
          <v-btn color="primary" variant="outlined" size="small" @click="load">查询</v-btn>
        </v-col>
        <v-col cols="4" />
        <v-col cols="3" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增产品</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead><tr><th>产品编号</th><th>产品名称</th><th>材料规格</th><th>节拍(秒/件)</th><th>生产时间(秒)</th><th>计划产量</th><th>月份</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.product_code + r.month">
            <td>{{ r.product_code }}</td><td>{{ r.product_name }}</td>
            <td>{{ r.material_spec }}</td><td>{{ r.cycle_sec }}</td><td>{{ r.work_time_sec }}</td><td>{{ r.monthly_plan }}</td><td>{{ r.month }}</td>
            <td>
              <v-btn icon size="small" color="primary" @click="openEdit(r)" class="mr-1">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.product_code, r.month)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="450">
      <v-card :title="editMode ? '编辑产品' : '新增产品'">
        <v-card-text>
          <v-text-field v-model="form.product_code" label="产品编号" />
          <v-text-field v-model="form.product_name" label="产品名称" />
          <v-text-field v-model="form.material_spec" label="材料规格" />
          <v-text-field v-model="form.cycle_sec" label="节拍（秒/件）" type="number" />
          <v-text-field v-model="form.work_time_sec" label="生产时间（秒）" type="number" />
          <v-text-field v-model="form.monthly_plan" label="当月计划产量" type="number" />
          <v-select v-model="form.month" :items="monthOptions" label="月份" density="compact" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="primary" @click="submit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>确定删除该产品主数据吗？此操作不可撤销。</v-card-text>
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
import { ref, onMounted } from 'vue'
import { products } from '../../api'
const now = new Date()
const currentMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
const monthOptions = []
for (let y = 2025; y <= 2027; y++) {
  for (let m = 1; m <= 12; m++) {
    monthOptions.push(`${y}-${String(m).padStart(2, '0')}`)
  }
}
const filterProductCode = ref('')
const list = ref([])
const form = ref({ product_code: '', product_name: '', material_spec: '', monthly_plan: 0, cycle_sec: 0, work_time_sec: 0, loss_remark: '', month: '' })
const dialog = ref(false)
const editMode = ref(false)
const originalCode = ref('')
const originalMonth = ref('')
const confirmDialog = ref(false)
const pendingDelete = ref({ code: '', month: '' })

async function load() {
  if (!currentMonth.value && !filterProductCode.value) {
    list.value = []
    return
  }
  list.value = await products.list(currentMonth.value, filterProductCode.value)
}
function openAdd() {
  editMode.value = false
  form.value = { product_code: '', product_name: '', material_spec: '', monthly_plan: 0, cycle_sec: 0, work_time_sec: 0, loss_remark: '', month: currentMonth.value }
  dialog.value = true
}
function openEdit(r) {
  editMode.value = true
  originalCode.value = r.product_code
  originalMonth.value = r.month
  form.value = {
    product_code: r.product_code,
    product_name: r.product_name,
    material_spec: r.material_spec,
    monthly_plan: r.monthly_plan,
    cycle_sec: r.cycle_sec,
    work_time_sec: r.work_time_sec,
    loss_remark: r.loss_remark || '',
    month: r.month,
  }
  dialog.value = true
}
async function submit() {
  if (!form.value.product_code) return
  try {
    if (editMode.value) {
      await products.update({ ...form.value, month: form.value.month }, originalCode.value, originalMonth.value)
    } else {
      await products.create({ ...form.value, month: form.value.month })
    }
    dialog.value = false
    await load()
  } catch (e) {
    console.error('保存失败', e)
    console.error('保存失败', e)
  }
}
function remove(code, month) {
  pendingDelete.value = { code, month }
  confirmDialog.value = true
}
async function confirmDelete() {
  confirmDialog.value = false
  try {
    await products.delete(pendingDelete.value.code, pendingDelete.value.month)
    pendingDelete.value = { code: '', month: '' }
    await load()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}

onMounted(load)
</script>
