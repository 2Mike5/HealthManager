<template>
	<view class="diet-page">
		<view v-if="loading" class="loading-overlay">
			<view class="loading-spinner"></view>
		</view>

		<!-- 日期选择 -->
		<view class="date-bar">
			<text class="date-nav" @tap="prevDay">&#8249;</text>
			<text class="date-text">{{ displayDate }}</text>
			<text class="date-nav" @tap="nextDay">&#8250;</text>
		</view>

		<!-- 每日摘要 -->
		<view class="summary-card glass-card">
			<view class="summary-row">
				<view class="summary-item">
					<text class="summary-num">{{ summary.total_calories || 0 }}</text>
					<text class="summary-label">总热量 (kcal)</text>
				</view>
				<view class="summary-divider"></view>
				<view class="summary-item">
					<text class="summary-num">{{ summary.total_protein || 0 }}g</text>
					<text class="summary-label">蛋白质</text>
				</view>
				<view class="summary-divider"></view>
				<view class="summary-item">
					<text class="summary-num">{{ summary.total_fat || 0 }}g</text>
					<text class="summary-label">脂肪</text>
				</view>
				<view class="summary-divider"></view>
				<view class="summary-item">
					<text class="summary-num">{{ summary.total_carbs || 0 }}g</text>
					<text class="summary-label">碳水</text>
				</view>
			</view>
			<!-- 营养素环图 -->
			<view v-if="hasNutrition" class="macro-chart">
				<qiun-data-charts type="ring" :chartData="macroData" :opts="macroOpts" height="280rpx" />
			</view>
		</view>

		<!-- 餐次列表 -->
		<view class="meals-section">
			<view v-for="meal in mealOrder" :key="meal.key" class="meal-card glass-card">
				<view class="meal-header">
					<text class="meal-tag" :class="'meal-' + meal.key">{{ meal.label }}</text>
					<text class="meal-cal">{{ byMeal[meal.key] ? byMeal[meal.key].calories : 0 }} kcal</text>
				</view>
				<view v-if="byMeal[meal.key] && byMeal[meal.key].items.length">
					<view v-for="item in byMeal[meal.key].items" :key="item.id" class="food-item">
						<text class="food-name">{{ item.food_name }}</text>
						<text class="food-amount">{{ item.amount }}{{ item.unit }}</text>
						<text class="food-cal">{{ item.calories }}kcal</text>
						<text class="food-del" @tap="deleteItem(item.id)">&#10005;</text>
					</view>
				</view>
				<view v-else class="meal-empty">
					<text class="empty-text">暂无记录</text>
				</view>
			</view>
		</view>

		<!-- 添加饮食 -->
		<view class="add-section glass-card">
			<text class="card-title">添加饮食</text>
			<view class="add-form">
				<view class="form-row">
					<picker class="meal-picker" :value="mealIndex" :range="mealOptions" @change="onMealChange">
						<text class="picker-text">{{ mealOptions[mealIndex] }}</text>
					</picker>
					<input class="add-input food-input" v-model="foodName" placeholder="食物名称" placeholder-class="ph" />
				</view>
				<view class="form-row">
					<input class="add-input" v-model="foodAmount" type="digit" placeholder="份量(g)" placeholder-class="ph" />
					<input class="add-input" v-model="foodCal" type="digit" placeholder="热量(kcal)" placeholder-class="ph" />
				</view>
				<view class="form-row">
					<input class="add-input" v-model="foodProtein" type="digit" placeholder="蛋白(g)" placeholder-class="ph" />
					<input class="add-input" v-model="foodFat" type="digit" placeholder="脂肪(g)" placeholder-class="ph" />
					<input class="add-input" v-model="foodCarbs" type="digit" placeholder="碳水(g)" placeholder-class="ph" />
				</view>
				<button class="add-food-btn" @tap="addFood">添加</button>
			</view>
		</view>
	</view>
</template>

<script>
import { getDietSummary, createDietRecord, deleteDietRecord, searchFoods } from '@/utils/api'

const MEAL_CONFIG = {
	breakfast: { label: '早餐', key: 'breakfast' },
	lunch: { label: '午餐', key: 'lunch' },
	dinner: { label: '晚餐', key: 'dinner' },
	snack: { label: '加餐', key: 'snack' }
}

export default {
	data() {
		const today = new Date()
		return {
			loading: true,
			currentDate: today.getFullYear() + '-' + String(today.getMonth()+1).padStart(2,'0') + '-' + String(today.getDate()).padStart(2,'0'),
			summary: {},
			byMeal: {},
			mealOrder: [
				{ key: 'breakfast', label: '早餐' },
				{ key: 'lunch', label: '午餐' },
				{ key: 'dinner', label: '晚餐' },
				{ key: 'snack', label: '加餐' }
			],
			mealOptions: ['早餐', '午餐', '晚餐', '加餐'],
			mealIndex: 0,
			foodName: '',
			foodAmount: '',
			foodCal: '',
			foodProtein: '',
			foodFat: '',
			foodCarbs: ''
		}
	},
	computed: {
		displayDate() {
			const parts = this.currentDate.split('-')
			return parts[0] + '年' + parseInt(parts[1]) + '月' + parseInt(parts[2]) + '日'
		},
		hasNutrition() {
			return (this.summary.total_protein || 0) > 0 || (this.summary.total_fat || 0) > 0 || (this.summary.total_carbs || 0) > 0
		},
		macroData() {
			if (!this.hasNutrition) return null
			return {
				series: [
					{ name: '蛋白质', data: this.summary.total_protein || 0 },
					{ name: '脂肪', data: this.summary.total_fat || 0 },
					{ name: '碳水', data: this.summary.total_carbs || 0 }
				]
			}
		},
		macroOpts() {
			return {
				legend: { position: 'bottom', show: true },
				dataLabel: false,
				extra: {
					ring: { ringWidth: 24, ringLabel: false }
				},
				color: ['#4CAF50', '#FF6B6B', '#45B7D1'],
				background: 'transparent'
			}
		},
		mealKeys() { return ['breakfast', 'lunch', 'dinner', 'snack'] }
	},
	onShow() {
		this.loadData()
	},
	methods: {
		loadData() {
			this.loading = true
			getDietSummary(this.currentDate).then(res => {
				this.summary = res
				this.byMeal = res.by_meal || {}
			}).catch(() => {}).finally(() => {
				this.loading = false
			})
		},
		prevDay() {
			const d = new Date(this.currentDate)
			d.setDate(d.getDate() - 1)
			this.currentDate = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
			this.loadData()
		},
		nextDay() {
			const d = new Date(this.currentDate)
			d.setDate(d.getDate() + 1)
			this.currentDate = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
			this.loadData()
		},
		onMealChange(e) {
			this.mealIndex = e.detail.value
		},
		addFood() {
			if (!this.foodName.trim()) {
				uni.showToast({ title: '请输入食物名称', icon: 'none' })
				return
			}
			const mealMap = { 0: 'breakfast', 1: 'lunch', 2: 'dinner', 3: 'snack' }
			const data = {
				date: this.currentDate,
				meal_type: mealMap[this.mealIndex],
				food_name: this.foodName.trim(),
				amount: parseFloat(this.foodAmount) || 100,
				unit: 'g',
				calories: parseFloat(this.foodCal) || 0,
				protein: parseFloat(this.foodProtein) || 0,
				fat: parseFloat(this.foodFat) || 0,
				carbs: parseFloat(this.foodCarbs) || 0
			}
			createDietRecord(data).then(() => {
				uni.showToast({ title: '添加成功', icon: 'success' })
				this.foodName = ''
				this.foodAmount = ''
				this.foodCal = ''
				this.foodProtein = ''
				this.foodFat = ''
				this.foodCarbs = ''
				this.loadData()
			}).catch(() => {
				uni.showToast({ title: '添加失败', icon: 'none' })
			})
		},
		deleteItem(id) {
			uni.showModal({
				title: '提示',
				content: '删除这条记录？',
				success: (res) => {
					if (res.confirm) {
						deleteDietRecord(id).then(() => {
							this.loadData()
						})
					}
				}
			})
		}
	}
}
</script>

<style lang="scss">
.diet-page {
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

.date-bar {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 40rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
}

.date-nav {
	font-size: 48rpx;
	color: #667eea;
	padding: 8rpx 16rpx;
}

.date-text {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

.summary-row {
	display: flex;
	align-items: center;
}

.summary-item {
	flex: 1;
	text-align: center;
}

.summary-num {
	font-size: 32rpx;
	font-weight: bold;
	color: #667eea;
}

.summary-label {
	font-size: 22rpx;
	color: #999;
	margin-top: 6rpx;
	display: block;
}

.summary-divider {
	width: 1px;
	height: 50rpx;
	background: #eee;
}

.macro-chart {
	margin-top: 16rpx;
}

.meal-card { }

.meal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.meal-tag {
	font-size: 26rpx;
	font-weight: 600;
	padding: 6rpx 20rpx;
	border-radius: 20rpx;
}

.meal-breakfast { background: #fff3e0; color: #e65100; }
.meal-lunch { background: #e8f5e9; color: #2e7d32; }
.meal-dinner { background: #e3f2fd; color: #1565c0; }
.meal-snack { background: #fce4ec; color: #c62828; }

.meal-cal {
	font-size: 26rpx;
	color: #666;
}

.food-item {
	display: flex;
	align-items: center;
	padding: 14rpx 0;
	border-bottom: 1px solid #f5f5f5;
	font-size: 26rpx;
}

.food-item:last-child { border-bottom: none; }

.food-name { flex: 1; color: #333; }
.food-amount { color: #999; margin-right: 16rpx; }
.food-cal { color: #666; width: 100rpx; text-align: right; }
.food-del { color: #e74c3c; margin-left: 16rpx; padding: 8rpx; }

.meal-empty {
	padding: 30rpx 0;
	text-align: center;
}

.empty-text { font-size: 24rpx; color: #ccc; }

.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.add-form {}

.form-row {
	display: flex;
	gap: 12rpx;
	margin-bottom: 16rpx;
}

.meal-picker {
	height: 72rpx;
	background: #f5f7fa;
	border-radius: 14rpx;
	padding: 0 20rpx;
	display: flex;
	align-items: center;
	min-width: 140rpx;
}

.picker-text {
	font-size: 26rpx;
	color: #333;
}

.add-input {
	height: 72rpx;
	background: #f5f7fa;
	border-radius: 14rpx;
	padding: 0 16rpx;
	font-size: 26rpx;
	flex: 1;
}

.ph { color: #bbb; font-size: 26rpx; }

.food-input { flex: 2; }

.add-food-btn {
	width: 100%;
	height: 72rpx;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border-radius: 36rpx;
	color: #fff;
	font-size: 28rpx;
	line-height: 72rpx;
	margin-top: 8rpx;
}
</style>
