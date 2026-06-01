<template>
	<view class="profile-page">
		<!-- 用户信息卡片 -->
		<view class="user-card glass-card">
			<view class="user-avatar">
				<text class="avatar-text">{{ avatarChar }}</text>
			</view>
			<view class="user-info">
				<text class="user-name">{{ userInfo.nickname || userInfo.username || '用户' }}</text>
				<text class="user-desc">@{{ userInfo.username || '未知' }}</text>
			</view>
		</view>

		<!-- 统计数据 -->
		<view class="stats-row">
			<view class="stat-item glass-card" @tap="goWeight">
				<text class="stat-num">{{ latestWeight ? latestWeight.weight + 'kg' : '--' }}</text>
				<text class="stat-label">当前体重</text>
			</view>
			<view class="stat-item glass-card" @tap="goExercise">
				<text class="stat-num">{{ todayBurnCalories || '--' }}</text>
				<text class="stat-label">今日消耗</text>
			</view>
			<view class="stat-item glass-card" @tap="goDiet">
				<text class="stat-num">{{ todayCalories || '--' }}</text>
				<text class="stat-label">今日摄入</text>
			</view>
		</view>

		<!-- 功能菜单 -->
		<view class="menu-section glass-card">
			<view class="menu-item" @tap="goWeight">
				<text class="menu-icon menu-icon-weight">&#9878;</text>
				<text class="menu-text">体重管理</text>
				<text class="menu-arrow">&#8250;</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="goDiet">
				<text class="menu-icon menu-icon-diet">&#127858;</text>
				<text class="menu-text">饮食记录</text>
				<text class="menu-arrow">&#8250;</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="goExercise">
				<text class="menu-icon menu-icon-exercise">&#127939;</text>
				<text class="menu-text">运动历史</text>
				<text class="menu-arrow">&#8250;</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="editProfile">
				<text class="menu-icon menu-icon-profile">&#9998;</text>
				<text class="menu-text">个人资料</text>
				<text class="menu-arrow">&#8250;</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="showGoalsModal">
				<text class="menu-icon menu-icon-goals">🎯</text>
				<text class="menu-text">健康目标</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="showNutritionGoalsModal">
				<text class="menu-icon menu-icon-nutrition">🍎</text>
				<text class="menu-text">营养目标</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @tap="goReport">
				<text class="menu-icon menu-icon-report">📊</text>
				<text class="menu-text">健康周报</text>
				<text class="menu-arrow">›</text>
			</view>
			<view class="menu-item">
				<text class="menu-icon menu-icon-dark">&#9790;</text>
				<text class="menu-text">暗黑模式</text>
				<switch :checked="isDarkMode" @change="toggleDarkMode" style="transform:scale(0.8)" />
			</view>
		</view>

		<!-- 退出登录 -->
		<button class="logout-btn" @tap="handleLogout">退出登录</button>
	</view>
</template>

<script>
import { getProfile, getLatestWeight, getDietSummary, updateProfile, fetchRecords, calcExerciseCalories } from '@/utils/api'

export default {
	data() {
		return {
			userInfo: {},
			latestWeight: null,
			todayCalories: 0,
			todayBurnCalories: 0,
			showProfileEdit: false,
			editNickname: '',
			editHeight: '',
			editTargetWeight: '',
			isDarkMode: uni.getStorageSync('darkMode') === true,
			goals: uni.getStorageSync("healthGoals") || { steps: 10000, sleep: 8, water: 8 },
			nutritionGoals: uni.getStorageSync("nutritionGoals") || { protein: 80, fat: 60, carbs: 300 },
		}
	},
	computed: {
		avatarChar() {
			const name = this.userInfo.nickname || this.userInfo.username || 'U'
			return name.charAt(0).toUpperCase()
		}
	},
	onShow() {
		this.loadData()
	},
	methods: {
		loadData() {
			this.userInfo = uni.getStorageSync('userInfo') || {}
			getProfile().then(res => {
				this.userInfo = res
				uni.setStorageSync('userInfo', res)
			}).catch(() => {})

			getLatestWeight().then(res => {
				this.latestWeight = res
			}).catch(() => {})

			const today = new Date()
			const dateStr = today.getFullYear() + '-' + String(today.getMonth()+1).padStart(2,'0') + '-' + String(today.getDate()).padStart(2,'0')
			getDietSummary(dateStr).then(res => {
				this.todayCalories = res.total_calories || 0
			}).catch(() => {})

			// 加载今日运动消耗
			fetchRecords(dateStr, dateStr).then(records => {
				if (records && records.length > 0) {
					const r = records[0]
					this.todayBurnCalories = calcExerciseCalories(r.exerciseType, r.exercise)
				}
			}).catch(() => {})
		},
		goWeight() {
			uni.navigateTo({ url: '/pages/profile/weight' })
		},
		goReport() { uni.navigateTo({ url: "/pages/report/index" }) },
		goDiet() {
			uni.navigateTo({ url: '/pages/profile/diet' })
		},
		goExercise() {
			uni.navigateTo({ url: '/pages/profile/exercise' })
		},
		editProfile() {
			this.editNickname = this.userInfo.nickname || ''
			this.editHeight = this.userInfo.height ? String(this.userInfo.height) : ''
			this.editTargetWeight = this.userInfo.target_weight ? String(this.userInfo.target_weight) : ''
			uni.showModal({
				title: '编辑资料',
				confirmText: '保存',
				editable: true,
				placeholderText: '昵称',
				content: this.editNickname,
				success: (res) => {
					if (res.confirm && res.content) {
						this.editNickname = res.content
						this.saveProfile()
					}
				}
			})
		},
		saveProfile() {
			const data = {}
			if (this.editNickname) data.nickname = this.editNickname
			if (this.editHeight) data.height = parseFloat(this.editHeight)
			if (this.editTargetWeight) data.target_weight = parseFloat(this.editTargetWeight)
			updateProfile(data).then(res => {
				this.userInfo = res
				uni.setStorageSync('userInfo', res)
				uni.showToast({ title: '保存成功', icon: 'success' })
			}).catch(() => {
				uni.showToast({ title: '保存失败', icon: 'none' })
			})
		},
		toggleDarkMode(e) {
			this.isDarkMode = e.detail.value
			uni.setStorageSync('darkMode', this.isDarkMode)
			const bg = this.isDarkMode ? '#1a1a2e' : '#F1F5F9'
			const fc = this.isDarkMode ? '#ffffff' : '#000000'
			uni.setNavigationBarColor({ frontColor: fc, backgroundColor: bg })
			uni.$emit('darkModeChanged', this.isDarkMode)
			getApp().applyTheme(this.isDarkMode)
		},
		showGoalsModal() {
			const g = this.goals
			uni.showModal({
				title: "健康目标设置",
				editable: true,
				placeholderText: "步数目标,睡眠目标(h),饮水目标(杯)",
				content: g.steps + "," + g.sleep + "," + g.water,
				success: (res) => {
					if (res.confirm && res.content) {
						const parts = res.content.split(",")
						const newGoals = {
							steps: parseInt(parts[0]) || g.steps,
							sleep: parseFloat(parts[1]) || g.sleep,
							water: parseInt(parts[2]) || g.water,
						}
						this.goals = newGoals
						uni.setStorageSync("healthGoals", newGoals)
						uni.showToast({ title: "目标已保存", icon: "success" })
					}
				}
			})
		},
		showNutritionGoalsModal() {
			const g = this.nutritionGoals
			uni.showModal({
				title: "营养目标设置",
				editable: true,
				placeholderText: "蛋白质(g),脂肪(g),碳水(g)",
				content: g.protein + "," + g.fat + "," + g.carbs,
				success: (res) => {
					if (res.confirm && res.content) {
						const parts = res.content.split(",")
						const newGoals = {
							protein: parseInt(parts[0]) || g.protein,
							fat: parseInt(parts[1]) || g.fat,
							carbs: parseInt(parts[2]) || g.carbs,
						}
						this.nutritionGoals = newGoals
						uni.setStorageSync("nutritionGoals", newGoals)
						uni.showToast({ title: "营养目标已保存", icon: "success" })
					}
				}
			})
		},
						handleLogout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						uni.removeStorageSync('token')
						uni.removeStorageSync('userInfo')
						uni.reLaunch({ url: '/pages/login/index' })
					}
				}
			})
		}
	}
}
</script>

<style lang="scss">
.profile-page {
	padding: 24rpx;
	min-height: 100vh;
	background: var(--page-bg);
	transition: background 0.3s;
}

.glass-card {
	background: var(--card-bg);
	border-radius: 24rpx;
	border: 1px solid rgba(0,0,0,0.04);
	box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
	padding: 32rpx;
	margin-bottom: 24rpx;
	transition: background 0.3s;
}

.user-card {
	display: flex;
	align-items: center;
	gap: 24rpx;
}

.user-avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #4F46E5, #818CF8);
	display: flex;
	align-items: center;
	justify-content: center;
}

.avatar-text {
	font-size: 40rpx;
	color: #fff;
	font-weight: bold;
}

.user-name {
	font-size: 34rpx;
	font-weight: 600;
	color: var(--text-1);
}

.user-desc {
	font-size: 24rpx;
	color: var(--text-3);
	margin-top: 6rpx;
	display: block;
}

.stats-row {
	display: flex;
	gap: 16rpx;
}

.stat-item {
	flex: 1;
	text-align: center;
	padding: 24rpx 16rpx;
}

.stat-num {
	font-size: 32rpx;
	font-weight: bold;
	color: #4F46E5;
}

.stat-label {
	font-size: 22rpx;
	color: var(--text-3);
	margin-top: 8rpx;
	display: block;
}

.menu-section {
	padding: 0;
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 28rpx 32rpx;
}

.menu-icon {
	font-size: 36rpx;
	width: 48rpx;
	text-align: center;
}

.menu-icon-weight { color: #7C4DFF; }
.menu-icon-diet { color: #FF6B6B; }
.menu-icon-exercise { color: #FFA94D; }
.menu-icon-profile { color: #45B7D1; }
.menu-icon-dark { color: #7C4DFF; }

.menu-text {
	flex: 1;
	font-size: 28rpx;
	color: var(--text-1);
	margin-left: 20rpx;
}

.menu-arrow {
	font-size: 36rpx;
	color: #ccc;
}

.menu-divider {
	height: 1px;
	background: var(--divider);
	margin: 0 32rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	background: var(--card-bg);
	border: 2rpx solid #e74c3c;
	border-radius: 44rpx;
	color: #e74c3c;
	font-size: 30rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 32rpx;
}
</style>
