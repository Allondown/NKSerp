<template>
  <v-card title="材料规格管理">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增材料</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead><tr><th>材料规格</th><th>单位</th><th>标准单价</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.material_spec">
            <td>{{ r.material_spec }}</td><td>{{ r.unit }}</td>
            <td>{{ r.standard_price }}</td>
            <td>
              <v-btn icon size="small" @click="edit(r)"><v-icon>mdi-pencil</v-icon></v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.material_spec)"><v-icon>mdi-delete</v-icon></v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="450">
      <v-card :title="editing ? '编辑材料' : '新增材料'">
        <v-card-text>
          <v-text-field v-model="form.material_spec" label="材料规格" />
          <v-text-field v-model="form.standard_price" label="标准单价（元/kg）" type="number" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="primary" @click="submit">{{ editing ? '更新' : '保存' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>确定删除该材料吗？此操作不可撤销。</v-card-text>
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
import { materials } from '../../api'
const list = ref([])
const form = ref({ material_spec: '', unit: 'kg', standard_price: 0 })
const editing = ref(false)
const originSpec = ref('')
const dialog = ref(false)
const confirmDialog = ref(false)
const pendingDelete = ref(null)

async function load() { list.value = await materials.list() }
function openAdd() {
  form.value = { material_spec: '', unit: 'kg', standard_price: 0 }
  editing.value = false
  dialog.value = true
}
async function submit() {
  try {
    if (editing.value) {
      await materials.update(originSpec.value, form.value)
    } else {
      await materials.create(form.value)
    }
    dialog.value = false
    form.value = { material_spec: '', unit: 'kg', standard_price: 0 }
    editing.value = false
    await load()
  } catch (e) {
    console.error('操作失败', e)
    console.error('操作失败', e)
  }
}
function edit(r) {
  form.value = { ...r }
  originSpec.value = r.material_spec
  editing.value = true
  dialog.value = true
}
function remove(spec) {
  pendingDelete.value = spec
  confirmDialog.value = true
}
async function confirmDelete() {
  confirmDialog.value = false
  try {
    await materials.delete(pendingDelete.value)
    pendingDelete.value = null
    await load()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}
onMounted(load)
</script>
