<template>
  <v-card title="采购记录">
    <v-card-text>
      <v-row>
        <v-col cols="6">
          <v-text-field v-model="searchSpec" label="按材料筛选" density="compact" />
        </v-col>
        <v-col cols="6" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">新增采购</v-btn>
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
      <v-card title="采购入库登记">
        <v-card-text>
          <v-text-field v-model="form.arrival_date" label="到货时间" type="date" density="compact" />
          <v-select v-model="form.machine" :items="machineList" label="加工机器" density="compact" />
          <v-text-field v-model="form.product" label="产品名称" density="compact" />
          <v-text-field v-model="form.product_code" label="产品编号" density="compact" />
          <v-select v-model="form.material_spec" :items="materialList" label="材料规格" density="compact" />
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
import { purchases, machines, materials } from '../../api'
const initForm = () => ({
  arrival_date: new Date().toISOString().slice(0, 10),
  machine: '', product: '', product_code: '', material_spec: '',
  quantity_rods: 0, weight_kg: 0, unit_price: 0, remark: '',
})

const form = ref(initForm())
const machineList = ref([])
const materialList = ref([])
const records = ref([])
const searchSpec = ref('')
const loading = ref(false)
const dialog = ref(false)
const confirmDialog = ref(false)
const pendingDelete = ref(null)

const autoTotalPrice = computed(() =>
  (parseFloat(form.value.weight_kg || 0) * parseFloat(form.value.unit_price || 0)).toFixed(2)
)

const filteredRecords = computed(() => {
  if (!searchSpec.value) return []
  return records.value.filter(r => r.material_spec.includes(searchSpec.value))
})

async function submit() {
  loading.value = true
  try {
    await purchases.create({
      ...form.value,
      weight_kg: parseFloat(form.value.weight_kg),
      unit_price: parseFloat(form.value.unit_price),
      quantity_rods: parseFloat(form.value.quantity_rods),
    })
    form.value = initForm()
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
    await purchases.delete(pendingDelete.value)
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
  const res = await purchases.list({ page: 1, page_size: 100 })
  records.value = res.items
}

onMounted(async () => {
  machineList.value = (await machines.list()).map(m => m.machine_name)
  materialList.value = (await materials.list()).map(m => m.material_spec)
  await loadRecords()
})
</script>
