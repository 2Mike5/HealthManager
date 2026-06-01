<template>
	<view class="page">
		<view class="hero">
			<view class="hero-back" @click="goBack"><text>‹</text></view>
			<text class="hero-title">📊 健康周报</text>
			<text class="hero-date">{{ weekLabel }}</text>
		</view>

		<scroll-view scroll-y="true" class="body" show-scrollbar="false">
			<!-- 综合评分 -->
			<view class="score-hero">
				<text class="sh-big">{{ weekAvgScore }}</text>
				<text class="sh-unit">分</text>
				<view class="sh-trend" v-if="scoreChange !== 0">
					<text :class="scoreChange > 0 ? 'c-green' : 'c-red'">{{ scoreChange > 0 ? '↑' : '↓' }}{{ Math.abs(scoreChange) }}</text>
					<text class="sh-trend-label">较上周</text>
				</view>
			</view>

			<!-- 四项指标对比 -->
			<view class="compare-grid">
				<view class="cg-item" v-for="m in compareMetrics" :key="m.key">
					<text class="cg-icon">{{ m.icon }}</text>
					<text class="cg-label">{{ m.label }}</text>
					<text class="cg-val">{{ m.thisWeek }}</text>
					<text class="cg-unit">{{ m.unit }}</text>
					<view class="cg-change" v-if="m.change !== 0">
						<text :class="m.change > 0 ? 'c-green' : 'c-red'">{{ m.change > 0 ? '↑' : '↓' }}{{ Math.abs(m.change) }}%</text>
					</view>
					<text class="cg-vs" v-else>持平</text>
					<!-- 迷你趋势条 -->
					<view class="cg-mini-bars">
						<view v-for="(h, i) in m.bars" :key="i" class="cg-bar" :style="{ height: h + 'rpx', background: m.color }"></view>
					</view>
				</view>
			</view>

			<!-- AI 总结 -->
			<view class="ai-summary-card">
				<text class="as-title">🤖 AI 本周总结</text>
				<text class="as-text">{{ aiLoading ? 'AI 正在生成总结...' : aiSummary }}</text>
			</view>

			<!-- 每日详情 -->
			<view class="daily-card">
				<text class="as-title">📋 每日记录</text>
				<view class="daily-row" v-for="d in dailyList" :key="d.date">
					<text class="dr-date">{{ d.dayLabel }}</text>
					<text class="dr-steps">🚶{{ d.steps }}</text>
					<text class="dr-sleep">💤{{ d.sleep }}h</text>
					<text class="dr-score">{{ d.score }}分</text>
				</view>
			</view>

			<view class="bottom-spacer"></view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecords, getProfile } from '@/utils/api'

const fmtDate = (d) => {
	const y = d.getFullYear()
	const m = String(d.getMonth() + 1).padStart(2, '0')
	const day = String(d.getDate()).padStart(2, '0')
	return `${y}-${m}-${day}`
}

const weekLabel = ref('')
const weekAvgScore = ref(0)
const scoreChange = ref(0)
const aiSummary = ref('')
const aiLoading = ref(false)
const dailyList = ref([])

const compareMetrics = computed(() => {
	const cur = currentWeekData.value
	const prev = prevWeekData.value
	const avg = (arr, key) => {
		const vals = arr.filter(r => r[key] != null).map(r => r[key])
		return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length * 10) / 10 : 0
	}
	const pctChange = (curVal, prevVal) => prevVal ? Math.round((curVal - prevVal) / prevVal * 100) : 0
	const normBars = (arr, key, maxH = 36) => {
		const vals = arr.map(r => r[key] || 0)
		const max = Math.max(...vals, 1)
		return vals.map(v => Math.max(3, (v / max) * maxH))
	}

	const curSteps = Math.round(avg(cur, 'steps'))
	const prevSteps = Math.round(avg(prev, 'steps'))
	const curSleep = avg(cur, 'sleep')
	const prevSleep = avg(prev, 'sleep')
	const curHr = Math.round(avg(cur, 'hrAvg'))
	const prevHr = Math.round(avg(prev, 'hrAvg'))
	const curWater = Math.round(avg(cur, 'water'))
	const prevWater = Math.round(avg(prev, 'water'))

	return [
		{ key: 'steps', icon: '🚶', label: '步数', thisWeek: curSteps.toLocaleString(), unit: '步', change: pctChange(curSteps, prevSteps), color: '#4CAF50', bars: normBars(cur, 'steps') },
		{ key: 'sleep', icon: '💤', label: '睡眠', thisWeek: curSleep, unit: 'h', change: pctChange(curSleep, prevSleep), color: '#7C3AED', bars: normBars(cur, 'sleep') },
		{ key: 'heart', icon: '❤️', label: '心率', thisWeek: curHr, unit: 'bpm', change: -pctChange(curHr, prevHr), color: '#EF4444', bars: normBars(cur, 'hrAvg').map(v => v * 0.6) },
		{ key: 'water', icon: '💧', label: '饮水', thisWeek: curWater, unit: '杯', change: pctChange(curWater, prevWater), color: '#3B82F6', bars: normBars(cur, 'water') },
	]
})

const currentWeekData = ref([])
const prevWeekData = ref([])

// ── 数据加载 ──
onMounted(async () => {
	const now = new Date()
	const dayOfWeek = now.getDay()
	const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
	const thisMonday = new Date(now); thisMonday.setDate(now.getDate() + mondayOffset)
	const thisSunday = new Date(thisMonday); thisSunday.setDate(thisMonday.getDate() + 6)
	const lastMonday = new Date(thisMonday); lastMonday.setDate(thisMonday.getDate() - 7)
	const lastSunday = new Date(thisSunday); lastSunday.setDate(thisSunday.getDate() - 7)

	weekLabel.value = `${thisMonday.getMonth()+1}/${thisMonday.getDate()} - ${thisSunday.getMonth()+1}/${thisSunday.getDate()}`

	try {
		const [curData, prevData] = await Promise.all([
			fetchRecords(fmtDate(thisMonday), fmtDate(thisSunday)),
			fetchRecords(fmtDate(lastMonday), fmtDate(lastSunday)),
		])
		currentWeekData.value = curData || []
		prevWeekData.value = prevData || []

		// 计算评分
		const curScores = (curData || []).filter(r => r.healthScore != null).map(r => r.healthScore)
		const prevScores = (prevData || []).filter(r => r.healthScore != null).map(r => r.healthScore)
		const curAvg = curScores.length ? Math.round(curScores.reduce((a, b) => a + b, 0) / curScores.length) : 0
		const prevAvg = prevScores.length ? Math.round(prevScores.reduce((a, b) => a + b, 0) / prevScores.length) : 0
		weekAvgScore.value = curAvg
		scoreChange.value = prevAvg ? curAvg - prevAvg : 0

		// 每日列表
		const map = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
		dailyList.value = (curData || []).map(r => ({
			date: r.date,
			dayLabel: `${r.date.slice(5)} ${map[new Date(r.date).getDay()]}`,
			steps: (r.steps || 0).toLocaleString(),
			sleep: (r.sleep || 0).toFixed(1),
			score: r.healthScore || '--',
		}))

		// AI 总结
		loadAISummary()
	} catch (e) { console.warn('[Report] 加载失败:', e) }
})

async function loadAISummary() {
	aiLoading.value = true
	const m = compareMetrics.value
	const upItems = m.filter(x => x.change > 0).map(x => x.label)
	const downItems = m.filter(x => x.change < 0).map(x => x.label)
	const prompt = `作为健康助手，请根据以下本周健康数据生成一段50字以内的温暖鼓励性总结：
本周平均评分${weekAvgScore.value}分（较上周${scoreChange.value > 0 ? '上升' : '下降'}${Math.abs(scoreChange.value)}分）。
提升的指标：${upItems.join('、') || '无'}。
下降的指标：${downItems.join('、') || '无'}。
请给出具体鼓励和建议。`
	try {
		const res = await uni.request({
			url: 'http://192.168.20.41:5001/api/ai/query',
			method: 'POST',
			data: { question: prompt },
			timeout: 15000,
		})
		if (res.data && res.data.code === 200 && res.data.data) {
			aiSummary.value = res.data.data.answer || ''
		}
	} catch (e) {}
	aiLoading.value = false
	if (!aiSummary.value) {
		aiSummary.value = `本周综合评分 ${weekAvgScore.value} 分，各项指标整体平稳。继续保持健康的生活习惯！`
	}
}

const goBack = () => uni.navigateBack()
</script>

<style scoped lang="scss">
$green: #4CAF50; $red: #EF4444;

.page { background: var(--page-bg); min-height: 100vh; transition: background 0.3s; }
.hero { background: linear-gradient(135deg, var(--hero-bg-start), var(--hero-bg-end)); padding: 24rpx 32rpx 32rpx; }
.hero-back { width: 56rpx; height: 56rpx; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 12rpx; font-size: 40rpx; color: #fff; }
.hero-title { font-size: 44rpx; font-weight: 800; color: #fff; display: block; }
.hero-date { font-size: 24rpx; color: rgba(255,255,255,0.6); display: block; margin-top: 6rpx; }
.body { padding: 0 24rpx; }

// Score hero
.score-hero { display: flex; flex-direction: row; align-items: baseline; justify-content: center; gap: 8rpx; padding: 32rpx 0 20rpx; }
.sh-big { font-size: 80rpx; font-weight: 900; color: var(--text-1); }
.sh-unit { font-size: 28rpx; color: var(--text-3); }
.sh-trend { display: flex; flex-direction: column; align-items: center; margin-left: 16rpx; font-size: 32rpx; font-weight: 700; }
.sh-trend-label { font-size: 20rpx; color: var(--text-3); font-weight: 400; }
.c-green { color: $green; }
.c-red { color: $red; }

// Compare grid
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin-bottom: 20rpx; }
.cg-item { background: var(--card-bg); border-radius: 20rpx; padding: 20rpx; text-align: center; box-shadow: var(--shadow-card); transition: background 0.3s; }
.cg-icon { font-size: 32rpx; display: block; }
.cg-label { font-size: 22rpx; color: var(--text-3); display: block; margin-top: 4rpx; }
.cg-val { font-size: 40rpx; font-weight: 800; color: var(--text-1); display: block; margin-top: 6rpx; }
.cg-unit { font-size: 20rpx; color: var(--text-3); }
.cg-change { font-size: 24rpx; font-weight: 700; margin-top: 4rpx; }
.cg-vs { font-size: 22rpx; color: var(--text-3); margin-top: 4rpx; }
.cg-mini-bars { display: flex; flex-direction: row; align-items: flex-end; gap: 4rpx; height: 40rpx; margin-top: 10rpx; }
.cg-bar { flex: 1; border-radius: 3rpx 3rpx 0 0; min-height: 3rpx; opacity: 0.6; &:last-child { opacity: 1; } }

// AI & Daily cards
.ai-summary-card, .daily-card { background: var(--card-bg); border-radius: 20rpx; padding: 24rpx; margin-bottom: 20rpx; box-shadow: var(--shadow-card); transition: background 0.3s; }
.as-title { font-size: 28rpx; font-weight: 700; color: var(--text-1); display: block; margin-bottom: 12rpx; }
.as-text { font-size: 26rpx; color: var(--text-2); line-height: 1.7; }

.daily-row { display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 14rpx 0; border-bottom: 1px solid var(--divider); }
.dr-date { font-size: 24rpx; color: var(--text-2); width: 160rpx; }
.dr-steps { font-size: 24rpx; color: var(--text-1); }
.dr-sleep { font-size: 24rpx; color: var(--text-1); }
.dr-score { font-size: 24rpx; font-weight: 600; color: #6B73FF; width: 70rpx; text-align: right; }

.bottom-spacer { height: 40rpx; }
</style>
