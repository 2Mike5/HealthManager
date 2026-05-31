<template>
	<view class="detail-page">

		<!-- 顶部概览卡片 -->
		<view class="detail-hero" :style="{ background: heroBg }">
			<view class="dh-back" @click="goBack">
				<text class="dh-back-icon">‹</text>
			</view>
			<view class="dh-info">
				<text class="dh-icon">{{ metricIcon }}</text>
				<text class="dh-title">{{ metricTitle }}</text>
				<text class="dh-sub">{{ metricSub }}</text>
			</view>
			<view class="dh-stats">
				<view class="dhs-item">
					<text class="dhs-val">{{ fmtNum(currentVal) }}</text>
					<text class="dhs-unit">{{ metricUnit }}</text>
				</view>
				<view class="dhs-row">
					<view class="dhs-mini">
						<text class="dhs-mini-label">平均值</text>
						<text class="dhs-mini-val">{{ fmtNum(avgVal) }} {{ metricUnit }}</text>
					</view>
					<view class="dhs-mini">
						<text class="dhs-mini-label">最高</text>
						<text class="dhs-mini-val">{{ fmtNum(maxVal) }} {{ metricUnit }}</text>
					</view>
					<view class="dhs-mini">
						<text class="dhs-mini-label">最低</text>
						<text class="dhs-mini-val">{{ fmtNum(minVal) }} {{ metricUnit }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 时间范围切换 -->
		<view class="range-bar">
			<view
				v-for="r in ranges"
				:key="r.key"
				class="range-tab"
				:class="{ active: activeRange === r.key }"
				@click="switchRange(r.key)"
			>
				<text>{{ r.label }}</text>
			</view>
		</view>

		<!-- 心率模式切换（仅心率显示） -->
		<view class="hr-mode-bar" v-if="metricType === 'heart'">
			<view
				v-for="m in hrModes"
				:key="m.key"
				class="hr-mode-tab"
				:class="{ active: hrDetailMode === m.key }"
				@click="hrDetailMode = m.key"
			>
				<text>{{ m.label }}</text>
			</view>
		</view>

		<!-- 图表区 -->
		<view class="chart-card">
			<qiun-data-charts
				v-if="chartType === 'line'"
				type="line"
				:chartData="chartData"
				:opts="chartOpts"
				height="400rpx"
			/>
			<qiun-data-charts
				v-else-if="chartType === 'column'"
				type="column"
				:chartData="chartData"
				:opts="chartOpts"
				height="400rpx"
			/>
			<view v-else class="chart-empty">
				<text class="chart-empty-text">暂无数据</text>
			</view>
		</view>

		<!-- 统计数据 -->
		<view class="stats-card">
			<text class="stats-title">📊 统计概览</text>
			<view class="stats-grid">
				<view class="stats-item">
					<text class="stats-val">{{ fmtNum(avgVal) }}</text>
					<text class="stats-label">平均值</text>
				</view>
				<view class="stats-item">
					<text class="stats-val">{{ fmtNum(maxVal) }}</text>
					<text class="stats-label">最高值</text>
				</view>
				<view class="stats-item">
					<text class="stats-val">{{ fmtNum(minVal) }}</text>
					<text class="stats-label">最低值</text>
				</view>
				<view class="stats-item">
					<text class="stats-val">{{ dataCount }}</text>
					<text class="stats-label">记录天数</text>
				</view>
			</view>
		</view>

		<!-- 睡眠热力图（仅睡眠类型显示） -->
		<view class="heatmap-card" v-if="metricType === 'sleep'">
			<view class="heatmap-header">
				<text class="heatmap-title">📅 睡眠热力图</text>
				<view class="heatmap-month-nav">
					<text class="hm-nav" @click="prevCalendarMonth">〈</text>
					<text class="hm-month">{{ calendarYear }}年{{ calendarMonth }}月</text>
					<text class="hm-nav" @click="nextCalendarMonth">〉</text>
				</view>
			</view>
			<view class="cal-grid">
				<text v-for="w in calWeekdays" :key="w" class="cal-hd">{{ w }}</text>
				<view
					v-for="(cell, i) in calendarGrid"
					:key="i"
					class="cal-cell"
					:class="{ 'cal-empty': !cell.isCurrentMonth }"
				>
					<template v-if="cell.isCurrentMonth">
						<view class="cal-bg" :style="{ background: sleepHeatColor(cell.value) }"></view>
						<text class="cal-num">{{ cell.day }}</text>
					</template>
				</view>
			</view>
			<view class="cal-legend">
				<text class="cal-legend-label">不足</text>
				<view class="cal-legend-bar" style="background:rgba(239,68,68,0.55);"></view>
				<view class="cal-legend-bar" style="background:rgba(239,68,68,0.35);"></view>
				<view class="cal-legend-bar" style="background:rgba(245,158,11,0.35);"></view>
				<view class="cal-legend-bar" style="background:rgba(139,92,246,0.35);"></view>
				<view class="cal-legend-bar" style="background:rgba(139,92,246,0.55);"></view>
				<text class="cal-legend-label">充足</text>
			</view>
		</view>

		<!-- 近期记录列表 -->
		<view class="records-card">
			<text class="records-title">📋 近期记录</text>
			<view class="record-row" v-for="(r, i) in displayRecords" :key="i">
				<text class="rec-date">{{ r.date }}</text>
				<view class="rec-vals" v-if="metricType === 'heart' && r.maxVal !== null">
					<text class="rec-hi">最高 {{ r.maxVal }}</text>
					<text class="rec-lo">最低 {{ r.minVal }}</text>
				</view>
				<text class="rec-val" v-else>{{ fmtNum(r.value) }} {{ metricUnit }}</text>
			</view>
			<view v-if="!displayRecords.length" class="record-empty">
				<text>暂无记录</text>
			</view>
		</view>

		<view class="bottom-spacer"></view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecords } from '@/utils/api'

// ── 页面参数 ──
const metricType = ref('steps')

const metricConfig = {
	steps: {
		title: '步数', icon: '🚶', unit: '步', goal: 10000,
		bg: 'linear-gradient(135deg, #E8F5E9, #C8E6C9)',
		field: 'steps', chartType: 'column',
		sub: '每日步行数据',
	},
	sleep: {
		title: '睡眠', icon: '💤', unit: '小时', goal: 8,
		bg: 'linear-gradient(135deg, #EDE9FE, #DDD6FE)',
		field: 'sleep', chartType: 'column',
		sub: '每日睡眠时长',
	},
	heart: {
		title: '心率', icon: '❤️', unit: 'bpm', goal: null,
		bg: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
		field: 'hrAvg', chartType: 'line',
		sub: '静息心率趋势',
	},
	water: {
		title: '饮水', icon: '💧', unit: '杯', goal: 8,
		bg: 'linear-gradient(135deg, #DBEAFE, #BFDBFE)',
		field: 'water', chartType: 'column',
		sub: '每日饮水量',
	},
}

const ranges = [
	{ key: 'day',   label: '日' },
	{ key: 'week',  label: '周' },
	{ key: 'month', label: '月' },
	{ key: 'year',  label: '年' },
]

const fmtDate = (d) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

const fmtNum = (v) => {
	if (v === null || v === undefined || v === 0 && typeof v !== 'number') return '--'
	if (typeof v === 'number' && v % 1 !== 0) return v.toFixed(1)
	return Number(v).toLocaleString()
}

// ── 响应式数据 ──
const activeRange = ref('week')
const allRecords = ref([])

const config = computed(() => metricConfig[metricType.value] || metricConfig.steps)
const metricTitle = computed(() => config.value.title)
const metricIcon = computed(() => config.value.icon)
const metricUnit = computed(() => config.value.unit)
const metricSub = computed(() => config.value.sub)
const heroBg = computed(() => config.value.bg)
const chartType = computed(() => config.value.chartType)
const hrModes = [
    { key: 'min', label: '最低' },
    { key: 'avg', label: '平均' },
    { key: 'max', label: '最高' },
]
const hrDetailMode = ref('avg')
const field = computed(() => {
    if (metricType.value === 'heart') {
        return hrDetailMode.value === 'min' ? 'hrMin' : hrDetailMode.value === 'max' ? 'hrMax' : 'hrAvg'
    }
    return config.value.field
})

// 根据范围过滤数据
const filteredRecords = computed(() => {
	const now = new Date()
	let start
	switch (activeRange.value) {
		case 'day':   start = new Date(now); break
		case 'week':  start = new Date(now); start.setDate(now.getDate() - 6); break
		case 'month': start = new Date(now); start.setDate(now.getDate() - 29); break
		case 'year':  start = new Date(now); start.setFullYear(now.getFullYear() - 1); break
		default:      start = new Date(now); start.setDate(now.getDate() - 6)
	}
	const startStr = fmtDate(start)
	const endStr = fmtDate(now)

	// 从 allRecords 过滤
	let filtered = allRecords.value.filter(r => r.date >= startStr && r.date <= endStr)

	// 如果数据不够，补充空白（让图表好看）
	if (activeRange.value === 'week' && filtered.length < 7) {
		const existing = new Set(filtered.map(r => r.date))
		const cur = new Date(start)
		for (let i = 0; i < 7; i++) {
			const ds = fmtDate(cur)
			if (!existing.has(ds)) {
				filtered.push({ date: ds, [field.value]: null })
			}
			cur.setDate(cur.getDate() + 1)
		}
		filtered.sort((a, b) => a.date.localeCompare(b.date))
	}

	return filtered
})

const currentVal = computed(() => {
	const recs = filteredRecords.value.filter(r => r[field.value] != null)
	return recs.length ? recs[recs.length - 1][field.value] : 0
})

const avgVal = computed(() => {
	const vals = filteredRecords.value.filter(r => r[field.value] != null).map(r => r[field.value])
	return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length * 10) / 10 : 0
})

const maxVal = computed(() => {
	const vals = filteredRecords.value.filter(r => r[field.value] != null).map(r => r[field.value])
	return vals.length ? Math.max(...vals) : 0
})

const minVal = computed(() => {
	const vals = filteredRecords.value.filter(r => r[field.value] != null).map(r => r[field.value])
	return vals.length ? Math.min(...vals) : 0
})

const dataCount = computed(() => {
	return filteredRecords.value.filter(r => r[field.value] != null).length
})

// 近期记录（最近20条）
const displayRecords = computed(() => {
	return filteredRecords.value
		.filter(r => r[field.value] != null)
		.map(r => ({
			date: r.date,
			value: r[field.value],
			maxVal: metricType.value === 'heart' ? (r.hrMax || null) : null,
			minVal: metricType.value === 'heart' ? (r.hrMin || null) : null,
		}))
		.slice(-20)
		.reverse()
})

// ── 图表配置 ──
const chartData = computed(() => {
	const data = filteredRecords.value
	const WEEKDAYS_MAP = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

	const cats = data.map(r => {
		if (activeRange.value === 'day') return r.date
		const d = new Date(r.date)
		if (activeRange.value === 'week') return WEEKDAYS_MAP[d.getDay()]
		return r.date.slice(5) // MM-DD
	})
	const vals = data.map(r => r[field.value] || 0)

	return {
		categories: cats,
		series: [{ name: config.value.title, data: vals }],
	}
})

const chartColors = {
	steps: ['#4CAF50'],
	sleep: ['#7C3AED'],
	heart: ['#EF4444'],
	water: ['#3B82F6'],
}

const chartOpts = computed(() => {
	const c = chartColors[metricType.value] || ['#4CAF50']
	return {
		padding: [15, 10, 10, 35],
		dataLabel: false,
			legend: { show: false },
		xAxis: {
			labelCount: activeRange.value === 'year' ? 12 : activeRange.value === 'month' ? 10 : 7,
			itemCount: activeRange.value === 'year' ? 12 : activeRange.value === 'month' ? 30 : 7,
			scrollShow: activeRange.value === 'month' || activeRange.value === 'year',
			scrollAlign: 'left',
		},
		yAxis: { data: [{ min: 0 }] },
		extra: {
			[chartType.value]: {
				width: activeRange.value === 'day' ? 30 : 16,
				color: c,
				linearType: 'custom',
				...(chartType.value === 'line' ? {
					type: 'curve',
					width: 1.5,
					areaStyle: {
						type: 'gradient',
						color: [c[0] + '30', 'transparent'],
						opacity: 0.3,
					},
				} : {}),
			},
			tooltip: { showBox: true },
		},
		color: c,
	}
})

// ── 方法 ──
const switchRange = (key) => {
	activeRange.value = key
}

// ── 睡眠热力图数据 ──
const calWeekdays = ['日', '一', '二', '三', '四', '五', '六']
const calendarYear = ref(new Date().getFullYear())
const calendarMonth = ref(new Date().getMonth() + 1)

const calendarGrid = computed(() => {
	const year = calendarYear.value
	const month = calendarMonth.value
	const firstDay = new Date(year, month - 1, 1)
	const lastDay = new Date(year, month, 0)
	const daysInMonth = lastDay.getDate()
	const startWeekday = firstDay.getDay()

	// 建立 date → sleep 映射
	const sleepMap = {}
	allRecords.value.forEach(r => {
		if (r.date) sleepMap[r.date] = r.sleep
	})

	const grid = []
	for (let i = 0; i < startWeekday; i++) {
		grid.push({ day: 0, value: null, isCurrentMonth: false })
	}
	for (let d = 1; d <= daysInMonth; d++) {
		const ds = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`
		grid.push({
			day: d,
			value: sleepMap[ds] !== undefined ? sleepMap[ds] : null,
			isCurrentMonth: true,
		})
	}
	return grid
})

const sleepHeatColor = (sleep) => {
	if (sleep === null || sleep === undefined) return 'transparent'
	if (sleep >= 8) return 'rgba(139, 92, 246, 0.55)'
	if (sleep >= 7) return 'rgba(139, 92, 246, 0.35)'
	if (sleep >= 6) return 'rgba(245, 158, 11, 0.35)'
	if (sleep >= 5) return 'rgba(239, 68, 68, 0.35)'
	return 'rgba(239, 68, 68, 0.55)'
}

const prevCalendarMonth = () => {
	if (calendarMonth.value === 1) {
		calendarMonth.value = 12
		calendarYear.value--
	} else {
		calendarMonth.value--
	}
}
const nextCalendarMonth = () => {
	if (calendarMonth.value === 12) {
		calendarMonth.value = 1
		calendarYear.value++
	} else {
		calendarMonth.value++
	}
}

const goBack = () => {
	uni.navigateBack()
}

// ── 数据加载 ──
onMounted(() => {
	// 获取页面参数
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	if (currentPage && currentPage.options && currentPage.options.type) {
		metricType.value = currentPage.options.type
	}
	loadData()
})

async function loadData() {
	const now = new Date()
	const yearAgo = new Date(now)
	yearAgo.setFullYear(now.getFullYear() - 1)

	try {
		const records = await fetchRecords(fmtDate(yearAgo), fmtDate(now))
		if (records && records.length) {
			allRecords.value = records
		}
	} catch (e) {
		console.warn('[Detail] 数据加载失败:', e)
	}
}
</script>

<style scoped lang="scss">
$white: #FFFFFF;
$text-1: #1A1A2E;
$text-2: #555;
$text-3: #999;
$bg: #F5F7FA;

.detail-page {
	background: $bg;
	min-height: 100vh;
	padding-bottom: 40rpx;
}

// ── Hero ──
.detail-hero {
	padding: 24rpx 28rpx 32rpx;
	position: relative;
}
.dh-back {
	width: 56rpx; height: 56rpx; border-radius: 50%;
	background: rgba(255,255,255,0.6);
	display: flex; align-items: center; justify-content: center;
	margin-bottom: 16rpx;
}
.dh-back-icon { font-size: 40rpx; color: $text-1; font-weight: 300; }
.dh-info { text-align: center; margin-bottom: 20rpx; }
.dh-icon { font-size: 56rpx; display: block; }
.dh-title { font-size: 40rpx; font-weight: 800; color: $text-1; display: block; margin-top: 8rpx; }
.dh-sub { font-size: 24rpx; color: $text-2; display: block; margin-top: 4rpx; }
.dh-stats { text-align: center; }
.dhs-item { display: flex; flex-direction: row; align-items: baseline; justify-content: center; gap: 8rpx; }
.dhs-val { font-size: 80rpx; font-weight: 900; color: $text-1; line-height: 1; }
.dhs-unit { font-size: 28rpx; color: $text-3; }
.dhs-row { display: flex; flex-direction: row; justify-content: center; gap: 48rpx; margin-top: 16rpx; }
.dhs-mini { text-align: center; }
.dhs-mini-label { font-size: 20rpx; color: $text-3; display: block; }
.dhs-mini-val { font-size: 26rpx; color: $text-1; font-weight: 600; display: block; margin-top: 4rpx; }

// ── 范围切换 ──
.range-bar {
	display: flex; flex-direction: row; justify-content: center;
	margin: 0 28rpx 20rpx;
	background: $white; border-radius: 24rpx;
	padding: 6rpx; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.range-tab {
	flex: 1; text-align: center;
	padding: 14rpx 0; border-radius: 20rpx;
	font-size: 26rpx; color: $text-3; font-weight: 500;
	transition: all 0.2s;
}
.range-tab.active { background: #3B82F6; color: #fff; font-weight: 600; }

// ── 心率模式切换 ──
.hr-mode-bar {
	display: flex; flex-direction: row; justify-content: center;
	margin: 0 28rpx 16rpx;
	background: $white; border-radius: 24rpx;
	padding: 6rpx; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.hr-mode-tab {
	flex: 1; text-align: center;
	padding: 10rpx 0; border-radius: 20rpx;
	font-size: 24rpx; color: $text-3; font-weight: 500;
	transition: all 0.2s;
}
.hr-mode-tab.active { background: #3B82F6; color: #fff; font-weight: 600; }

// ── 图表卡片 ──
.chart-card {
	background: $white; margin: 0 24rpx 20rpx;
	border-radius: 24rpx; padding: 20rpx 16rpx;
	box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.chart-empty { display: flex; align-items: center; justify-content: center; height: 400rpx; }
.chart-empty-text { font-size: 28rpx; color: $text-3; }

// ── 统计卡片 ──
.stats-card {
	background: $white; margin: 0 24rpx 20rpx;
	border-radius: 24rpx; padding: 24rpx 28rpx;
	box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.stats-title { font-size: 28rpx; font-weight: 700; color: $text-1; display: block; margin-bottom: 16rpx; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16rpx; }
.stats-item { text-align: center; }
.stats-val { font-size: 40rpx; font-weight: 800; color: $text-1; display: block; line-height: 1; }
.stats-label { font-size: 20rpx; color: $text-3; display: block; margin-top: 6rpx; }

// ── 记录列表 ──
.records-card {
	background: $white; margin: 0 24rpx;
	border-radius: 24rpx; padding: 24rpx 28rpx;
	box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.records-title { font-size: 28rpx; font-weight: 700; color: $text-1; display: block; margin-bottom: 14rpx; }
.record-row {
	display: flex; flex-direction: row;
	justify-content: space-between; align-items: center;
	padding: 14rpx 0; border-bottom: 1px solid #F5F5F5;
}
.rec-date { font-size: 26rpx; color: $text-2; }
.rec-val { font-size: 26rpx; color: $text-1; font-weight: 600; }
.rec-vals { display: flex; flex-direction: row; gap: 16rpx; }
.rec-hi { font-size: 24rpx; color: $text-1; font-weight: 600; }
.rec-lo { font-size: 24rpx; color: $text-1; font-weight: 600; }
.record-empty { text-align: center; padding: 40rpx 0; font-size: 26rpx; color: $text-3; }

// ── 睡眠热力图 ──
.heatmap-card {
	background: $white; margin: 0 24rpx 20rpx;
	border-radius: 24rpx; padding: 24rpx 20rpx;
	box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.heatmap-header {
	display: flex; flex-direction: row;
	justify-content: space-between; align-items: center;
	margin-bottom: 16rpx;
}
.heatmap-title { font-size: 28rpx; font-weight: 700; color: $text-1; }
.heatmap-month-nav { display: flex; flex-direction: row; align-items: center; gap: 12rpx; }
.hm-nav {
	font-size: 26rpx; color: #7C3AED;
	padding: 4rpx 12rpx; background: rgba(124,58,237,0.08);
	border-radius: 8rpx;
}
.hm-month { font-size: 26rpx; font-weight: 600; color: $text-2; min-width: 130rpx; text-align: center; }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5rpx; }
.cal-hd { text-align: center; font-size: 22rpx; color: $text-3; padding: 8rpx 0; font-weight: 500; }
.cal-cell {
	position: relative; aspect-ratio: 1;
	display: flex; align-items: center; justify-content: center;
	border-radius: 10rpx; min-height: 70rpx;
}
.cal-empty { visibility: hidden; }
.cal-bg { position: absolute; inset: 0; border-radius: 10rpx; }
.cal-num { font-size: 22rpx; color: $text-1; font-weight: 500; z-index: 1; }

.cal-legend {
	display: flex; flex-direction: row;
	align-items: center; justify-content: center;
	gap: 8rpx; margin-top: 18rpx;
}
.cal-legend-label { font-size: 20rpx; color: $text-3; }
.cal-legend-bar { width: 34rpx; height: 12rpx; border-radius: 3rpx; }

.bottom-spacer { height: 40rpx; }
</style>
