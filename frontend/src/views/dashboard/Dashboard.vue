<template>
  <v-card title="仪表盘">
    <v-card-text>
      <!-- 筛选条件 -->
      <v-row>
        <v-col cols="2">
          <v-select v-model="year" :items="years" label="年份" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-select v-model="month" :items="monthOpts" label="月份" density="compact" clearable />
        </v-col>
        <v-col cols="3">
          <v-select v-model="reportType" :items="reportTypeOpts" label="报表类别" density="compact" />
        </v-col>
        <v-col cols="2">
          <v-btn color="primary" @click="loadAll">查询</v-btn>
        </v-col>
      </v-row>

      <!-- 加载中 -->
      <v-row v-if="loading">
        <v-col cols="12" class="text-center py-8">
          <v-progress-circular indeterminate color="primary" />
          <div class="text-caption mt-2">加载中...</div>
        </v-col>
      </v-row>

      <template v-if="!loading">
        <!-- KPI 卡片 -->
        <v-row v-if="kpiCards.length">
          <v-col v-for="card in kpiCards" :key="card.title" cols="12" sm="6" md="3">
            <v-card :color="card.color" variant="tonal">
              <v-card-text class="text-center pa-4">
                <v-icon :color="card.color" size="32">{{ card.icon }}</v-icon>
                <div class="text-h5 font-weight-bold mt-1">{{ card.value }}</div>
                <div class="text-caption text-medium-emphasis">{{ card.title }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 图表区域 -->
        <v-row v-if="chartPanels.length">
          <v-col v-for="(panel, idx) in chartPanels" :key="idx" cols="12" :md="panel.span || 6">
            <v-card :title="panel.title" variant="outlined">
              <v-card-text>
                <div :style="{ height: panel.height || '300px', position: 'relative' }">
                  <Bar v-if="panel.type === 'bar'" :data="panel.data" :options="barOptions" />
                  <Doughnut v-else-if="panel.type === 'doughnut'" :data="panel.data" :options="doughnutOptions" />
                  <Pie v-else-if="panel.type === 'pie'" :data="panel.data" :options="doughnutOptions" />
                  <Line v-else-if="panel.type === 'line'" :data="panel.data" :options="barOptions" />
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 表格 -->
        <v-row v-if="tableHeaders.length && tableRows.length">
          <v-col cols="12">
            <v-card variant="outlined">
              <v-card-text>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th v-for="h in tableHeaders" :key="h">{{ h }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(r, i) in tableRows" :key="i">
                      <td v-for="h in tableHeaders" :key="h">{{ r[h] }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 无数据 -->
        <v-row v-if="!kpiCards.length && !chartPanels.length && !loading">
          <v-col cols="12" class="text-center py-8">
            <v-icon size="48" color="grey-lighten-1">mdi-chart-box-outline</v-icon>
            <div class="text-caption text-medium-emphasis mt-2">请选择条件后点击查询</div>
          </v-col>
        </v-row>
      </template>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bar, Doughnut, Pie, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale,
  ArcElement, PointElement, LineElement, Filler,
} from 'chart.js'
import { reports } from '../../api'

// 自定义插件：柱状图顶部显示数值
const barValuePlugin = {
  id: 'barValueLabels',
  afterDatasetsDraw(chart) {
    const { ctx } = chart
    ctx.save()
    const barCount = chart.data.labels?.length || 1
    const dsCount = chart.data.datasets?.length || 1
    chart.data.datasets.forEach((dataset, dsIdx) => {
      const meta = chart.getDatasetMeta(dsIdx)
      if (meta.hidden) return
      meta.data.forEach((bar, idx) => {
        const value = dataset.data[idx]
        if (value == null || Number(value) === 0) return
        const n = Number(value)
        const isMoney = n >= 100 && chart.data.datasets[dsIdx]?.label?.includes('金额')
        let display
        if (isMoney) {
          display = '¥' + n.toLocaleString('zh-CN')
        } else if (n >= 1000) {
          display = n.toLocaleString('zh-CN')
        } else {
          display = Number.isInteger(n) ? String(n) : n.toFixed(1)
        }
        ctx.font = `bold ${barCount > 8 ? 10 : 11}px sans-serif`
        ctx.fillStyle = '#444'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'bottom'
        if (dsCount >= 3) {
          ctx.save()
          ctx.translate(bar.x, bar.y - 4)
          ctx.rotate(-45 * Math.PI / 180)
          ctx.fillText(display, 0, 0)
          ctx.restore()
        } else {
          ctx.fillText(display, bar.x, bar.y - 4)
        }
      })
    })
    ctx.restore()
  },
}

// 自定义插件：饼图/环形图显示百分比
const doughnutPctPlugin = {
  id: 'doughnutPctLabels',
  afterDatasetsDraw(chart) {
    const { ctx, data } = chart
    ctx.save()
    const dataset = data.datasets[0]
    const meta = chart.getDatasetMeta(0)
    if (!meta || !meta.data) { ctx.restore(); return }
    const total = dataset.data.reduce((a, b) => Number(a) + Number(b), 0)
    if (total === 0) { ctx.restore(); return }
    meta.data.forEach((arc, idx) => {
      const value = Number(dataset.data[idx])
      if (value === 0) return
      const pct = ((value / total) * 100).toFixed(1) + '%'
      const angle = (arc.startAngle + arc.endAngle) / 2
      const radius = (arc.outerRadius + arc.innerRadius) / 2
      const x = arc.x + Math.cos(angle) * radius
      const y = arc.y + Math.sin(angle) * radius
      ctx.font = 'bold 12px sans-serif'
      ctx.fillStyle = '#fff'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(pct, x, y)
    })
    ctx.restore()
  },
}

ChartJS.register(
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale,
  ArcElement, PointElement, LineElement, Filler,
  barValuePlugin, doughnutPctPlugin,
)

// --- 状态 ---
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const reportType = ref('cost')
const loading = ref(false)

const years = [2025, 2026, 2027]
const monthOpts = Array.from({ length: 12 }, (_, i) => ({ title: `${i + 1}月`, value: i + 1 }))
const reportTypeOpts = [
  { title: '成本报表', value: 'cost' },
  { title: '刀具采购报表', value: 'tool-purchase' },
  { title: '生产数据统计报表', value: 'production' },
  { title: '后工序报表', value: 'post-process' },
]

const kpiCards = ref([])
const chartPanels = ref([])
const tableHeaders = ref([])
const tableRows = ref([])

// --- 图表通用配置 ---
const COLORS = [
  '#1976D2', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
  '#009688', '#FF5722', '#3F51B5', '#8BC34A', '#FFC107',
  '#00BCD4', '#E91E63', '#607D8B', '#CDDC39', '#795548',
]

const barOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}` } },
  },
  scales: {
    y: { beginAtZero: true },
  },
}))

const doughnutOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'right' },
  },
}))

// --- 格式化 ---
const fmtMoney = (v) => '¥' + (Number(v) || 0).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
const fmtPct = (v) => ((Number(v) || 0) * 100).toFixed(1) + '%'

// --- 数据加载 ---
function makeColorArray(len) {
  return Array.from({ length: len }, (_, i) => COLORS[i % COLORS.length])
}

async function loadCost() {
  const data = await reports.cost(year.value, month.value)
  const details = data.details || []
  const s = data.summary || {}

  kpiCards.value = [
    { title: '本月采购额', value: fmtMoney(s.total_purchase_amount), icon: 'mdi-cart', color: 'primary' },
    { title: '本月领用成本', value: fmtMoney(s.total_issue_cost), icon: 'mdi-cart-arrow-up', color: 'warning' },
    { title: '期末库存金额', value: fmtMoney(s.total_inventory_amount), icon: 'mdi-warehouse', color: 'success' },
    { title: '涉及材料', value: `${details.length} 种`, icon: 'mdi-shape', color: 'info' },
  ]

  const labels = details.map(d => d.material_spec)
  chartPanels.value = [
    {
      type: 'bar', title: '各材料采购金额 vs 领用成本',
      data: {
        labels,
        datasets: [
          { label: '采购金额', data: details.map(d => d.purchase_amount), backgroundColor: COLORS[0] },
          { label: '领用成本', data: details.map(d => d.issue_cost), backgroundColor: COLORS[3] },
        ],
      },
    },
  ]

  if (details.length > 1) {
    chartPanels.value.push({
      type: 'doughnut', title: '采购金额占比',
      data: {
        labels,
        datasets: [{ data: details.map(d => d.purchase_amount), backgroundColor: makeColorArray(details.length) }],
      },
    })
  }

  tableHeaders.value = ['材料规格', '期初数量', '期初金额', '采购数量', '采购金额', '领用数量', '领用成本', '期末数量', '期末金额']
  tableRows.value = details
}

async function loadToolPurchase() {
  const [costData, supplierData] = await Promise.all([
    reports.toolPurchaseCost(year.value, month.value),
    reports.toolSupplierCost(year.value, month.value),
  ])
  const items = costData.items || []
  const sItems = supplierData.items || []

  kpiCards.value = [
    { title: '刀具采购总成本', value: fmtMoney(costData.total_cost), icon: 'mdi-wrench', color: 'primary' },
    { title: '采购总笔数', value: `${items.length} 笔`, icon: 'mdi-note-text', color: 'info' },
    { title: '涉及供应商', value: `${sItems.length} 家`, icon: 'mdi-store', color: 'success' },
    { title: '供应商总金额', value: fmtMoney(supplierData.grand_total), icon: 'mdi-cash', color: 'accent' },
  ]

  chartPanels.value = []
  if (sItems.length > 0) {
    chartPanels.value.push({
      type: 'bar', title: '各供应商采购金额',
      data: {
        labels: sItems.map(d => d.supplier),
        datasets: [{
          label: '采购金额', data: sItems.map(d => d.total_cost),
          backgroundColor: makeColorArray(sItems.length),
        }],
      },
    })
    if (sItems.length > 1) {
      chartPanels.value.push({
        type: 'doughnut', title: '供应商采购金额占比',
        data: {
          labels: sItems.map(d => d.supplier),
          datasets: [{ data: sItems.map(d => d.total_cost), backgroundColor: makeColorArray(sItems.length) }],
        },
      })
    }
  }

  tableHeaders.value = ['品名', '规格', '数量', '单价', '总金额', '加工产品', '供应商']
  tableRows.value = items.map(r => ({
    '品名': r.name, '规格': r.spec, '数量': r.quantity,
    '单价': r.unit_price, '总金额': r.total_amount,
    '加工产品': r.processed_product, '供应商': r.supplier,
  }))
}

async function loadProduction() {
  const [prodData, teamData] = await Promise.all([
    reports.productAchieve(year.value, month.value),
    reports.teamAchieve(year.value, month.value),
  ])

  // 按产品聚合达成率和合格率
  const prodAgg = {}
  for (const r of prodData || []) {
    const key = r.product
    if (!prodAgg[key]) prodAgg[key] = { theo: 0, actual: 0, good: 0, count: 0, qRateSum: 0 }
    prodAgg[key].theo += r.theoretical_qty
    prodAgg[key].actual += r.actual_qty
    prodAgg[key].good += r.good_qty
    prodAgg[key].count += 1
    prodAgg[key].qRateSum += r.qualified_rate
  }
  const prodEntries = Object.entries(prodAgg).map(([name, v]) => ({
    product: name,
    achieve_rate: v.theo > 0 ? v.actual / v.theo : 0,
    qualified_rate: v.count > 0 ? v.qRateSum / v.count : 0,
  }))

  const totalTheo = (prodData || []).reduce((s, r) => s + (r.theoretical_qty || 0), 0)
  const totalActual = (prodData || []).reduce((s, r) => s + (r.actual_qty || 0), 0)
  const totalGood = (prodData || []).reduce((s, r) => s + (r.good_qty || 0), 0)
  const overallAchieve = totalTheo > 0 ? totalActual / totalTheo : 0
  const overallQualified = totalActual > 0 ? totalGood / totalActual : 0

  kpiCards.value = [
    { title: '产品数', value: `${prodEntries.length} 个`, icon: 'mdi-package-variant', color: 'primary' },
    { title: '整体达成率', value: fmtPct(overallAchieve), icon: 'mdi-chart-line', color: 'success' },
    { title: '整体合格率', value: fmtPct(overallQualified), icon: 'mdi-check-circle', color: 'info' },
    { title: '班组数', value: `${(teamData || []).length} 个`, icon: 'mdi-account-group', color: 'accent' },
  ]

  chartPanels.value = [
    {
      type: 'bar', title: '产品达成率',
      data: {
        labels: prodEntries.map(d => d.product),
        datasets: [{
          label: '达成率', data: prodEntries.map(d => +(d.achieve_rate * 100).toFixed(1)),
          backgroundColor: COLORS[0],
        }],
      },
      height: '300px',
    },
  ]

  if ((teamData || []).length > 0) {
    chartPanels.value.push({
      type: 'bar', title: '班组达成率 / 合格率',
      data: {
        labels: teamData.map(d => d.shift),
        datasets: [
          { label: '达成率', data: teamData.map(d => +(d.achieve_rate * 100).toFixed(1)), backgroundColor: COLORS[0] },
          { label: '合格率', data: teamData.map(d => +(d.qualified_rate * 100).toFixed(1)), backgroundColor: COLORS[1] },
        ],
      },
    })
  }

  tableHeaders.value = ['产品', '机器', '理论产量', '实绩数量', '良品数量', '不良数量', '达成率', '合格率']
  tableRows.value = (prodData || []).map(r => ({
    '产品': r.product, '机器': r.machine, '理论产量': r.theoretical_qty,
    '实绩数量': r.actual_qty, '良品数量': r.good_qty, '不良数量': r.bad_qty,
    '达成率': fmtPct(r.achieve_rate), '合格率': fmtPct(r.qualified_rate),
  }))
}

async function loadPostProcess() {
  const data = await reports.postProcessSummary(year.value)
  const rows = data.uncompleted || []
  const sendRows = data.send_summary || []

  const totalReceived = rows.reduce((s, r) => s + (r.total_received || 0), 0)
  const totalSent = rows.reduce((s, r) => s + (r.total_sent || 0), 0)
  const totalUncompleted = rows.reduce((s, r) => s + (r.uncompleted || 0), 0)
  const monthCount = rows.length || 0

  // 按月份建立送出对照表
  const sendMap = {}
  for (const s of sendRows) {
    const key = `${s.year}-${String(s.month).padStart(2, '0')}`
    sendMap[key] = s.total_send_qty || 0
  }

  kpiCards.value = [
    { title: '年度入仓总量', value: `${totalReceived} 件`, icon: 'mdi-archive-arrow-down', color: 'primary' },
    { title: '年度送出总量', value: `${totalSent} 件`, icon: 'mdi-send', color: 'success' },
    { title: '未完成总数', value: `${totalUncompleted} 件`, icon: 'mdi-progress-clock', color: 'warning' },
    { title: '已统计月份', value: `${monthCount} 个月`, icon: 'mdi-calendar-month', color: 'info' },
  ]

  chartPanels.value = []
  if (rows.length > 0) {
    const labels = rows.map(r => `${r.month}月`)
    chartPanels.value.push({
      type: 'bar', title: '各月入仓 / 送出 / 未完成',
      data: {
        labels,
        datasets: [
          { label: '本月入仓', data: rows.map(r => r.total_received), backgroundColor: COLORS[0] },
          { label: '本月完成', data: rows.map(r => r.total_sent), backgroundColor: COLORS[1] },
          { label: '未完成结余', data: rows.map(r => r.uncompleted), backgroundColor: COLORS[3] },
        ],
      },
    })

    // 后工序送出统计对比（按送出月份）
    if (sendRows.length > 0) {
      chartPanels.value.push({
        type: 'bar', title: '后工序各月送出数量',
        data: {
          labels: sendRows.map(r => `${r.month}月`),
          datasets: [{
            label: '送出数量',
            data: sendRows.map(r => r.total_send_qty),
            backgroundColor: COLORS[1],
          }],
        },
      })
    }
  }

  tableHeaders.value = ['月份', '本月入仓', '本月完成', '未完成结余']
  tableRows.value = rows.map(r => ({
    '月份': `${r.year}-${String(r.month).padStart(2, '0')}`,
    '本月入仓': r.total_received,
    '本月完成': r.total_sent,
    '未完成结余': r.uncompleted,
  }))
}

async function loadAll() {
  loading.value = true
  kpiCards.value = []
  chartPanels.value = []
  tableHeaders.value = []
  tableRows.value = []

  try {
    switch (reportType.value) {
      case 'cost': await loadCost(); break
      case 'tool-purchase': await loadToolPurchase(); break
      case 'production': await loadProduction(); break
      case 'post-process': await loadPostProcess(); break
    }
  } catch (e) {
    console.error('加载报表数据失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>
