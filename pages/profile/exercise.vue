<template>
	<view class="exercise-page">
		<view v-if="loading" class="loading-overlay">
			<view class="loading-spinner"></view>
		</view>

		<!-- 本周统计 -->
		<view class="stats-card glass-card">
			<text class="card-title">本周运动</text>
			<view class="stats-row">
				<view class="stat-item">
					<text class="stat-num">{{ weekTotalDuration }}</text>
					<text class="stat-unit">分钟</text>
					<text class="stat-label">总时长</text>
				</view>
				<view class="stat-divider"></view>
				<view class="stat-item">
					<text class="stat-num">{{ weekTotalDays }}</text>
					<text class="stat-unit">天</text>
					<text class="stat-label">运动天数</text>
				</view>
				<view class="stat-divider"></view>
				<view class="stat-item">
					<text class="stat-num">{{ mostType }}</text>
					<text class="stat-unit"></text>
					<text class="stat-label">最常见类型</text>
				</view>
				<view class="stat-divider"></view>
				<view class="stat-item">
					<text class="stat-num">{{ weekTotalCalories }}</text>
					<text class="stat-unit">千卡</text>
					<text class="stat-label">总消耗</text>
				</view>
			</view>
		</view>

		<!-- 运动分布雷达图 -->
		<view class="radar-card glass-card">
			<view class="radar-header">
				<text class="card-title">运动分布</text>
				<view class="trend-toggle">
					<text v-for="t in ['日','周','月']" :key="t" class="trend-tab" :class="{ active: radarActive === t }"
						@click="radarActive = t">{{ t }}</text>
				</view>
			</view>
			<view v-if="radarChartData" class="radar-chart-wrap">
				<qiun-data-charts type="radar" :chartData="radarChartData" :opts="radarChartOpts" height="420rpx" />
			</view>
			<view v-else class="empty-chart">
				<text class="empty-text">{{ radarActive === '日' ? '今天还没有运动哦' : '暂无运动数据' }}</text>
			</view>
		</view>

		<!-- 运动记录列表 -->
		<view class="list-card glass-card">
			<view class="card-header">
				<text class="card-title">运动记录</text>
			</view>
			<view v-if="exerciseList.length === 0" class="empty-list">
				<text class="empty-text">暂无运动记录</text>
			</view>
			<view v-for="(item, i) in exerciseList" :key="i" class="exercise-item">
				<text class="ex-date">{{ item.date }}</text>
				<text class="ex-type">{{ item.exerciseType || '运动' }}</text>
				<text class="ex-duration">{{ item.exercise }}分钟</text>
				<text class="ex-cal">{{ calcCalories(item.exerciseType, item.exercise) }}千卡</text>
			</view>
		</view>
	</view>
</template>

<script>
import { fetchRecords, calcExerciseCalories } from '@/utils/api'
import { getWeekRange } from '@/utils/mock'

const ALL_TYPES = ['跑步','骑行','瑜伽','游泳','力量训练','篮球','足球','羽毛球','乒乓球','跳绳','快走','散步','其他']

export default {
	data() {
		return {
			loading: true,
			exerciseList: [],
			radarActive: '周',
		}
	},
	computed: {
		weekRecords() {
			const range = getWeekRange(new Date())
			const weekStart = range.start
			weekStart.setHours(0,0,0,0)
			return this.exerciseList.filter(r => {
				const d = new Date(r.date)
				return d >= weekStart
			})
		},
		weekTotalDuration() {
			return this.weekRecords.reduce((sum, r) => sum + (r.exercise || 0), 0)
		},
		weekTotalDays() {
			const days = new Set()
			this.weekRecords.forEach(r => days.add(r.date))
			return days.size
		},
		mostType() {
			const types = {}
			this.weekRecords.forEach(r => {
				const t = r.exerciseType || '其他'
				types[t] = (types[t] || 0) + 1
			})
			let maxType = '无'
			let maxCount = 0
			for (const [t, c] of Object.entries(types)) {
				if (c > maxCount) { maxType = t; maxCount = c }
			}
			return maxType
		},
		weekTotalCalories() {
			return this.weekRecords.reduce((sum, r) => sum + calcExerciseCalories(r.exerciseType, r.exercise), 0)
		},
		// 雷达图 —— 按选中范围聚合运动时长，取 Top 6
		radarTopTypes() {
			const now = new Date()
			let start
			if (this.radarActive === '日') { start = new Date(now); start.setHours(0,0,0,0) }
			else if (this.radarActive === '月') { start = new Date(now); start.setDate(now.getDate() - 30) }
			else { const d = new Date(now); d.setDate(now.getDate() - 6); start = d }

			const filtered = this.exerciseList.filter(r => new Date(r.date) >= start)
			const agg = {}
			filtered.forEach(r => {
				const t = r.exerciseType || '其他'
				agg[t] = (agg[t] || 0) + (r.exercise || 0)
			})
			const sorted = Object.entries(agg).sort((a, b) => b[1] - a[1])
			return sorted.slice(0, 6)
		},
		radarChartData() {
			if (!this.radarTopTypes.length) return null
			return {
				categories: this.radarTopTypes.map(e => e[0]),
				series: [{ name: '运动时长', data: this.radarTopTypes.map(e => e[1]) }]
			}
		},
		radarChartOpts() {
			const max = Math.max(...this.radarTopTypes.map(e => e[1]), 1)
			const roundMax = Math.ceil(max / 10) * 10
			return {
				padding: [20, 20, 10, 20],
				legend: { show: false },
				dataLabel: false,
				color: ['#667eea'],
				background: 'transparent',
				extra: {
					radar: {
						gridType: 'radar',
						gridColor: '#E8ECF1',
						gridCount: 4,
						opacity: 0.2,
						max: roundMax,
						labelColor: '#999',
						labelFontSize: 11,
					}
				}
			}
		},
	},
	onShow() {
		this.loadData()
	},
	methods: {
		loadData() {
			this.loading = true
			const today = new Date()
			const start = new Date(today)
			start.setDate(today.getDate() - 90)
			const fmt = (d) => d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
			fetchRecords(fmt(start), fmt(today)).then(data => {
				this.exerciseList = (data || []).filter(r => r.exercise && r.exercise > 0)
			}).catch(() => {}).finally(() => {
				this.loading = false
			})
		},
		calcCalories(type, minutes) {
			return calcExerciseCalories(type, minutes)
		}
	}
}
</script>

<style lang="scss">
.exercise-page {
	padding: 24rpx;
	min-height: 100vh;
	background: var(--page-bg);
	transition: background 0.3s;
}

.glass-card {
	background: var(--card-bg-glass);
	backdrop-filter: blur(20px);
	border-radius: 20px;
	padding: 32rpx;
	margin-bottom: 24rpx;
	box-shadow: var(--shadow-glass);
	transition: background 0.3s, box-shadow 0.3s;
}

.loading-overlay {
	position: fixed;
	inset: 0;
	background: rgba(255,255,255,0.8);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 100;
}

.loading-spinner {
	width: 60rpx;
	height: 60rpx;
	border: 4rpx solid #eee;
	border-top-color: #667eea;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

.card-title { font-size: 30rpx; font-weight: 600; color: var(--text-1); }

.card-header { margin-bottom: 16rpx; }

.stats-row {
	display: flex;
	align-items: center;
	margin-top: 20rpx;
}

.stat-item {
	flex: 1;
	text-align: center;
}

.stat-num {
	font-size: 36rpx;
	font-weight: bold;
	color: #667eea;
}

.stat-unit { font-size: 22rpx; color: var(--text-3); }
.stat-label { font-size: 22rpx; color: var(--text-3); margin-top: 4rpx; display: block; }

.stat-divider {
	width: 1px;
	height: 60rpx;
	background: var(--divider);
}

// 雷达图
.radar-card { }
.radar-header {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}
.trend-toggle {
	display: flex;
	flex-direction: row;
	background: var(--input-bg);
	border-radius: 24rpx;
	padding: 4rpx;
}
.trend-tab {
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	color: var(--text-3);
	font-weight: 500;
}
.trend-tab.active { background: #667eea; color: #fff; font-weight: 600; }

.radar-chart-wrap { margin-top: 8rpx; }
.empty-chart { padding: 80rpx 0; text-align: center; }

.empty-list { padding: 60rpx 0; text-align: center; }
.empty-text { font-size: 26rpx; color: #bbb; }

.exercise-item {
	display: flex;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1px solid var(--divider);
}

.exercise-item:last-child { border-bottom: none; }

.ex-date { flex: 1; font-size: 26rpx; color: var(--text-2); }
.ex-type { font-size: 26rpx; color: var(--text-1); width: 120rpx; }
.ex-duration { font-size: 26rpx; color: #667eea; font-weight: 500; }
.ex-cal { font-size: 24rpx; color: #FF6B6B; font-weight: 500; width: 100rpx; text-align: right; }
</style>
