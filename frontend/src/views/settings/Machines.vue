<template>
  <v-card title="机器管理">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">新增机器</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead><tr><th>机器名称</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.machine_name">
            <td>{{ r.machine_name }}</td>
            <td>
              <v-btn icon size="small" color="error" @click="remove(r.machine_name)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="400">
      <v-card title="新增机器">
        <v-card-text>
          <v-text-field v-model="machineName" label="机器名称" />
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
        <v-card-text>确定删除该机器吗？此操作不可撤销。</v-card-text>
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
import { machines } from '../../api'
const list = ref([])
const machineName = ref('')
const dialog = ref(false)
const confirmDialog = ref(false)
const pendingDelete = ref(null)

async function load() { list.value = await machines.list() }
async function submit() {
  if (!machineName.value) return
  try {
    await machines.create({ machine_name: machineName.value })
    machineName.value = ''
    dialog.value = false
    await load()
  } catch (e) {
    console.error('操作失败', e)
    console.error('操作失败', e)
  }
}
function remove(name) {
  pendingDelete.value = name
  confirmDialog.value = true
}
async function confirmDelete() {
  confirmDialog.value = false
  try {
    await machines.delete(pendingDelete.value)
    pendingDelete.value = null
    await load()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}
onMounted(load)
</script>
