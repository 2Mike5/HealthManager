<template>
	<view class="weight-page">
		<view v-if="loading" class="loading-overlay">
			<view class="loading-spinner"></view>
		</view>

		<!-- 当前体重卡片 -->
		<view class="current-card glass-card">
			<view class="current-row">
				<view class="current-left">
					<text class="current-label">当前体重</text>
					<text class="current-value">{{ latest ? latest.weight : '--' }}<text class="current-unit"> kg</text></text>
				</view>
				<view class="current-right" v-if="latest && latest.bmi">
					<text class="bmi-value">{{ latest.bmi }}</text>
					<text class="bmi-label" :class="bmiClass">{{ latest.bmi_label }}</text>
				</view>
			</view>
			<!-- 目标进度 -->
			<view v-if="targetWeight" class="target-row">
				<text class="target-text">目标: {{ targetWeight }}kg</text>
				<view class="progress-bg">
					<view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
				</view>
				<text class="target-diff">{{ diffText }}</text>
			</view>
		</view>

		<!-- 体重趋势图 -->
		<view class="chart-card glass-card">
			<view class="card-header">
				<text class="card-title">体重趋势</text>
			</view>
			<view v-if="chartData" class="chart-wrap">
				<qiun-data-charts type="line" :chartData="chartData" :opts="chartOpts" height="400rpx" />
			</view>
			<view v-else class="empty-chart">
				<text class="empty-text">暂无体重数据，快去记录吧</text>
			</view>
		</view>

		<!-- 快速添加 -->
		<view class="add-card glass-card">
			<text class="card-title">记录体重</text>
			<view class="add-row">
				<input class="add-input" v-model="newWeight" type="digit" placeholder="体重 (kg)" placeholder-class="ph" />
				<input class="add-input" v-model="newFat" type="digit" placeholder="体脂% (可选)" placeholder-class="ph" />
				<button class="add-btn" @tap="addWeight">记录</button>
			</view>
		</view>

		<!-- 历史列表 -->
		<view class="history-card glass-card">
			<view class="card-header">
				<text class="card-title">历史记录</text>
			</view>
			<view v-if="records.length === 0" class="empty-list">
				<text class="empty-text">暂无记录</text>
			</view>
			<view v-for="(r, i) in records" :key="r.id" class="history-item" :style="{ animationDelay: i * 0.05 + 's' }">
				<text class="history-date">{{ r.date }}</text>
				<text class="history-weight">{{ r.weight }} kg</text>
				<text v-if="r.body_fat" class="history-fat">体脂 {{ r.body_fat }}%</text>
			</view>
		</view>
	</view>
</template>

<script>
import { fetchWeightRecords, createWeightRecord, getLatestWeight, getProfile } from '@/utils/api'

export default {
	data() {
		return {
			loading: true,
			records: [],
			latest: null,
			targetWeight: null,
			newWeight: '',
			newFat: ''
		}
	},
	computed: {
		chartData() {
			if (!this.records || this.records.length < 2) return null
			const sorted = [...this.records].sort((a, b) => a.date.localeCompare(b.date))
			return {
				categories: sorted.map(r => r.date.slice(5)),
				series: [{ name: '体重', data: sorted.map(r => r.weight) }]
			}
		},
		chartOpts() {
			return {
				padding: [20, 15, 10, 40],
				legend: { show: false },
				dataLabel: false,
				color: ['#7C4DFF'],
				background: 'transparent',
				xAxis: { labelCount: 5, scrollShow: true, scrollAlign: 'left' },
				yAxis: { data: [{ min: 0 }] },
				extra: {
					line: { type: 'curve', width: 3 },
					tooltip: { showBox: true, showLabel: true }
				}
			}
		},
		bmiClass() {
			if (!this.latest || !this.latest.bmi_label) return ''
			const map = { '偏瘦': 'bmi-low', '正常': 'bmi-normal', '超重': 'bmi-high', '肥胖': 'bmi-danger' }
			return map[this.latest.bmi_label] || ''
		},
		progressPercent() {
			if (!this.latest || !this.targetWeight) return 0
			const diff = this.targetWeight - (this.latest.weight || 0)
			return Math.min(100, Math.max(0, diff / this.targetWeight * 100))
		},
		diffText() {
			if (!this.latest || !this.targetWeight) return ''
			const diff = this.latest.weight - this.targetWeight
			if (Math.abs(diff) < 0.5) return '已达目标!'
			return diff > 0 ? '还需减 ' + diff.toFixed(1) + 'kg' : '超过目标 ' + Math.abs(diff).toFixed(1) + 'kg'
		}
	},
	onShow() {
		this.loadData()
	},
	methods: {
		loadData() {
			this.loading = true
			Promise.all([
				fetchWeightRecords(),
				getLatestWeight(),
				getProfile()
			]).then(([records, latest, profile]) => {
				this.records = records || []
				this.latest = latest
				this.targetWeight = profile.target_weight
			}).catch(() => {}).finally(() => {
				this.loading = false
			})
		},
		addWeight() {
			const weight = parseFloat(this.newWeight)
			if (!weight || weight <= 0) {
				uni.showToast({ title: '请输入有效体重', icon: 'none' })
				return
			}
			const data = { weight }
			if (this.newFat) data.body_fat = parseFloat(this.newFat)

			createWeightRecord(data).then(() => {
				uni.showToast({ title: '记录成功', icon: 'success' })
				this.newWeight = ''
				this.newFat = ''
				this.loadData()
			}).catch(() => {
				uni.showToast({ title: '记录失败', icon: 'none' })
			})
		}
	}
}
</script>

<style lang="scss">
.weight-page {
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

.current-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.current-label {
	font-size: 26rpx;
	color: var(--text-3);
}

.current-value {
	font-size: 56rpx;
	font-weight: bold;
	color: var(--text-1);
}

.current-unit {
	font-size: 28rpx;
	color: var(--text-3);
}

.current-right { text-align: center; }

.bmi-value {
	font-size: 40rpx;
	font-weight: bold;
	color: #667eea;
}

.bmi-label {
	font-size: 22rpx;
	padding: 4rpx 16rpx;
	border-radius: 20rpx;
	margin-top: 6rpx;
	display: inline-block;
}

.bmi-low { background: #e3f2fd; color: #1976d2; }
.bmi-normal { background: #e8f5e9; color: #388e3c; }
.bmi-high { background: #fff3e0; color: #f57c00; }
.bmi-danger { background: #fce4ec; color: #d32f2f; }

.target-row {
	margin-top: 20rpx;
}

.target-text {
	font-size: 24rpx;
	color: var(--text-2);
}

.progress-bg {
	height: 12rpx;
	background: var(--input-bg);
	border-radius: 6rpx;
	margin: 10rpx 0;
	overflow: hidden;
}

.progress-fill {
	height: 100%;
	background: linear-gradient(90deg, #667eea, #764ba2);
	border-radius: 6rpx;
	transition: width 0.5s ease;
}

.target-diff {
	font-size: 22rpx;
	color: var(--text-3);
}

.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
}

.chart-wrap { margin-top: 16rpx; }

.empty-chart, .empty-list {
	padding: 60rpx 0;
	text-align: center;
}

.empty-text {
	font-size: 26rpx;
	color: #bbb;
}

.add-row {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-top: 16rpx;
}

.add-input {
	flex: 1;
	height: 72rpx;
	background: var(--input-bg);
	border-radius: 14rpx;
	padding: 0 20rpx;
	font-size: 26rpx;
}

.ph { color: #bbb; font-size: 26rpx; }

.add-btn {
	height: 72rpx;
	padding: 0 32rpx;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border-radius: 36rpx;
	color: #fff;
	font-size: 28rpx;
	line-height: 72rpx;
}

.history-item {
	display: flex;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1px solid #f5f5f5;
	animation: fadeIn 0.3s ease both;
}

@keyframes fadeIn {
	from { opacity: 0; transform: translateY(10rpx); }
	to { opacity: 1; transform: translateY(0); }
}

.history-item:last-child { border-bottom: none; }

.history-date {
	flex: 1;
	font-size: 26rpx;
	color: #666;
}

.history-weight {
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
	margin-right: 20rpx;
}

.history-fat {
	font-size: 24rpx;
	color: #999;
}

.card-header {
	margin-bottom: 16rpx;
}
</style>
