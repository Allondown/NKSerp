<template>
  <v-card title="后工序统计报表">
    <v-card-text>
      <v-row>
        <v-col cols="3"><v-select v-model="year" :items="years" label="年份" density="compact" /></v-col>
        <v-col cols="3"><v-btn color="primary" @click="loadData">查询</v-btn></v-col>
        <v-col cols="6"><v-btn color="success" variant="outlined" @click="exportExcel">导出Excel</v-btn></v-col>
      </v-row>

      <v-row>
        <v-col cols="6">
          <v-card variant="outlined" title="机加送入统计">
            <v-table density="compact">
              <thead>
                <tr><th>月份</th><th>未完成数量</th></tr>
              </thead>
              <tbody>
                <tr v-for="(r, i) in uncompleted" :key="'u'+i">
                  <td>{{ r.year }}-{{ String(r.month).padStart(2, '0') }}</td>
                  <td>{{ r.uncompleted }}</td>
                </tr>
                <tr v-if="uncompleted.length" class="font-weight-bold">
                  <td>合计</td>
                  <td>{{ totalUncompleted }}</td>
                </tr>
                <tr v-if="!uncompleted.length"><td colspan="2" class="text-center">暂无数据</td></tr>
              </tbody>
            </v-table>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card variant="outlined" title="后工序送出统计">
            <v-table density="compact">
              <thead>
                <tr><th>月份</th><th>送出数量</th></tr>
              </thead>
              <tbody>
                <tr v-for="(r, i) in sendSummary" :key="'s'+i">
                  <td>{{ r.year }}-{{ String(r.month).padStart(2, '0') }}</td>
                  <td>{{ r.total_send_qty }}</td>
                </tr>
                <tr v-if="sendSummary.length" class="font-weight-bold">
                  <td>合计</td>
                  <td>{{ totalSend }}</td>
                </tr>
                <tr v-if="!sendSummary.length"><td colspan="2" class="text-center">暂无数据</td></tr>
              </tbody>
            </v-table>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { reports } from '../../api'

const now = new Date()
const year = ref(now.getFullYear())
const years = [2025, 2026, 2027]
const uncompleted = ref([])
const sendSummary = ref([])

const totalUncompleted = computed(() =>
  uncompleted.value.reduce((sum, r) => sum + r.uncompleted, 0)
)

const totalSend = computed(() =>
  sendSummary.value.reduce((sum, r) => sum + r.total_send_qty, 0)
)

async function loadData() {
  const data = await reports.postProcessSummary(year.value)
  uncompleted.value = data.uncompleted || []
  sendSummary.value = data.send_summary || []
}

function exportExcel() {
  reports.export('post-process-summary', year.value, 1)
}

onMounted(loadData)
</script>
