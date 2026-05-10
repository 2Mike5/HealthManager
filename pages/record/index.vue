<template>
	<view class="record-page">
		<view v-if="submitting" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">保存中...</text>
		</view>

		<!-- 日期显示 -->
		<view class="date-section">
			<view class="date-nav" @tap="prevDay">&#8249;</view>
			<view class="date-info">
				<text class="date-text">{{ displayDate }}</text>
				<text class="date-label">{{ dayLabel }}</text>
			</view>
			<view class="date-nav" @tap="nextDay">&#8250;</view>
		</view>

		<!-- Section 1: 基础指标 -->
		<view class="section-card glass-card">
			<view class="section-header">
				<text class="section-title">基础指标</text>
			</view>

			<view class="field-row">
				<text class="field-label">步数</text>
				<input class="field-input" v-model="form.steps" type="number" placeholder="0" placeholder-class="ph" />
			</view>

			<view class="field-row">
				<text class="field-label">心率 (最低)</text>
				<input class="field-input" v-model="form.hrMin" type="number" placeholder="--" placeholder-class="ph" />
			</view>
			<view class="field-row">
				<text class="field-label">心率 (平均)</text>
				<input class="field-input" v-model="form.hrAvg" type="number" placeholder="--" placeholder-class="ph" />
			</view>
			<view class="field-row">
				<text class="field-label">心率 (最高)</text>
				<input class="field-input" v-model="form.hrMax" type="number" placeholder="--" placeholder-class="ph" />
			</view>

			<view class="field-row">
				<text class="field-label">睡眠 (小时)</text>
				<view class="slider-wrap">
					<slider :value="form.sleep" min="0" max="12" step="0.5" @change="onSleepChange" />
					<text class="slider-val">{{ form.sleep }}h</text>
				</view>
			</view>

			<view class="field-row">
				<text class="field-label">饮水 (杯)</text>
				<view class="stepper-wrap">
					<text class="stepper-btn" @tap="adjustWater(-1)">-</text>
					<text class="stepper-val">{{ form.water }}</text>
					<text class="stepper-btn" @tap="adjustWater(1)">+</text>
				</view>
			</view>

			<view class="field-row">
				<text class="field-label">情绪</text>
				<view class="mood-wrap">
					<text v-for="m in 5" :key="m" class="mood-star" :class="{ active: form.mood >= m }" @tap="form.mood = m">&#9733;</text>
				</view>
			</view>
		</view>

		<!-- Section 2: 运动记录 -->
		<view class="section-card glass-card">
			<view class="section-header">
				<text class="section-title">运动记录</text>
			</view>
			<view class="field-row">
				<text class="field-label">运动类型</text>
				<picker :value="exerciseIndex" :range="exerciseTypes" @change="onExerciseTypeChange">
					<text class="picker-text">{{ exerciseTypes[exerciseIndex] }}</text>
				</picker>
			</view>
			<view class="field-row">
				<text class="field-label">运动时长 (分钟)</text>
				<input class="field-input" v-model="form.exercise" type="number" placeholder="0" placeholder-class="ph" />
			</view>
			<view class="field-row">
				<text class="field-label">预估消耗</text>
				<view class="cal-display">
					<input class="field-input" v-model="form.caloriesBurned" type="digit" placeholder="自动计算" placeholder-class="ph" />
					<text class="cal-unit">千卡</text>
				</view>
			</view>
		</view>

		<!-- Section 3: 体重记录 -->
		<view class="section-card glass-card">
			<view class="section-header">
				<text class="section-title">体重记录</text>
			</view>
			<view class="field-row">
				<text class="field-label">体重 (kg)</text>
				<input class="field-input" v-model="form.weight" type="digit" placeholder="--" placeholder-class="ph" />
			</view>
			<view class="field-row">
				<text class="field-label">体脂率 (%)</text>
				<input class="field-input" v-model="form.bodyFat" type="digit" placeholder="可选" placeholder-class="ph" />
			</view>
			<view v-if="form.weight && userHeight" class="bmi-display">
				<text>BMI: <text class="bmi-value">{{ computedBMI }}</text></text>
			</view>
		</view>

		<!-- Section 4: 饮食记录 -->
		<view class="section-card glass-card">
			<view class="section-header">
				<text class="section-title">饮食记录</text>
				<text class="section-add" @tap="addFoodEntry">+ 添加</text>
			</view>

			<view v-for="(entry, i) in form.foodEntries" :key="i" class="food-entry">
				<view class="food-header">
					<text class="food-num">#{{ i+1 }}</text>
					<text class="food-del" @tap="removeFoodEntry(i)">删除</text>
				</view>
				<view class="field-row">
					<text class="field-label">餐次</text>
					<picker :value="entry.mealIndex" :range="mealOptions" @change="(e) => onFoodMealChange(i, e)">
						<text class="picker-text">{{ mealOptions[entry.mealIndex] }}</text>
					</picker>
				</view>
				<view class="field-row">
					<text class="field-label">食物</text>
					<input class="field-input" v-model="entry.foodName" placeholder="食物名称" placeholder-class="ph" />
				</view>
				<view class="field-row">
					<text class="field-label">份量(g)</text>
					<input class="field-input" v-model="entry.amount" type="digit" placeholder="100" placeholder-class="ph" />
				</view>
				<view class="field-row">
					<text class="field-label">热量(kcal)</text>
					<input class="field-input" v-model="entry.calories" type="digit" placeholder="0" placeholder-class="ph" />
				</view>
				<view class="macro-row">
					<input class="macro-input" v-model="entry.protein" type="digit" placeholder="蛋白(g)" placeholder-class="ph" />
					<input class="macro-input" v-model="entry.fat" type="digit" placeholder="脂肪(g)" placeholder-class="ph" />
					<input class="macro-input" v-model="entry.carbs" type="digit" placeholder="碳水(g)" placeholder-class="ph" />
				</view>
			</view>

			<view v-if="form.foodEntries.length > 0" class="food-total">
				<text class="total-text">合计: {{ foodTotalCal }} kcal</text>
			</view>
		</view>

		<!-- 提交按钮 -->
		<button class="submit-btn" :disabled="submitting" @tap="handleSubmit">
			保存今日记录
		</button>

		<view class="safe-bottom"></view>
	</view>
</template>

<script>
import { createRecord, createWeightRecord, createDietRecord, getProfile, calcExerciseCalories } from '@/utils/api'

export default {
	data() {
		const today = new Date()
		const dateStr = today.getFullYear() + '-' + String(today.getMonth()+1).padStart(2,'0') + '-' + String(today.getDate()).padStart(2,'0')
		return {
			currentDate: dateStr,
			submitting: false,
			userHeight: null,
			form: this.getDefaultForm(),
			exerciseTypes: ['未选择', '跑步', '骑行', '瑜伽', '游泳', '力量训练', '篮球', '足球', '羽毛球', '乒乓球', '跳绳', '快走', '其他'],
			exerciseIndex: 0,
			mealOptions: ['早餐', '午餐', '晚餐', '加餐']
		}
	},
	computed: {
		displayDate() {
			const p = this.currentDate.split('-')
			return p[0] + '年' + parseInt(p[1]) + '月' + parseInt(p[2]) + '日'
		},
		dayLabel() {
			if (!this.currentDate) return ''
			const d = new Date(this.currentDate)
			const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
			return weekdays[d.getDay()]
		},
		computedBMI() {
			if (!this.form.weight || !this.userHeight) return '--'
			const h = this.userHeight / 100
			return (this.form.weight / (h * h)).toFixed(1)
		},
		foodTotalCal() {
			return this.form.foodEntries.reduce((s, e) => s + (parseFloat(e.calories) || 0), 0)
		}
	},
	watch: {
		'form.exercise'() { this.autoCalcCalories() },
		exerciseIndex() { this.autoCalcCalories() }
	},
	onShow() {
		this.loadUserProfile()
	},
	methods: {
		getDefaultForm() {
			return {
				steps: '',
				hrMin: '',
				hrAvg: '',
				hrMax: '',
				sleep: 7,
				water: 6,
				mood: 3,
				exercise: '',
				caloriesBurned: '',
				weight: '',
				bodyFat: '',
				foodEntries: []
			}
		},
		loadUserProfile() {
			getProfile().then(res => {
				this.userHeight = res.height
			}).catch(() => {})
		},
		prevDay() {
			const d = new Date(this.currentDate)
			d.setDate(d.getDate() - 1)
			this.currentDate = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
		},
		nextDay() {
			const d = new Date(this.currentDate)
			d.setDate(d.getDate() + 1)
			this.currentDate = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
		},
		onSleepChange(e) {
			this.form.sleep = e.detail.value
		},
		adjustWater(delta) {
			this.form.water = Math.max(0, Math.min(20, this.form.water + delta))
		},
		onExerciseTypeChange(e) {
			this.exerciseIndex = e.detail.value
		},
		autoCalcCalories() {
			if (this.exerciseIndex > 0 && this.form.exercise > 0) {
				const cal = calcExerciseCalories(this.exerciseTypes[this.exerciseIndex], this.form.exercise)
				this.form.caloriesBurned = String(cal)
			} else {
				this.form.caloriesBurned = ''
			}
		},
		addFoodEntry() {
			this.form.foodEntries.push({
				mealIndex: 0,
				foodName: '',
				amount: '100',
				calories: '',
				protein: '',
				fat: '',
				carbs: ''
			})
		},
		removeFoodEntry(i) {
			this.form.foodEntries.splice(i, 1)
		},
		onFoodMealChange(i, e) {
			this.form.foodEntries[i].mealIndex = e.detail.value
		},
		async handleSubmit() {
			this.submitting = true
			const promises = []
			const date = this.currentDate
			const mealMap = { 0: 'breakfast', 1: 'lunch', 2: 'dinner', 3: 'snack' }

			// 1. 健康记录
			const hasHealth = this.form.steps || this.form.hrMin || this.form.hrAvg || this.form.hrMax || this.form.exercise
			if (hasHealth) {
				const healthData = { date }
				if (this.form.steps) healthData.steps = parseInt(this.form.steps)
				if (this.form.hrMin) healthData.hr_min = parseInt(this.form.hrMin)
				if (this.form.hrAvg) healthData.hr_avg = parseInt(this.form.hrAvg)
				if (this.form.hrMax) healthData.hr_max = parseInt(this.form.hrMax)
				if (this.form.sleep) healthData.sleep = parseFloat(this.form.sleep)
				if (this.form.water) healthData.water = parseInt(this.form.water)
				if (this.form.mood) healthData.mood = this.form.mood * 20 - 10
				if (this.form.exercise) {
					healthData.exercise = parseInt(this.form.exercise)
					if (this.exerciseIndex > 0) {
						healthData.exercise_type = this.exerciseTypes[this.exerciseIndex]
					}
					if (this.form.caloriesBurned) {
						healthData.calories_burned = parseInt(this.form.caloriesBurned)
					}
				}
				promises.push(
					createRecord(healthData).catch(() => {})
				)
			}

			// 2. 体重
			if (this.form.weight) {
				const weightData = { date, weight: parseFloat(this.form.weight) }
				if (this.form.bodyFat) weightData.body_fat = parseFloat(this.form.bodyFat)
				promises.push(
					createWeightRecord(weightData).catch(() => {})
				)
			}

			// 3. 饮食
			this.form.foodEntries.forEach(entry => {
				if (!entry.foodName.trim()) return
				promises.push(
					createDietRecord({
						date,
						meal_type: mealMap[entry.mealIndex],
						food_name: entry.foodName.trim(),
						amount: parseFloat(entry.amount) || 100,
						calories: parseFloat(entry.calories) || 0,
						protein: parseFloat(entry.protein) || 0,
						fat: parseFloat(entry.fat) || 0,
						carbs: parseFloat(entry.carbs) || 0
					}).catch(() => {})
				)
			})

			try {
				await Promise.all(promises)
				uni.showToast({ title: '保存成功!', icon: 'success' })
				this.form = this.getDefaultForm()
				this.exerciseIndex = 0
			} catch (e) {
				uni.showToast({ title: '部分保存失败', icon: 'none' })
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style lang="scss">
.record-page {
	padding: 24rpx;
	min-height: 100vh;
	padding-bottom: 40rpx;
}

.loading-overlay {
	position: fixed;
	inset: 0;
	background: rgba(255,255,255,0.85);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	z-index: 200;
}

.loading-spinner {
	width: 64rpx;
	height: 64rpx;
	border: 4rpx solid #eee;
	border-top-color: #667eea;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

.loading-text {
	font-size: 26rpx;
	color: #667eea;
	margin-top: 20rpx;
}

/* 日期导航 */
.date-section {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 40rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
	background: rgba(255,255,255,0.75);
	backdrop-filter: blur(20px);
	border-radius: 20px;
	box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}

.date-nav {
	font-size: 48rpx;
	color: #667eea;
	padding: 8rpx 16rpx;
}

.date-info { text-align: center; }

.date-text {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
}

.date-label {
	font-size: 22rpx;
	color: #999;
	margin-top: 4rpx;
	display: block;
}

/* 卡片 */
.glass-card {
	background: rgba(255,255,255,0.75);
	backdrop-filter: blur(20px);
	border-radius: 20px;
	padding: 32rpx;
	margin-bottom: 24rpx;
	box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

.section-add {
	font-size: 26rpx;
	color: #667eea;
	padding: 8rpx 16rpx;
}

/* 字段行 */
.field-row {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.field-label {
	width: 180rpx;
	font-size: 26rpx;
	color: #555;
	flex-shrink: 0;
}

.field-input {
	flex: 1;
	height: 72rpx;
	background: #f5f7fa;
	border-radius: 14rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333;
	text-align: right;
}

.ph { color: #bbb; font-size: 26rpx; }

/* 滑动选择 */
.slider-wrap {
	flex: 1;
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.slider-wrap slider { flex: 1; }

.slider-val {
	font-size: 28rpx;
	color: #667eea;
	font-weight: 600;
	width: 80rpx;
	text-align: right;
}

/* 步进器 */
.stepper-wrap {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 16rpx;
}

.stepper-btn {
	width: 56rpx;
	height: 56rpx;
	border-radius: 50%;
	background: #f0f0f0;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	color: #666;
}

.stepper-val {
	font-size: 32rpx;
	font-weight: 600;
	color: #667eea;
	min-width: 60rpx;
	text-align: center;
}

/* 情绪星星 */
.mood-wrap {
	flex: 1;
	display: flex;
	justify-content: flex-end;
	gap: 12rpx;
}

.mood-star {
	font-size: 48rpx;
	color: #ddd;
}

.mood-star.active {
	color: #FFA94D;
	text-shadow: 0 0 8rpx rgba(255,169,77,0.4);
}

/* 选择器 */
.picker-text {
	font-size: 28rpx;
	color: #333;
	padding: 8rpx 0;
}

/* BMI 显示 */
.bmi-display {
	text-align: right;
	font-size: 24rpx;
	color: #999;
	margin-top: 8rpx;
}

.bmi-value {
	color: #667eea;
	font-weight: 600;
}

/* 饮食条目 */
.food-entry {
	background: #fafbfc;
	border-radius: 16rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
}

.food-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}

.food-num {
	font-size: 24rpx;
	color: #999;
}

.food-del {
	font-size: 22rpx;
	color: #e74c3c;
	padding: 4rpx 12rpx;
}

.macro-row {
	display: flex;
	gap: 12rpx;
}

.macro-input {
	flex: 1;
	height: 64rpx;
	background: #f5f7fa;
	border-radius: 12rpx;
	padding: 0 12rpx;
	font-size: 24rpx;
	text-align: center;
}

.food-total {
	text-align: right;
	margin-top: 8rpx;
}

.total-text {
	font-size: 26rpx;
	color: #667eea;
	font-weight: 600;
}

/* 提交按钮 */
.submit-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border-radius: 44rpx;
	color: #fff;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	margin-top: 8rpx;
}

.submit-btn[disabled] {
	opacity: 0.7;
}

.safe-bottom {
	height: 40rpx;
}

.cal-display {
	flex: 1;
	display: flex;
	align-items: center;
	gap: 8rpx;
}
.cal-unit {
	font-size: 26rpx;
	color: #999;
	width: 60rpx;
}
</style>
