<template>
  <v-card title="系统账户管理">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">新增账号</v-btn>
        </v-col>
      </v-row>
      <v-table density="compact">
        <thead><tr><th>账号</th><th>权限</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.username">
            <td>{{ r.username }}</td><td>{{ ROLE_REVERSE[r.role] || r.role }}</td>
            <td>
              <v-btn icon size="small" color="primary" @click="edit(r)"><v-icon>mdi-pencil</v-icon></v-btn>
              <v-btn icon size="small" color="warning" @click="openPassword(r.username)"><v-icon>mdi-lock-reset</v-icon></v-btn>
              <v-btn icon size="small" color="error" @click="remove(r.username)"><v-icon>mdi-delete</v-icon></v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>

    <v-dialog v-model="dialog" max-width="450">
      <v-card :title="editing ? '编辑账号' : '新增账号'">
        <v-card-text>
          <v-text-field v-model="form.username" label="账号" :disabled="editing" />
          <v-select v-model="form.role" :items="roleOptions" label="权限" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">取消</v-btn>
          <v-btn color="primary" :loading="loading" @click="submit">{{ editing ? '更新' : '保存' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="passwordDialog" max-width="400">
      <v-card title="修改登录密码">
        <v-card-text>
          <p class="mb-2">账号：<strong>{{ passwordTarget }}</strong></p>
          <v-text-field v-model="newPassword" label="新密码" type="password" density="compact" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="passwordDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="passwordLoading" @click="doChangePassword">确认</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card title="确认删除">
        <v-card-text>确定删除该账号吗？此操作不可撤销。</v-card-text>
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
import { users } from '../../api'
const ROLE_MAP = { '普通账户': 'viewer', '管理账户': 'admin' }
const ROLE_REVERSE = Object.fromEntries(Object.entries(ROLE_MAP).map(([k, v]) => [v, k]))
const roleOptions = Object.keys(ROLE_MAP)

const list = ref([])
const form = ref({ username: '', real_name: '', shift: 'A班', role: '普通账户', password: '123456' })
const editing = ref(false)
const originUsername = ref('')
const dialog = ref(false)
const loading = ref(false)
const confirmDialog = ref(false)
const pendingDelete = ref(null)
const passwordDialog = ref(false)
const passwordLoading = ref(false)
const passwordTarget = ref('')
const newPassword = ref('')

async function load() { list.value = await users.list() }
function openAdd() {
  form.value = { username: '', real_name: '', shift: 'A班', role: '普通账户', password: '123456' }
  editing.value = false
  dialog.value = true
}
async function submit() {
  if (!form.value.username?.trim()) { console.error('账号不能为空'); return }
  loading.value = true
  try {
    const payload = { ...form.value, role: ROLE_MAP[form.value.role] || form.value.role }
    if (editing.value) {
      await users.update(originUsername.value, payload)
    } else {
      await users.create(payload)
    }
    dialog.value = false
    form.value = { username: '', real_name: '', shift: 'A班', role: '普通账户', password: '123456' }
    editing.value = false
    await load()
  } catch (e) {
    console.error('操作失败', e)
    console.error('操作失败', e)
  } finally {
    loading.value = false
  }
}
function edit(r) {
  form.value = { ...r, role: ROLE_REVERSE[r.role] || r.role, password: '123456' }
  originUsername.value = r.username
  editing.value = true
  dialog.value = true
}
function remove(username) {
  pendingDelete.value = username
  confirmDialog.value = true
}
function openPassword(username) {
  passwordTarget.value = username
  newPassword.value = ''
  passwordDialog.value = true
}

async function doChangePassword() {
  passwordLoading.value = true
  try {
    await users.changePassword(passwordTarget.value, newPassword.value)
    passwordDialog.value = false
  } catch (e) {
    console.error('密码修改失败', e)
  } finally {
    passwordLoading.value = false
  }
}

async function confirmDelete() {
  confirmDialog.value = false
  try {
    await users.delete(pendingDelete.value)
    pendingDelete.value = null
    await load()
  } catch (e) {
    console.error('删除失败', e)
    console.error('删除失败', e)
  }
}
onMounted(load)
</script>
