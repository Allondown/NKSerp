<template>
  <v-card title="刀具采购供应商管理">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增供应商</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead><tr><th>供应商名称</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.id">
            <td>{{ r.name }}</td>
            <td>
              <v-btn icon size="small" color="primary" @click="openEdit(r)"><v-icon>mdi-pencil</v-icon></v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.id)"><v-icon>mdi-delete</v-icon></v-btn>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="2" class="text-center">暂无数据</td></tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="400">
      <v-card :title="editingId ? '编辑供应商' : '新增供应商'">
        <v-card-text>
          <v-text-field v-model="form.name" label="供应商名称" density="compact" />
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
        <v-card-text>确定删除该供应商吗？</v-card-text>
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
import { suppliers } from '../../api'

const list = ref([])
const form = ref({ name: '' })
const dialog = ref(false)
const editingId = ref(null)
const loading = ref(false)
const confirmDialog = ref(false)
const pendingDelete = ref(null)

async function load() { list.value = await suppliers.list() }

function openAdd() {
  form.value = { name: '' }
  editingId.value = null
  dialog.value = true
}

function openEdit(r) {
  form.value = { name: r.name }
  editingId.value = r.id
  dialog.value = true
}

async function submit() {
  loading.value = true
  try {
    if (editingId.value) {
      await suppliers.update(editingId.value, form.value)
    } else {
      await suppliers.create(form.value)
    }
    dialog.value = false
    editingId.value = null
    await load()
  } catch (e) {
    console.error('操作失败', e)
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
    await suppliers.delete(pendingDelete.value)
    pendingDelete.value = null
    await load()
  } catch (e) {
    console.error('删除失败', e)
  }
}

onMounted(load)
</script>
