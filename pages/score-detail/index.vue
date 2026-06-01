<template>
	<view class="page">
		<!-- Hero -->
		<view class="hero">
			<view class="hero-back" @click="goBack"><text>‹</text></view>
			<view class="hero-score-wrap">
				<text class="hero-score">{{ healthScore || '--' }}</text>
				<text class="hero-label">健康评分</text>
			</view>
			<view class="hero-meta">
				<text class="hero-level">{{ healthLevel }}</text>
				<view class="hero-trend" v-if="scoreTrend !== 0">
					<text>{{ scoreTrend > 0 ? '↑' : '↓' }}{{ Math.abs(scoreTrend) }}</text>
				</view>
			</view>
		</view>

		<!-- 范围切换 -->
		<view class="range-bar">
			<view v-for="r in ranges" :key="r.key" class="range-tab" :class="{ active: activeRange === r.key }" @click="activeRange = r.key">
				<text>{{ r.label }}</text>
			</view>
		</view>

		<!-- 评分趋势折线图 -->
		<view class="chart-card">
			<text class="chart-title">📈 评分趋势</text>
			<qiun-data-charts type="line" :chartData="trendChartData" :opts="trendChartOpts" height="360rpx" />
		</view>

		<!-- 6 维度雷达图 -->
		<view class="chart-card">
			<text class="chart-title">🎯 维度分析</text>
			<qiun-data-charts type="radar" :chartData="radarChartData" :opts="radarChartOpts" height="420rpx" />
		</view>

		<!-- 评分日历热力图 -->
		<view class="chart-card">
			<view class="heatmap-header">
				<text class="chart-title">📅 每日评分</text>
				<view class="hm-nav-row">
					<text class="hm-nav" @click="prevCalMonth">‹</text>
					<text class="hm-month">{{ calYear }}.{{ calMonth }}</text>
					<text class="hm-nav" @click="nextCalMonth">›</text>
				</view>
			</view>
			<view class="cal-grid">
				<text v-for="w in calWeekdays" :key="w" class="cal-hd">{{ w }}</text>
				<view v-for="(c, i) in calGrid" :key="i" class="cal-cell" :class="{ 'cal-empty': !c.current }">
					<template v-if="c.current">
						<view class="cal-bg" :style="{ background: scoreHeatColor(c.value) }"></view>
						<text class="cal-num">{{ c.day }}</text>
					</template>
				</view>
			</view>
			<view class="cal-legend">
				<text class="cal-leg-label">低</text>
				<view class="cal-leg-bar" style="background:rgba(239,68,68,0.55)"></view>
				<view class="cal-leg-bar" style="background:rgba(245,158,11,0.35)"></view>
				<view class="cal-leg-bar" style="background:rgba(16,185,129,0.35)"></view>
				<view class="cal-leg-bar" style="background:rgba(16,185,129,0.55)"></view>
				<text class="cal-leg-label">高</text>
			</view>
		</view>

		<view class="bottom-spacer"></view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecords } from '@/utils/api'

const fmtDate = (d) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

const ranges = [
	{ key: 'day', label: '日' },
	{ key: 'week', label: '周' },
	{ key: 'month', label: '月' },
	{ key: 'year', label: '年' },
]
const calWeekdays = ['日', '一', '二', '三', '四', '五', '六']

const activeRange = ref('week')
const allRecords = ref([])

// ── 范围过滤 ──
const filteredRecords = computed(() => {
	const now = new Date()
	let start
	switch (activeRange.value) {
		case 'day': start = new Date(now); break
		case 'week': start = new Date(now); start.setDate(now.getDate() - 6); break
		case 'month': start = new Date(now); start.setDate(now.getDate() - 29); break
		case 'year': start = new Date(now); start.setFullYear(now.getFullYear() - 1); break
		default: start = new Date(now); start.setDate(now.getDate() - 6)
	}
	return allRecords.value.filter(r => r.date >= fmtDate(start) && r.date <= fmtDate(now))
})

// ── 当前评分 ──
const healthScore = computed(() => {
	const data = filteredRecords.value.filter(r => r.healthScore != null)
	return data.length ? data[data.length - 1].healthScore : 0
})

const healthLevel = computed(() => {
	const s = healthScore.value
	if (!s) return '暂无数据'; if (s >= 90) return '优秀'; if (s >= 80) return '良好'
	if (s >= 60) return '一般'; return '需关注'
})

const scoreTrend = computed(() => {
	const data = filteredRecords.value.filter(r => r.healthScore != null)
	if (data.length < 2) return 0
	return data[data.length - 1].healthScore - data[data.length - 2].healthScore
})

// ── 今日6维度得分 ──
const todayDims = computed(() => {
	const data = filteredRecords.value.filter(r => r.healthScore != null)
	const t = data.length ? data[data.length - 1] : {}
	const has = Object.keys(t).length > 0
	return [
		{ label: '步数', value: Math.min(100, Math.round(((has ? t.steps : 0) || 0) / 10000 * 100)) },
		{ label: '心率', value: has && (t.hrAvg || t.heartRate) ? Math.max(0, Math.min(100, Math.round(100 - Math.abs((t.hrAvg || t.heartRate) - 70) * 2.5))) : 0 },
		{ label: '睡眠', value: Math.min(100, Math.round(((has ? t.sleep : 0) || 0) / 8 * 100)) },
		{ label: '饮水', value: Math.min(100, Math.round(((has ? t.water : 0) || 0) / 8 * 100)) },
		{ label: '运动', value: Math.min(100, Math.round(((has ? t.exercise : 0) || 0) / 60 * 100)) },
		{ label: '情绪', value: (has ? t.mood : 0) || 70 },
	]
})

// ── 趋势折线图 ──
const trendChartData = computed(() => {
	const data = filteredRecords.value.filter(r => r.healthScore != null)
	const map = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
	return {
		categories: data.map(r => {
			if (activeRange.value === 'day') return r.date
			if (activeRange.value === 'week') { const d = new Date(r.date); return map[d.getDay()] }
			return (r.date || '').slice(5)
		}),
		series: [{ name: '健康评分', data: data.map(r => r.healthScore || 0) }],
	}
})

const trendChartOpts = computed(() => ({
	padding: [15, 10, 10, 35],
	dataLabel: false,
	legend: { show: false },
	xAxis: {
		labelCount: activeRange.value === 'year' ? 12 : 7,
		itemCount: activeRange.value === 'year' ? 12 : activeRange.value === 'month' ? 30 : 7,
		scrollShow: activeRange.value === 'month' || activeRange.value === 'year',
		scrollAlign: 'left',
	},
	yAxis: { data: [{ min: 0, max: 100 }] },
	extra: {
		line: {
			type: 'curve',
			width: 2,
			color: ['#6B73FF'],
			areaStyle: { type: 'gradient', color: ['#6B73FF30', 'transparent'], opacity: 0.3 },
		},
		tooltip: { showBox: true },
	},
	color: ['#6B73FF'],
}))

// ── 雷达图 ──
const radarChartData = computed(() => ({
	categories: todayDims.value.map(d => d.label),
	series: [{ name: '当前评分', data: todayDims.value.map(d => d.value) }],
}))

const radarChartOpts = {
	padding: [20, 20, 20, 20],
	legend: { show: false },
	dataLabel: false,
	background: 'transparent',
	yAxis: { disabled: true, max: 100 },
	extra: {
		radar: {
			type: 'circle',
			gridColor: '#E8ECF1',
			gridBorderWidth: 1,
			max: 100,
			labelColor: '#666',
			opacity: 0.3,
			lineColor: ['#6B73FF'],
			areaColor: ['#6B73FF20'],
		},
	},
	color: ['#6B73FF'],
}

// ── 评分热力图 ──
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth() + 1)

const calGrid = computed(() => {
	const y = calYear.value; const m = calMonth.value
	const firstDay = new Date(y, m - 1, 1)
	const lastDay = new Date(y, m, 0)
	const days = lastDay.getDate()
	const startWd = firstDay.getDay()
	const map = {}
	allRecords.value.forEach(r => { if (r.date && r.healthScore != null) map[r.date] = r.healthScore })
	const grid = []
	for (let i = 0; i < startWd; i++) grid.push({ current: false, day: 0, value: null })
	for (let d = 1; d <= days; d++) {
		const ds = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
		grid.push({ current: true, day: d, value: map[ds] !== undefined ? map[ds] : null })
	}
	return grid
})

const scoreHeatColor = (v) => {
	if (v === null || v === undefined) return 'transparent'
	if (v >= 85) return 'rgba(16,185,129,0.55)'
	if (v >= 70) return 'rgba(16,185,129,0.35)'
	if (v >= 55) return 'rgba(245,158,11,0.35)'
	return 'rgba(239,68,68,0.55)'
}

const prevCalMonth = () => {
	if (calMonth.value === 1) { calMonth.value = 12; calYear.value-- } else calMonth.value--
}
const nextCalMonth = () => {
	if (calMonth.value === 12) { calMonth.value = 1; calYear.value++ } else calMonth.value++
}

const goBack = () => uni.navigateBack()

// ── 数据加载 ──
onMounted(async () => {
	const now = new Date()
	const yearAgo = new Date(now); yearAgo.setFullYear(now.getFullYear() - 1)
	try {
		const records = await fetchRecords(fmtDate(yearAgo), fmtDate(now))
		if (records && records.length) allRecords.value = records
	} catch (e) { console.warn('[ScoreDetail] 加载失败:', e) }
})
</script>

<style scoped lang="scss">
$primary: #6B73FF; $green: #10B981; $amber: #F59E0B; $red: #EF4444;

.page { background: var(--page-bg); min-height: 100vh; transition: background 0.3s; }

// Hero
.hero {
	background: linear-gradient(135deg, var(--hero-bg-start), var(--hero-bg-end));
	padding: 24rpx 32rpx 40rpx;
}
.hero-back { width: 56rpx; height: 56rpx; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 16rpx; font-size: 40rpx; color: #fff; }
.hero-score-wrap { text-align: center; }
.hero-score { font-size: 96rpx; font-weight: 900; color: #fff; line-height: 1; }
.hero-label { font-size: 24rpx; color: rgba(255,255,255,0.6); display: block; margin-top: 8rpx; }
.hero-meta { display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 16rpx; margin-top: 16rpx; }
.hero-level { font-size: 28rpx; font-weight: 600; color: #fff; background: rgba(255,255,255,0.15); padding: 6rpx 20rpx; border-radius: 999rpx; }
.hero-trend { font-size: 26rpx; font-weight: 600; color: $green; background: rgba(16,185,129,0.2); padding: 6rpx 16rpx; border-radius: 999rpx; }

// Range
.range-bar { display: flex; flex-direction: row; margin: 0 28rpx 20rpx; background: var(--card-bg); border-radius: 24rpx; padding: 6rpx; box-shadow: var(--shadow-card); transition: background 0.3s; }
.range-tab { flex: 1; text-align: center; padding: 14rpx 0; border-radius: 20rpx; font-size: 26rpx; color: var(--text-3); font-weight: 500; }
.range-tab.active { background: $primary; color: #fff; font-weight: 600; }

// Chart card
.chart-card { background: var(--card-bg); margin: 0 24rpx 20rpx; border-radius: 24rpx; padding: 24rpx 16rpx; box-shadow: var(--shadow-card); transition: background 0.3s; }
.chart-title { font-size: 28rpx; font-weight: 700; color: var(--text-1); display: block; margin-bottom: 12rpx; padding: 0 8rpx; }

// Heatmap
.heatmap-header { display: flex; flex-direction: row; justify-content: space-between; align-items: center; margin-bottom: 4rpx; padding: 0 8rpx; }
.hm-nav-row { display: flex; flex-direction: row; align-items: center; gap: 12rpx; }
.hm-nav { font-size: 26rpx; color: $primary; padding: 4rpx 12rpx; background: rgba(107,115,255,0.08); border-radius: 8rpx; }
.hm-month { font-size: 26rpx; font-weight: 600; color: var(--text-2); min-width: 120rpx; text-align: center; }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5rpx; }
.cal-hd { text-align: center; font-size: 22rpx; color: var(--text-3); padding: 8rpx 0; font-weight: 500; }
.cal-cell { position: relative; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 10rpx; min-height: 70rpx; }
.cal-empty { visibility: hidden; }
.cal-bg { position: absolute; inset: 0; border-radius: 10rpx; }
.cal-num { font-size: 22rpx; color: var(--text-1); font-weight: 500; z-index: 1; }

.cal-legend { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 8rpx; margin-top: 18rpx; }
.cal-leg-label { font-size: 20rpx; color: var(--text-3); }
.cal-leg-bar { width: 34rpx; height: 12rpx; border-radius: 3rpx; }

.bottom-spacer { height: 40rpx; }
</style>
