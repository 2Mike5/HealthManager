<template>
	<view class="dashboard">
		<!-- 加载遮罩 -->
		<view v-if="loading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">加载中...</text>
		</view>

		<!-- 数据来源标识 -->
		<view v-if="dataSource === 'mock'" class="offline-badge">
			离线模式（后端未连接）
		</view>

		<!-- ===== 1. 用户问候区 ===== -->
		<view class="greeting-card">
			<view class="greeting-content">
				<text class="greeting-date">{{ todayDate }}</text>
				<text class="greeting-title">{{ greeting }} 👋</text>
				<text class="greeting-sub">{{ encouragement }}</text>
			</view>
			<view class="greeting-avatar">
				<uni-icons type="person-filled" size="32" color="#fff"></uni-icons>
			</view>
		</view>

		<!-- ===== 2. 日期切换栏 ===== -->
		<view class="view-toggle">
			<view
				v-for="tab in viewTabs"
				:key="tab.key"
				class="toggle-item"
				:class="{ active: currentView === tab.key }"
				@click="switchView(tab.key)"
			>
				<text>{{ tab.label }}</text>
			</view>
			<view class="toggle-indicator" :style="indicatorStyle"></view>
		</view>

		<!-- 范围导航（周/月切换） -->
		<view class="range-nav" v-if="currentView !== 'day'">
			<text class="nav-btn" @click="prevRange">〈</text>
			<text class="range-label">{{ rangeLabel }}</text>
			<text class="nav-btn" @click="nextRange">〉</text>
		</view>

		<!-- ===== 3. 图表卡片列表 ===== -->
		<scroll-view scroll-y="true" class="chart-list" show-scrollbar="false">
			<!-- ─── 步数环形进度 ─── -->
			<view class="card glass-card">
				<view class="card-header">
					<view class="card-title-row">
						<text class="card-title">🚶 步数</text>
						<view v-if="currentView === 'day'" class="date-nav">
							<text class="nav-btn" @click="prevStepsDay">〈</text>
							<text class="date-label">{{ stepsDateLabel }}</text>
							<text class="nav-btn" @click="nextStepsDay">〉</text>
						</view>
						<text v-else class="avg-label">{{ currentView === 'week' ? '周平均' : '月平均' }}</text>
					</view>
				</view>
				<view class="ring-wrapper">
					<qiun-data-charts
						type="ring"
						:chartData="stepsRingData"
						:opts="stepsRingOpts"
						height="280rpx"
						:canvas2d="true"
					/>
					<view class="ring-center">
						<text class="ring-value">{{ stepsDisplayValue }}</text>
						<text class="ring-unit">步</text>
					</view>
				</view>
				<view class="card-footer">
					<text>目标 10000 步</text>
					<text class="footer-highlight">已完成 {{ stepsDisplayPercent }}%</text>
				</view>
			</view>

			<!-- ─── 心率趋势折线图 ─── -->
			<view class="card glass-card">
				<view class="card-header">
					<text class="card-title">❤️ 心率趋势</text>
					<text class="heartbeat-icon">💓</text>
				</view>
				<qiun-data-charts
					type="line"
					:chartData="hrChartData"
					:opts="hrChartOpts"
					height="400rpx"
				/>
				<view class="card-footer">
					<view class="legend-row">
						<view class="legend-dot" style="background:#4CAF50"></view>
						<text>最小</text>
						<view class="legend-dot" style="background:#FF9800"></view>
						<text>平均</text>
						<view class="legend-dot" style="background:#F44336"></view>
						<text>最大</text>
					</view>
				</view>
			</view>

			<!-- ─── 睡眠热力日历 ─── -->
			<view class="card glass-card">
				<view class="card-header">
					<text class="card-title">💤 睡眠热力图</text>
					<view class="month-nav">
						<text class="nav-btn" @click="prevMonth">〈</text>
						<text class="month-label">{{ calendarYear }}年{{ calendarMonth }}月</text>
						<text class="nav-btn" @click="nextMonth">〉</text>
					</view>
				</view>
				<view class="calendar-grid">
					<view class="cal-weekday" v-for="w in weekdays" :key="w">{{ w }}</view>
					<view
						v-for="(cell, i) in calendarGrid"
						:key="i"
						class="cal-cell"
						:class="{ 'cal-empty': !cell.isCurrentMonth }"
						@click="showSleepDetail(cell)"
					>
						<template v-if="cell.isCurrentMonth">
							<view
								class="cal-bg"
								:style="{ background: sleepColor(cell.sleep) }"
							></view>
							<text class="cal-day">{{ cell.day }}</text>
							<text class="cal-sleep">{{ cell.sleep ? cell.sleep + 'h' : '--' }}</text>
						</template>
					</view>
				</view>
			</view>

			<!-- ─── 健康评分雷达图 ─── -->
			<view class="card dark-card">
				<view class="card-header">
					<text class="card-title title-light">⭐ 健康评分</text>
					<text class="total-score">{{ totalHealthScore }}</text>
				</view>
				<qiun-data-charts
					type="radar"
					:chartData="radarData"
					:opts="radarOpts"
					height="420rpx"
				/>
				<view class="radar-footer">
					<view class="score-ring-wrap">
						<view class="score-ring">
							<svg viewBox="0 0 100 100" class="score-svg">
								<circle cx="50" cy="50" r="44" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6" />
								<circle
									cx="50" cy="50" r="44"
									fill="none" stroke="#7c4dff"
									stroke-width="6"
									stroke-linecap="round"
									stroke-dasharray="276"
									:stroke-dashoffset="radarRingOffset"
									transform="rotate(-90, 50, 50)"
									class="score-ring-anim"
								/>
							</svg>
							<text class="score-ring-text">{{ totalHealthScore }}</text>
						</view>
					</view>
					<view class="score-dims">
						<view class="dim-item" v-for="dim in radarDims" :key="dim.label">
							<text class="dim-label">{{ dim.label }}</text>
							<view class="dim-bar-bg">
								<view class="dim-bar" :style="{ width: dim.value + '%', background: dim.color }"></view>
							</view>
							<text class="dim-val">{{ dim.value }}</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 底部安全距离 -->
			<view style="height:40px"></view>
		</scroll-view>
	</view>
</template>

<script>
import { loadHealthData } from '@/utils/api'
import {
	getTodayData, filterByView,
	getMonthCalendar, getEncouragement
} from '@/utils/mock'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

export default {
	data() {
		return {
			allData: [],
			loading: true,
			dataSource: 'mock',
			stepsDate: new Date(),
			currentView: 'week',
			refDate: new Date(),
			calendarYear: new Date().getFullYear(),
			calendarMonth: new Date().getMonth() + 1,
			viewTabs: [
				{ key: 'day', label: '日' },
				{ key: 'week', label: '周' },
				{ key: 'month', label: '月' }
			],
			weekdays: WEEKDAYS
		}
	},

	computed: {
		// ── 问候区 ──
		todayDate() {
			const d = new Date()
			const y = d.getFullYear()
			const m = d.getMonth() + 1
			const day = d.getDate()
			const w = WEEKDAYS[d.getDay()]
			return `${y}年${m}月${day}日 星期${w}`
		},
		greeting() {
			const h = new Date().getHours()
			if (h < 6) return '夜深了'
			if (h < 9) return '早上好'
			if (h < 12) return '上午好'
			if (h < 14) return '中午好'
			if (h < 18) return '下午好'
			return '晚上好'
		},
		encouragement() {
			return getEncouragement()
		},

		// ── 数据 ──
		todayData() {
			return getTodayData(this.allData) || {}
		},
		filteredData() {
			return filterByView(this.allData, this.currentView, this.refDate)
		},

		// ── 视图切换指示器动画 ──
		indicatorStyle() {
			const idx = this.viewTabs.findIndex(t => t.key === this.currentView)
			const left = idx * 33.33
			return { left: left + '%' }
		},
		rangeLabel() {
			if (this.currentView === 'week') {
				const r = this.getWeekRange(this.refDate)
				const sm = r.start.getMonth() + 1
				const sd = r.start.getDate()
				const em = r.end.getMonth() + 1
				const ed = r.end.getDate()
				return sm + '月' + sd + '日 - ' + em + '月' + ed + '日'
			}
			if (this.currentView === 'month') {
				return this.refDate.getFullYear() + '年' + (this.refDate.getMonth() + 1) + '月'
			}
			return ''
		},

		// ── 步数环形图 ──
		todayStepsPercent() {
			const s = this.todayData.steps || 0
			return Math.min(100, Math.round((s / 10000) * 100))
		},
		stepsDayData() {
			const d = this.stepsDate
			const key = d.getFullYear() + '-' +
				String(d.getMonth() + 1).padStart(2, '0') + '-' +
				String(d.getDate()).padStart(2, '0')
			return this.allData.find(r => r.date === key) || {}
		},
		stepsDateLabel() {
			const d = this.stepsDate
			return d.getMonth() + 1 + '月' + d.getDate() + '日'
		},
		stepsDayPercent() {
			const s = this.stepsDayData.steps || 0
			return Math.min(100, Math.round((s / 10000) * 100))
		},
		stepsDisplayValue() {
			if (this.currentView === "day") return this.stepsDayData.steps || 0
			const src = this.filteredData
			const len = src.length || 1
			return Math.round(src.reduce((a, d) => a + (d.steps || 0), 0) / len)
		},
		stepsDisplayPercent() {
			return Math.min(100, Math.round((this.stepsDisplayValue / 10000) * 100))
		},
		stepsRingData() {
			const pct = this.stepsDisplayPercent
			return {
				series: [
					{ name: '已完成', data: pct },
					{ name: '剩余', data: Math.max(0, 100 - pct) }
				]
			}
		},
		stepsRingOpts() {
			return {
				type: 'ring',
				background: 'transparent',
				padding: [0, 0, 0, 0],
				rotate: false,
				legend: { show: false },
				title: { show: false },
				subtitle: {show:false},
				dataLabel: false,
				extra: {
					ring: {
						ringLabel: false,
						ringWidth: 28,
						activeOpacity: 0.5,
						activeRadius: 12,
						offsetRadius: 0,
						customWidth: 0,
						linearType: 'custom',
						color: [
							{ offset: 0, color: '#536DFE' },
							{ offset: 1, color: '#7C4DFF' }
						]
					}
				}
			}
		},

		// ── 心率折线图 ──
		hrChartData() {
			const d = this.filteredData
			const reversed = [...d].reverse()
			return {
				categories: reversed.map(r => {
					if (this.currentView === 'day') return r.dayLabel
					const md = r.date.slice(5)
					return this.currentView === 'week' ? r.dayLabel : md
				}),
				series: [
					{ name: '最小', data: reversed.map(r => r.hrMin) },
					{ name: '平均', data: reversed.map(r => r.hrAvg) },
					{ name: '最大', data: reversed.map(r => r.hrMax) }
				]
			}
		},
		hrChartOpts() {
			return {
				padding: [20, 15, 10, 35],
				legend: { show: false },
				xAxis: {
					labelCount: this.currentView === 'week' ? 7 : 5,
					itemCount: this.currentView === 'month' ? 30 : 7,
					scrollShow: this.currentView === 'month',
					scrollAlign: 'left'
				},
				yAxis: { data: [{ min: 40, max: 150 }] },
				extra: {
					line: {
						type: 'curve',
						width: 3,
						activeWidth: 5,
						linearType: 'custom',
						areaStyle: {
							linearType: 'custom',
							opacity: 0.15
						}
					},
					tooltip: { showBox: true, showLabel: true }
				},
				color: ['#4CAF50', '#FF9800', '#F44336']
			}
		},

		// ── 睡眠日历 ──
		calendarGrid() {
			return getMonthCalendar(this.calendarYear, this.calendarMonth, this.allData)
		},

		// ── 雷达图 ──
		radarDims() {
			const src = this.currentView === "day" ? [this.stepsDayData] : this.filteredData
			const len = src.length || 1
			const sum = (f) => src.reduce((a, d) => a + (d[f] || 0), 0) / len
			const avgSteps = sum("steps")
			const avgHr = sum("hrAvg")
			const avgSleep = sum("sleep")
			const avgWater = sum("water")
			const avgExercise = sum("exercise")
			const avgMood = sum("mood")
			const stepsScore = Math.min(100, Math.round((avgSteps / 10000) * 100))
			const hrScore = avgHr ? Math.max(0, 100 - Math.abs(avgHr - 70) * 2) : 70
			const sleepScore = avgSleep ? Math.min(100, Math.round((avgSleep / 8) * 100)) : 70
			const waterScore = Math.min(100, Math.round((avgWater / 8) * 100))
			const exerciseScore = Math.min(100, Math.round((avgExercise / 60) * 100))
			const moodScore = avgMood || 80

			return [
				{ label: '步数', value: stepsScore, color: '#536DFE' },
				{ label: '心率', value: hrScore, color: '#FF6B6B' },
				{ label: '睡眠', value: sleepScore, color: '#4ECDC4' },
				{ label: '饮水', value: waterScore, color: '#45B7D1' },
				{ label: '运动', value: exerciseScore, color: '#FFA94D' },
				{ label: '情绪', value: moodScore, color: '#F783AC' }
			]
		},
		radarData() {
			return {
				categories: this.radarDims.map(d => d.label),
				series: [{ name: this.currentView === 'day' ? '今日评分' : this.currentView === 'week' ? '本周平均' : '本月平均', data: this.radarDims.map(d => d.value) }]
			}
		},
		radarOpts() {
			return {
				padding: [20, 20, 20, 20],
				legend: { show: false },
				dataLabel: false,
				yAxis: { disabled: true, max: 100 },
				extra: {
					radar: {
						type: 'circle',
						gridColor: 'rgba(255,255,255,0.12)',
						gridBorderWidth: 1,
						max: 100,
						labelColor: '#ccc',
						opacity: 0.3,
						lineColor: ['#7C4DFF']
					}
				},
				color: ['#7C4DFF']
			}
		},
		totalHealthScore() {
			const vals = this.radarDims.map(d => d.value)
			return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
		},
		radarRingOffset() {
			const circumference = 2 * Math.PI * 44
			return circumference * (1 - this.totalHealthScore / 100)
		}
	},

	onLoad() {
		this.loadData()
	},
	onShow() {
		this.loadData()
	},

	methods: {
		async loadData() {
			this.loading = true
			const result = await loadHealthData()
			this.allData = result.data
			this.dataSource = result.source
			this.loading = false
		},
		switchView(view) {
			this.currentView = view
		},
		prevStepsDay() {
			const d = new Date(this.stepsDate)
			d.setDate(d.getDate() - 1)
			this.stepsDate = d
		},
		nextStepsDay() {
			const d = new Date(this.stepsDate)
			d.setDate(d.getDate() + 1)
			if (d <= new Date()) this.stepsDate = d
		},
		getWeekRange(date) {
			const d = new Date(date)
			const day = d.getDay()
			const diff = d.getDate() - day + (day === 0 ? -6 : 1)
			const monday = new Date(d.setDate(diff))
			const sunday = new Date(monday)
			sunday.setDate(monday.getDate() + 6)
			return { start: monday, end: sunday }
		},
		prevRange() {
			const d = new Date(this.refDate)
			if (this.currentView === "week") d.setDate(d.getDate() - 7)
			else d.setMonth(d.getMonth() - 1)
			this.refDate = d
		},
		nextRange() {
			const d = new Date(this.refDate)
			if (this.currentView === "week") d.setDate(d.getDate() + 7)
			else d.setMonth(d.getMonth() + 1)
			if (d <= new Date()) this.refDate = d
		},

		prevMonth() {
			if (this.calendarMonth === 1) {
				this.calendarMonth = 12
				this.calendarYear--
			} else {
				this.calendarMonth--
			}
		},
		nextMonth() {
			if (this.calendarMonth === 12) {
				this.calendarMonth = 1
				this.calendarYear++
			} else {
				this.calendarMonth++
			}
		},

		sleepColor(sleep) {
			if (sleep === null || sleep === undefined) return 'transparent'
			if (sleep >= 8) return 'rgba(76, 175, 80, 0.35)'
			if (sleep >= 7) return 'rgba(76, 175, 80, 0.2)'
			if (sleep >= 6) return 'rgba(255, 152, 0, 0.25)'
			if (sleep >= 5) return 'rgba(255, 87, 34, 0.25)'
			return 'rgba(244, 67, 54, 0.35)'
		},

		showSleepDetail(cell) {
			if (!cell.isCurrentMonth || !cell.sleep) return
			const stage = cell.sleep >= 8 ? '深度睡眠充足' :
				cell.sleep >= 7 ? '睡眠良好' :
				cell.sleep >= 6 ? '轻度不足' :
				cell.sleep >= 5 ? '睡眠不足' : '严重不足'

			uni.showModal({
				title: `${cell.date} 睡眠详情`,
				content: `总睡眠时长：${cell.sleep} 小时\n状态：${stage}\n建议：${cell.sleep >= 7 ? '继续保持良好作息！' : cell.sleep >= 6 ? '试着提前半小时入睡' : '请调整作息，保证充足睡眠'}`,
				showCancel: false
			})
		}
	}
}
</script>

<style lang="scss">
// ───────────── 全局变量 ─────────────
$glass-bg: rgba(255, 255, 255, 0.75);
$glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
$radius: 20px;
$safe-bottom: 40px;

// ── 加载遮罩 ──
.loading-overlay {
	position: fixed;
	inset: 0;
	background: rgba(255, 255, 255, 0.85);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	z-index: 999;
}

.loading-spinner {
	width: 60rpx;
	height: 60rpx;
	border: 6rpx solid #e0e0e0;
	border-top-color: #667eea;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

.loading-text {
	margin-top: 20rpx;
	font-size: 28rpx;
	color: #999;
}

// ── 离线模式标识 ──
.offline-badge {
	position: fixed;
	top: 16rpx;
	right: 16rpx;
	background: rgba(255, 152, 0, 0.9);
	color: #fff;
	font-size: 20rpx;
	padding: 6rpx 16rpx;
	border-radius: 20rpx;
	z-index: 100;
}

.dashboard {
	padding: 0;
	background: #f0f2f5;
	min-height: 100vh;
}

// ── 1. 问候区 ──
.greeting-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 32rpx 32rpx 40rpx;
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: flex-start;
}

.greeting-date {
	color: rgba(255, 255, 255, 0.7);
	font-size: 24rpx;
	display: block;
	margin-bottom: 8rpx;
}

.greeting-title {
	color: #fff;
	font-size: 40rpx;
	font-weight: bold;
	display: block;
}

.greeting-sub {
	color: rgba(255, 255, 255, 0.85);
	font-size: 26rpx;
	margin-top: 8rpx;
	display: block;
}

.greeting-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
}

// ── 2. 视图切换 ──

// ── 范围导航（周/月切换） ──
.range-nav {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
	gap: 24rpx;
	padding: 12rpx 0;
	margin: 0 24rpx 8rpx;
	background: #fff;
	border-radius: 14rpx;
	box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.range-label {
	font-size: 26rpx;
	color: #555;
	font-weight: 500;
}

.view-toggle {
	position: relative;
	display: flex;
	flex-direction: row;
	background: #fff;
	margin: -24rpx 32rpx 20rpx;
	border-radius: 16rpx;
	box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
	padding: 6rpx;
	z-index: 2;
}

.toggle-item {
	flex: 1;
	text-align: center;
	padding: 14rpx 0;
	font-size: 28rpx;
	color: #999;
	z-index: 2;
	transition: color 0.3s;
	border-radius: 12rpx;

	&.active {
		color: #667eea;
		font-weight: 600;
	}
}

.toggle-indicator {
	position: absolute;
	top: 6rpx;
	bottom: 6rpx;
	width: 33.33%;
	background: rgba(102, 126, 234, 0.12);
	border-radius: 12rpx;
	transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	z-index: 1;
}

// ── 3. 卡片列表 ──
.chart-list {
	padding: 0 24rpx;
	height: calc(100vh - 320rpx); // 减去问候区 + 切换栏高度
}

.card {
	border-radius: $radius;
	padding: 32rpx;
	margin-bottom: 24rpx;
}

// ── 毛玻璃效果 ──
.glass-card {
	background: $glass-bg;
	backdrop-filter: blur(20px);
	-webkit-backdrop-filter: blur(20px);
	box-shadow: $glass-shadow;
	border: 1px solid rgba(255, 255, 255, 0.6);
}

// ── 卡片头部 ──
.card-header {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}


.card-title-row {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 16rpx;
}

.date-nav {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 8rpx;
}

.date-label {
	font-size: 24rpx;
	color: #777;
	min-width: 80rpx;
	text-align: center;
}

.avg-label {
	font-size: 24rpx;
	color: #999;
	background: #f0f0f0;
	padding: 4rpx 16rpx;
	border-radius: 12rpx;
}


.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

.card-badge {
	font-size: 24rpx;
	color: #ff6b35;
	font-weight: 600;
}

// ── 卡片底部 ──
.card-footer {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	margin-top: 16rpx;
	font-size: 24rpx;
	color: #999;
}

.footer-highlight {
	color: #667eea;
	font-weight: 600;
}

// ════════════════════════════════
// 步数环形图
// ════════════════════════════════
.ring-wrapper {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: 320rpx;
}

.ring-center {
	position: absolute;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	text-align: center;
	pointer-events: none;
}

.ring-value {
	font-size: 72rpx;
	font-weight: bold;
	color: #5C6BC0;
	display: block;
	line-height: 1.1;
}

.ring-unit {
	font-size: 24rpx;
	color: #999;
}

// ════════════════════════════════
// 心率趋势
// ════════════════════════════════
.heartbeat-icon {
	font-size: 36rpx;
	animation: heartbeat 1.2s ease-in-out infinite;
}

@keyframes heartbeat {
	0%, 100% { transform: scale(1); }
	14% { transform: scale(1.25); }
	28% { transform: scale(1); }
	42% { transform: scale(1.25); }
	56% { transform: scale(1); }
}

.legend-row {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 16rpx;
	font-size: 22rpx;
	color: #888;
}

.legend-dot {
	width: 14rpx;
	height: 14rpx;
	border-radius: 50%;
}

// ════════════════════════════════
// 睡眠热力日历
// ════════════════════════════════
.month-nav {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 16rpx;
}

.nav-btn {
	font-size: 30rpx;
	color: #667eea;
	padding: 4rpx 12rpx;
	background: rgba(102, 126, 234, 0.1);
	border-radius: 8rpx;
}

.month-label {
	font-size: 26rpx;
	font-weight: 600;
	color: #555;
	min-width: 140rpx;
	text-align: center;
}

.calendar-grid {
	display: grid;
	grid-template-columns: repeat(7, 1fr);
	gap: 6rpx;
}

.cal-weekday {
	text-align: center;
	font-size: 22rpx;
	color: #999;
	padding: 10rpx 0;
	font-weight: 500;
}

.cal-cell {
	position: relative;
	aspect-ratio: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	border-radius: 12rpx;
	padding: 4rpx;
	min-height: 80rpx;
}

.cal-empty {
	visibility: hidden;
}

.cal-bg {
	position: absolute;
	inset: 0;
	border-radius: 12rpx;
}

.cal-day {
	font-size: 24rpx;
	color: #333;
	font-weight: 500;
	z-index: 1;
}

.cal-sleep {
	font-size: 18rpx;
	color: #888;
	margin-top: 2rpx;
	z-index: 1;
}

// ════════════════════════════════
// 健康评分 - 深色科技风
// ════════════════════════════════
.dark-card {
	background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
	box-shadow: 0 8px 32px rgba(15, 52, 96, 0.3);
	border: 1px solid rgba(255, 255, 255, 0.08);
}

.title-light {
	color: rgba(255, 255, 255, 0.9);
}

.total-score {
	font-size: 48rpx;
	font-weight: bold;
	color: #7c4dff;
	text-shadow: 0 0 20px rgba(124, 77, 255, 0.5);
}

.radar-footer {
	display: flex;
	flex-direction: row;
	gap: 24rpx;
	margin-top: 16rpx;
}

.score-ring-wrap {
	flex-shrink: 0;
	width: 160rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.score-ring {
	position: relative;
	width: 140rpx;
	height: 140rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.score-svg {
	width: 100%;
	height: 100%;
}

.score-ring-anim {
	transition: stroke-dashoffset 1s ease;
}

.score-ring-text {
	position: absolute;
	font-size: 36rpx;
	font-weight: bold;
	color: #7c4dff;
}

.score-dims {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 10rpx;
}

.dim-item {
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 10rpx;
}

.dim-label {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.7);
	width: 60rpx;
	text-align: right;
}

.dim-bar-bg {
	flex: 1;
	height: 12rpx;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 6rpx;
	overflow: hidden;
}

.dim-bar {
	height: 100%;
	border-radius: 6rpx;
	transition: width 0.8s ease;
}

.dim-val {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.8);
	width: 50rpx;
	text-align: right;
	font-weight: 600;
}
</style>
