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
				<text class="ex-type">{{ item.exercise_type || '运动' }}</text>
				<text class="ex-duration">{{ item.exercise }}分钟</text>
				<text class="ex-cal">{{ calcCalories(item.exercise_type, item.exercise) }}千卡</text>
			</view>
		</view>
	</view>
</template>

<script>
import { fetchRecords, calcExerciseCalories } from '@/utils/api'
import { getWeekRange } from '@/utils/mock'

export default {
	data() {
		return {
			loading: true,
			exerciseList: []
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
				const t = r.exercise_type || '其他'
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
			return this.weekRecords.reduce((sum, r) => sum + calcExerciseCalories(r.exercise_type, r.exercise), 0)
		}
	},
	onShow() {
		this.loadData()
	},
	methods: {
		loadData() {
			this.loading = true
			const today = new Date()
			const start = new Date(today)
			start.setDate(today.getDate() - 30)
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
}

.glass-card {
	background: rgba(255,255,255,0.75);
	backdrop-filter: blur(20px);
	border-radius: 20px;
	padding: 32rpx;
	margin-bottom: 24rpx;
	box-shadow: 0 8px 32px rgba(0,0,0,0.08);
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

.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

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

.stat-unit {
	font-size: 22rpx;
	color: #999;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
	margin-top: 4rpx;
	display: block;
}

.stat-divider {
	width: 1px;
	height: 60rpx;
	background: #eee;
}

.empty-list {
	padding: 60rpx 0;
	text-align: center;
}

.empty-text { font-size: 26rpx; color: #bbb; }

.exercise-item {
	display: flex;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1px solid #f5f5f5;
}

.exercise-item:last-child { border-bottom: none; }

.ex-date {
	flex: 1;
	font-size: 26rpx;
	color: #666;
}

.ex-type {
	font-size: 26rpx;
	color: #333;
	width: 120rpx;
}

.ex-duration {
	font-size: 26rpx;
	color: #667eea;
	font-weight: 500;
}

.ex-cal {
	font-size: 24rpx;
	color: #FF6B6B;
	font-weight: 500;
	width: 100rpx;
	text-align: right;
}
</style>
