<template>
	<view class="page">
		<view class="hero-bg">
			<view class="hero-content">
				<view class="hero-left">
					<text class="hero-greeting">{{ greetingTime }}，{{ userName }} 👋</text>
					<text class="hero-date">{{ currentDate }}</text>
				</view>
				<view class="hero-avatar">
					<text class="hero-avatar-text">{{ userInitial }}</text>
				</view>
			</view>
		</view>

		<scroll-view scroll-y="true" class="scroll-body" show-scrollbar="false">
			<!-- ═══════════ 1. 健康评分卡片 ═══════════ -->
			<view class="score-card" @click="goScoreDetail">
				<view class="score-row">
					<view class="score-ring-col">
						<view class="ring-wrap">
							<svg viewBox="0 0 120 120" class="ring-svg">
								<circle cx="60" cy="60" r="52" fill="none" stroke="#E8ECF1" stroke-width="10" />
								<circle cx="60" cy="60" r="52" fill="none" stroke="url(#ringGrad)" stroke-width="10"
									stroke-linecap="round" stroke-dasharray="327" :stroke-dashoffset="ringOffset"
									transform="rotate(-90, 60, 60)" class="ring-arc" />
								<defs>
									<linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop offset="0%" stop-color="#6B73FF" />
										<stop offset="100%" stop-color="#3B27FE" />
									</linearGradient>
								</defs>
							</svg>
							<view class="ring-center">
								<text class="ring-num">{{ healthScore || '--' }}</text>
								<text class="ring-label">健康评分</text>
							</view>
						</view>
					</view>
					<view class="score-detail">
						<view class="score-header">
							<text class="score-level">{{ healthLevel }}</text>
							<view class="score-trend" v-if="scoreTrend !== 0">
								<text class="score-trend-arrow">{{ scoreTrend > 0 ? '↑' : '↓' }}</text>
								<text class="score-trend-val">{{ Math.abs(scoreTrend) }}</text>
							</view>
						</view>
						<view class="score-dims">
							<view class="sd-row" v-for="d in dimensionBars" :key="d.key">
								<text class="sd-label">{{ d.icon }} {{ d.label }}</text>
								<view class="sd-track">
									<view class="sd-fill" :class="{ 'sd-best': d.isBest, 'sd-worst': d.isWorst }"
										:style="{ width: d.value + '%' }"></view>
								</view>
								<text class="sd-val" :class="{ 'sd-val-best': d.isBest, 'sd-val-worst': d.isWorst }">{{ d.value }}</text>
							</view>
						</view>
						<view class="score-arrow-hint"><text>查看详情 ›</text></view>
					</view>
				</view>
			</view>

			<!-- ═══════════ 2. AI 健康建议 ═══════════ -->
			<view class="ai-card">
				<view class="ai-header">
					<text class="ai-title">🤖 AI 健康建议</text>
					<text class="ai-more" @click="goAI">查看详情 ›</text>
				</view>
				<view class="ai-body" v-if="aiLoading">
					<text class="ai-loading-text">AI 正在分析你的健康数据...</text>
				</view>
				<view class="ai-body" v-else-if="aiInsight">
					<text class="ai-icon">⚡</text>
					<text class="ai-text">{{ aiInsight }}</text>
				</view>
				<view class="ai-body" v-else>
					<text class="ai-icon">⚡</text>
					<text class="ai-text">暂无法获取 AI 建议，请检查网络后重试</text>
				</view>
			</view>

			<!-- ═══════════ 3. 四大指标 2x2 ═══════════ -->
			<view class="metrics-grid">
				<view class="metric-cell" v-for="m in metricsGrid" :key="m.key" @click="goDetail(m.key)">
					<view class="mc-header">
						<view class="mc-icon" :style="{ background: m.bg }"><text>{{ m.icon }}</text></view>
						<text class="mc-title">{{ m.label }}</text>
						<text class="mc-arrow">›</text>
					</view>
					<view class="mc-body">
						<view class="mc-main-info">
							<text class="mc-value">{{ m.display }}</text>
							<text class="mc-unit">{{ m.unit }}</text>
						</view>
						<view class="mc-arc-progress" v-if="m.key === 'steps'">
							<svg viewBox="0 0 60 60" class="mc-arc-svg">
								<circle cx="30" cy="30" r="24" fill="none" stroke="#E8F5E9" stroke-width="5" />
								<circle cx="30" cy="30" r="24" fill="none" stroke="#4CAF50" stroke-width="5"
									stroke-linecap="round" stroke-dasharray="151" :stroke-dashoffset="151 * (1 - m.percent / 100)"
									transform="rotate(-90, 30, 30)" />
							</svg>
							<text class="mc-arc-pct">{{ m.percent }}%</text>
						</view>
						<view class="mc-quality-tag" v-else-if="m.key === 'sleep'" :class="'tag-' + m.sleepLevel">
							<text>{{ m.sleepLabel }}</text>
						</view>
						<view class="mc-water-dots" v-else-if="m.key === 'water'">
							<view v-for="i in 8" :key="i" class="water-dot" :class="{ filled: i <= m.current }"></view>
						</view>
					</view>
					<text class="mc-target">{{ m.sub }}</text>
					<view class="mini-bars" :class="m.barClass">
						<view class="mini-bar" v-for="(h, i) in m.bars" :key="i" :style="{ height: h + 'rpx' }"></view>
					</view>
				</view>
			</view>

			<!-- ═══════════ 4. 心率趋势 ═══════════ -->
			<view class="trend-card">
				<view class="trend-header">
					<text class="trend-title">❤️ 心率趋势</text>
					<view class="trend-toggles">
						<view class="trend-hr-toggle">
							<text v-for="m in hrModes" :key="m.key" class="thr-tab" :class="{ active: hrTrendMode === m.key }"
								@click="hrTrendMode = m.key">{{ m.label }}</text>
						</view>
						<view class="trend-toggle">
							<text v-for="t in trendTabs" :key="t" class="trend-tab" :class="{ active: activeTrend === t }"
								@click="activeTrend = t">{{ t }}</text>
						</view>
					</view>
				</view>
				<view class="trend-chart">
					<view class="trend-y-axis"><text>80</text><text>70</text><text>60</text><text>50</text></view>
					<view class="trend-plot">
						<svg viewBox="0 0 280 120" class="trend-svg">
							<line v-for="y in [0,40,80,120]" :key="'g'+y" x1="0" :y1="y" x2="280" :y2="y" stroke="#F0F0F5" stroke-width="1" />
							<polygon :points="heartTrendArea" :fill="hrTrendColor + '14'" />
							<polyline fill="none" :stroke="hrTrendColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" :points="heartTrendLine" />
							<circle v-for="(pt, i) in heartTrendPoints" :key="'p'+i" :cx="pt.x" :cy="pt.y" r="4" fill="#fff" :stroke="hrTrendColor" stroke-width="1.5" />
						</svg>
					</view>
				</view>
				<view class="trend-x-axis">
					<text v-for="d in trendXLabels" :key="d">{{ d }}</text>
				</view>
			</view>

			<view class="bottom-spacer"></view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { fetchRecords, getProfile, fetchAIInsight } from '@/utils/api'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

const fmtDate = (d) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

const fmtNum = (v) => {
	if (v === null || v === undefined) return '--'
	return Number(v).toLocaleString()
}

// ── 用户 ──
const userName = ref('用户')
const userInitial = computed(() => (userName.value || 'U')[0])

const greetingTime = computed(() => {
	const h = new Date().getHours()
	if (h < 6) return '夜深了'; if (h < 9) return '早上好'; if (h < 12) return '上午好'
	if (h < 14) return '中午好'; if (h < 18) return '下午好'; return '晚上好'
})

const currentDate = computed(() => {
	const d = new Date()
	return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${WEEKDAYS[d.getDay()]}`
})

// ── 数据 ──
const todayRecord = ref({})
const weekRecords = ref([])
const trendAllRecords = ref([])
const dataLoaded = ref(false)
const healthGoals = ref(uni.getStorageSync('healthGoals') || { steps: 10000, sleep: 8, water: 8 })

// ── 健康评分 ──
const healthScore = ref(0)

const healthLevel = computed(() => {
	const s = healthScore.value
	if (!s) return '暂无数据'; if (s >= 90) return '优秀'; if (s >= 80) return '良好'
	if (s >= 60) return '一般'; return '需关注'
})

const dimScores = computed(() => {
	const t = todayRecord.value
	const has = Object.keys(t).length > 0
	const stepsScore = Math.min(100, Math.round(((has ? t.steps : 0) || 0) / healthGoals.value.steps * 100))
	const hrVal = has ? (t.hrAvg || t.heartRate || 0) : 0
	const hrScore = hrVal ? Math.max(0, Math.min(100, Math.round(100 - Math.abs(hrVal - 70) * 2.5))) : 0
	const sleepScore = Math.min(100, Math.round(((has ? t.sleep : 0) || 0) / healthGoals.value.sleep * 100))
	const waterScore = Math.min(100, Math.round(((has ? t.water : 0) || 0) / healthGoals.value.water * 100))
	const exerciseScore = Math.min(100, Math.round(((has ? t.exercise : 0) || 0) / 60 * 100))
	const moodScore = (has ? t.mood : 0) || 70
	return [
		{ key: 'steps', label: '步数', value: stepsScore },
		{ key: 'heart', label: '心率', value: hrScore },
		{ key: 'sleep', label: '睡眠', value: sleepScore },
		{ key: 'water', label: '饮水', value: waterScore },
		{ key: 'exercise', label: '运动', value: exerciseScore },
		{ key: 'mood', label: '情绪', value: moodScore },
	]
})

const scoreTrend = computed(() => {
	const records = weekRecords.value
	if (records.length < 2) return 0
	const today = records.find(r => r.date === fmtDate(new Date()))
	const yesterday = records.find(r => {
		const d = new Date(); d.setDate(d.getDate() - 1); return r.date === fmtDate(d)
	})
	if (!today || !yesterday) return 0
	return (today.healthScore || calcHealthScore(today)) - (yesterday.healthScore || calcHealthScore(yesterday))
})

const dimensionBars = computed(() => {
	const ICONS = { steps: '🚶', heart: '❤️', sleep: '💤', water: '💧', exercise: '🏃', mood: '😊' }
	const arr = [...dimScores.value]
	const bestKey = arr.sort((a, b) => b.value - a.value)[0]?.key
	const worstKey = arr.sort((a, b) => a.value - b.value)[arr.length - 1]?.key
	return dimScores.value.map(d => ({
		...d,
		icon: ICONS[d.key] || '',
		isBest: d.key === bestKey && d.value >= 70,
		isWorst: d.key === worstKey && d.value < 80,
	}))
})

const ringOffset = computed(() => 327 * (1 - (healthScore.value || 0) / 100))

// ── AI ──
const aiInsight = ref('')
const aiLoading = ref(false)

// ── 四大指标 ──
const metricsGrid = computed(() => {
	const t = todayRecord.value
	const steps = t.steps || 0
	const sleep = t.sleep || 0
	const hrAvg = t.hrAvg || t.heartRate || 0
	const water = t.water || 0
	const week = weekRecords.value

	const normBars = (field, maxH = 40) => {
		if (!week.length) return [4, 4, 4, 4, 4, 4, 4]
		const vals = week.map(r => r[field] || 0)
		const max = Math.max(...vals, 1)
		return vals.map(v => Math.max(4, (v / max) * maxH))
	}

	return [
		{
			key: 'steps', label: '步数', icon: '🚶', unit: '步', bg: '#E8F5E9',
			display: fmtNum(steps), percent: Math.min(100, Math.round(steps / healthGoals.value.steps * 100)),
			sub: `目标 10,000 步`, barClass: 'green-bars', bars: normBars('steps'),
		},
		{
			key: 'sleep', label: '睡眠', icon: '💤', unit: '小时', bg: '#EDE9FE',
			display: sleep ? sleep.toFixed(1) : '--', percent: Math.min(100, Math.round(sleep / healthGoals.value.sleep * 100)),
			sleepLevel: sleep >= 8 ? 'good' : sleep >= 6 ? 'fair' : 'poor',
			sleepLabel: sleep >= 8 ? '睡眠充足' : sleep >= 6 ? '轻度不足' : '需要补觉',
			sub: '建议 ' + healthGoals.value.sleep + ' 小时', barClass: 'purple-bars', bars: normBars('sleep'),
		},
		{
			key: 'heart', label: '心率', icon: '❤️', unit: 'bpm', bg: '#FEE2E2',
			display: hrAvg || '--', percent: null, sub: t.hrMin && t.hrMax ? `${t.hrMin}-${t.hrMax} bpm` : '',
			barClass: '', bars: [],
		},
		{
			key: 'water', label: '饮水', icon: '💧', unit: '杯', bg: '#DBEAFE',
			display: water || '--', percent: Math.min(100, Math.round(water / healthGoals.value.water * 100)),
			current: water, sub: '目标 ' + healthGoals.value.water + ' 杯', barClass: 'blue-bars', bars: normBars('water'),
		},
	]
})

// ── 心率趋势 ──
const trendTabs = ['日', '周', '月']
const activeTrend = ref('周')
const hrModes = [{ key: 'min', label: '最低' }, { key: 'avg', label: '平均' }, { key: 'max', label: '最高' }]
const hrTrendMode = ref('avg')
const hrTrendColor = computed(() => ({ min: '#3B82F6', avg: '#EF4444', max: '#F59E0B' }[hrTrendMode.value] || '#EF4444'))
const hrField = computed(() => hrTrendMode.value === 'min' ? 'hrMin' : hrTrendMode.value === 'max' ? 'hrMax' : 'hrAvg')

const trendDataRange = computed(() => {
	const now = new Date(); let start
	if (activeTrend.value === '日') start = new Date(now)
	else if (activeTrend.value === '月') start = new Date(now.getFullYear(), now.getMonth(), 1)
	else { start = new Date(now); start.setDate(now.getDate() - 6) }
	const allData = trendAllRecords.value.length ? trendAllRecords.value : weekRecords.value
	return allData.filter(r => r.date >= fmtDate(start) && r.date <= fmtDate(now))
})

const heartTrendData = computed(() => {
	const data = trendDataRange.value; const f = hrField.value
	if (!data.length) return [0, 0, 0, 0, 0, 0, 0]
	return data.map(r => r[f] || r.heartRate || 0)
})

const heartTrendPoints = computed(() => {
	const data = heartTrendData.value
	const maxVal = Math.max(...data, 80); const minVal = Math.min(...data, 50)
	const range = maxVal - minVal || 1; const chartH = 120
	return data.map((v, i) => ({ x: data.length === 1 ? 140 : (i / (data.length - 1)) * 280, y: chartH - ((v - minVal) / range) * chartH }))
})

const heartTrendLine = computed(() => heartTrendPoints.value.map(p => `${p.x},${p.y}`).join(' '))

const heartTrendArea = computed(() => {
	const pts = heartTrendPoints.value; if (!pts.length) return ''
	const first = pts[0]; const last = pts[pts.length - 1]
	return `${first.x},120 ${pts.map(p => `${p.x},${p.y}`).join(' ')} ${last.x},120`
})

const trendXLabels = computed(() => {
	const data = trendDataRange.value; if (!data.length) return []
	if (activeTrend.value === '日') return [data[0]?.date || '']
	if (activeTrend.value === '月') return data.map((r, i) => {
		const parts = (r.date || '').split('-'); if (parts.length !== 3) return ''
		return (i === 0 || i === data.length - 1 || i % 3 === 0) ? `${parseInt(parts[1])}/${parseInt(parts[2])}` : ''
	})
	const map = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
	return data.map(r => { const d = new Date(r.date); return map[d.getDay()] })
})

// ── 导航 ──
const goDetail = (type) => { uni.navigateTo({ url: `/pages/detail/index?type=${type}` }) }
const goAI = () => { uni.switchTab({ url: '/pages/ai/index' }) }
const goScoreDetail = () => { uni.navigateTo({ url: '/pages/score-detail/index' }) }

// ── 数据加载 ──
onMounted(async () => {
	uni.showTabBar()
	await loadDashboardData()
})

onShow(async () => {
	healthGoals.value = uni.getStorageSync('healthGoals') || { steps: 10000, sleep: 8, water: 8 }
	uni.$on('recordUpdated', loadDashboardData)
	if (!dataLoaded.value) return
	await loadDashboardData()
})

// 下拉刷新
onPullDownRefresh(async () => {
	await loadDashboardData()
	uni.stopPullDownRefresh()
})

async function loadDashboardData() {
	const today = new Date()
	const weekAgo = new Date(today); weekAgo.setDate(today.getDate() - 6)
	const monthAgo = new Date(today); monthAgo.setDate(today.getDate() - 30)

	const todayStr = fmtDate(today)
	const weekAgoStr = fmtDate(weekAgo)
	const monthAgoStr = fmtDate(monthAgo)

	try {
		const [profile, records, trendRecords] = await Promise.all([
			getProfile().catch(() => null),
			fetchRecords(weekAgoStr, todayStr),
			fetchRecords(monthAgoStr, todayStr),
		])

		if (profile) userName.value = profile.nickname || profile.username || '用户'
		else { const info = uni.getStorageSync('userInfo'); if (info) userName.value = info.nickname || info.username || '用户' }

		if (records && records.length) {
			weekRecords.value = records
			const todayRec = records.find(r => r.date === todayStr)
			if (todayRec) { todayRecord.value = todayRec; healthScore.value = todayRec.healthScore || calcHealthScore(todayRec) }
		}

		if (trendRecords && trendRecords.length) trendAllRecords.value = trendRecords

		dataLoaded.value = true

		// 加载 AI 洞察
		if (todayRecord.value && Object.keys(todayRecord.value).length) loadAIInsight()
	} catch (e) { console.warn('[Dashboard] 加载失败:', e) }
}

async function loadAIInsight() {
	aiLoading.value = true
	try {
		const t = todayRecord.value
		const dims = dimScores.value
		const best = [...dims].sort((a, b) => b.value - a.value)[0]
		const worst = [...dims].sort((a, b) => a.value - b.value)[dims.length - 1]
		const res = await fetchAIInsight({
			steps: t.steps || 0, sleep: t.sleep || 0, heart: t.hrAvg || t.heartRate || 0,
			water: t.water || 0, exercise: t.exercise || 0, score: healthScore.value,
			level: healthLevel.value, best: best?.label || '', worst: worst?.label || '',
		})
		if (res && res.insight) aiInsight.value = res.insight
	} catch (e) { /* AI 不可用，保持空状态 */ }
	aiLoading.value = false
}

function calcHealthScore(rec) {
	const steps = rec.steps || 0; const hr = rec.hrAvg || rec.heartRate || 70
	const sleep = rec.sleep || 0; const water = rec.water || 0
	const exercise = rec.exercise || 0; const mood = rec.mood || 70
	return Math.round(
		Math.min(100, Math.round((steps / healthGoals.value.steps) * 100)) * 0.25 +
		Math.max(0, Math.min(100, Math.round(100 - Math.abs(hr - 70) * 2.5))) * 0.2 +
		Math.min(100, Math.round((sleep / healthGoals.value.sleep) * 100)) * 0.2 +
		Math.min(100, Math.round((water / healthGoals.value.water) * 100)) * 0.1 +
		Math.min(100, Math.round((exercise / 60) * 100)) * 0.15 + mood * 0.1
	)
}
</script>

<style scoped lang="scss">
$bg: #F5F7FA; $white: #FFFFFF; $text-1: #1A1A2E; $text-2: #555; $text-3: #999;
$grad-start: #6B73FF; $grad-end: #3B27FE;
$green: #4CAF50; $purple: #7C3AED; $red: #EF4444; $blue: #3B82F6;
$card-radius: 24rpx;
$shadow-card: 0 4px 24px rgba(0,0,0,0.05);

.page { background: $bg; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

// ── Hero ──
.hero-bg { background: linear-gradient(135deg, $grad-start 0%, $grad-end 100%); height: 28vh; border-radius: 0 0 48rpx 48rpx; }
.hero-content { display: flex; flex-direction: row; justify-content: space-between; align-items: flex-start; padding: 24rpx 36rpx 0; }
.hero-left { display: flex; flex-direction: column; }
.hero-greeting { font-size: 40rpx; font-weight: 700; color: #fff; }
.hero-date { font-size: 24rpx; color: rgba(255,255,255,0.7); margin-top: 8rpx; }
.hero-avatar { width: 80rpx; height: 80rpx; border-radius: 50%; background: rgba(255,255,255,0.2); border: 2rpx solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; }
.hero-avatar-text { font-size: 34rpx; font-weight: 700; color: #fff; }

// ── Scroll ──
.scroll-body { flex: 1; height: 0; padding: 0 24rpx; margin-top: -60rpx; position: relative; z-index: 2; }

// ── 1. 健康评分 ──
.score-card { background: $white; border-radius: $card-radius; padding: 32rpx; margin-bottom: 20rpx; box-shadow: $shadow-card; }
.score-row { display: flex; flex-direction: row; align-items: flex-start; gap: 24rpx; }
.score-ring-col { flex-shrink: 0; }
.ring-wrap { position: relative; width: 170rpx; height: 170rpx; display: flex; align-items: center; justify-content: center; }
.ring-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.ring-arc { transition: stroke-dashoffset 1.2s ease; }
.ring-center { text-align: center; }
.ring-num { font-size: 48rpx; font-weight: 900; color: $text-1; display: block; line-height: 1; }
.ring-label { font-size: 20rpx; color: $text-3; margin-top: 4rpx; display: block; }

.score-detail { flex: 1; display: flex; flex-direction: column; gap: 12rpx; }
.score-header { display: flex; flex-direction: row; align-items: center; gap: 14rpx; }
.score-level { font-size: 34rpx; font-weight: 800; color: $text-1; }
.score-trend { display: flex; flex-direction: row; align-items: center; gap: 2rpx; background: #E8F5E9; padding: 4rpx 12rpx; border-radius: 999rpx; }
.score-trend-arrow { font-size: 22rpx; color: $green; font-weight: 700; }
.score-trend-val { font-size: 22rpx; color: $green; font-weight: 700; }

.score-dims { display: flex; flex-direction: column; gap: 8rpx; }
.sd-row { display: flex; flex-direction: row; align-items: center; gap: 8rpx; }
.sd-label { font-size: 22rpx; color: $text-2; width: 100rpx; flex-shrink: 0; }
.sd-track { flex: 1; height: 8rpx; background: #F1F5F9; border-radius: 4rpx; overflow: hidden; }
.sd-fill { height: 100%; border-radius: 4rpx; background: #CBD5E1; transition: width 1s ease; }
.sd-fill.sd-best { background: $green; }
.sd-fill.sd-worst { background: #F59E0B; }
.sd-val { font-size: 20rpx; color: $text-3; width: 44rpx; text-align: right; font-weight: 500; }
.sd-val-best { color: $green; font-weight: 700; }
.sd-val-worst { color: #F59E0B; font-weight: 700; }

.score-arrow-hint { text-align: right; font-size: 22rpx; color: $text-3; }

// ── 2. AI ──
.ai-card { background: $white; border-radius: $card-radius; padding: 28rpx; margin-bottom: 20rpx; box-shadow: $shadow-card; }
.ai-header { display: flex; flex-direction: row; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.ai-title { font-size: 30rpx; font-weight: 700; color: $text-1; }
.ai-more { font-size: 24rpx; color: $text-3; }
.ai-body { display: flex; flex-direction: row; align-items: flex-start; gap: 14rpx; background: #F4F4FF; border-radius: 16rpx; padding: 20rpx; }
.ai-icon { font-size: 32rpx; flex-shrink: 0; margin-top: 4rpx; }
.ai-text { font-size: 26rpx; color: $text-2; line-height: 1.7; flex: 1; }
.ai-loading-text { font-size: 26rpx; color: $text-3; }

// ── 3. Metrics Grid ──
.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin-bottom: 20rpx; }
.metric-cell { background: $white; border-radius: $card-radius; padding: 24rpx 20rpx; box-shadow: $shadow-card; display: flex; flex-direction: column; &:active { transform: scale(0.97); } }
.mc-header { display: flex; flex-direction: row; align-items: center; gap: 8rpx; margin-bottom: 12rpx; }
.mc-icon { width: 44rpx; height: 44rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; font-size: 24rpx; }
.mc-title { font-size: 26rpx; font-weight: 600; color: $text-1; flex: 1; }
.mc-arrow { font-size: 28rpx; color: $text-3; }
.mc-body { display: flex; flex-direction: row; align-items: center; justify-content: space-between; margin-bottom: 8rpx; }
.mc-main-info { display: flex; flex-direction: row; align-items: baseline; gap: 4rpx; }
.mc-value { font-size: 48rpx; font-weight: 800; color: $text-1; line-height: 1; }
.mc-unit { font-size: 22rpx; color: $text-3; }
.mc-target { font-size: 20rpx; color: $text-3; }

.mc-arc-progress { position: relative; width: 70rpx; height: 70rpx; display: flex; align-items: center; justify-content: center; }
.mc-arc-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.mc-arc-pct { font-size: 20rpx; font-weight: 700; color: $green; }

.mc-quality-tag { font-size: 20rpx; font-weight: 600; padding: 4rpx 12rpx; border-radius: 999rpx; }
.tag-good { background: #EDE9FE; color: $purple; }
.tag-fair { background: #FEF3C7; color: #D97706; }
.tag-poor { background: #FEE2E2; color: $red; }

.mc-water-dots { display: flex; flex-direction: row; gap: 6rpx; }
.water-dot { width: 16rpx; height: 16rpx; border-radius: 50%; background: #E8ECF1; }
.water-dot.filled { background: $blue; }

.mini-bars { display: flex; flex-direction: row; align-items: flex-end; gap: 6rpx; height: 50rpx; margin-top: 14rpx; }
.green-bars .mini-bar { background: $green; }
.purple-bars .mini-bar { background: $purple; }
.blue-bars .mini-bar { background: $blue; }
.mini-bar { flex: 1; border-radius: 4rpx 4rpx 0 0; min-height: 4rpx; opacity: 0.6; &:last-child { opacity: 1; } }

// ── 4. Trend ──
.trend-card { background: $white; border-radius: $card-radius; padding: 28rpx 24rpx 20rpx; margin-bottom: 20rpx; box-shadow: $shadow-card; }
.trend-header { display: flex; flex-direction: row; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.trend-title { font-size: 30rpx; font-weight: 700; color: $text-1; }
.trend-toggles { display: flex; flex-direction: column; align-items: flex-end; gap: 8rpx; }
.trend-hr-toggle { display: flex; flex-direction: row; background: #F1F5F9; border-radius: 16rpx; padding: 3rpx; }
.thr-tab { padding: 6rpx 14rpx; border-radius: 14rpx; font-size: 20rpx; color: $text-3; font-weight: 500; }
.thr-tab.active { background: $blue; color: #fff; font-weight: 600; }
.trend-toggle { display: flex; flex-direction: row; background: #F1F5F9; border-radius: 24rpx; padding: 4rpx; }
.trend-tab { padding: 10rpx 24rpx; border-radius: 20rpx; font-size: 24rpx; color: $text-3; font-weight: 500; }
.trend-tab.active { background: $blue; color: #fff; font-weight: 600; }

.trend-chart { display: flex; flex-direction: row; gap: 10rpx; }
.trend-y-axis { display: flex; flex-direction: column; justify-content: space-between; padding: 0 0 20rpx; font-size: 18rpx; color: $text-3; width: 36rpx; text-align: right; }
.trend-plot { flex: 1; }
.trend-svg { width: 100%; height: 240rpx; }
.trend-x-axis { display: flex; flex-direction: row; justify-content: space-between; padding: 8rpx 0 0 46rpx; font-size: 20rpx; color: $text-3; }

.bottom-spacer { height: 24rpx; }
</style>
