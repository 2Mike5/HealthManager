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
			<view class="stat-item glass-card" @tap="goWeight">
				<text class="stat-num">{{ latestWeight && latestWeight.bmi ? latestWeight.bmi : '--' }}</text>
				<text class="stat-label">BMI</text>
			</view>
			<view class="stat-item glass-card" @tap="goDiet">
				<text class="stat-num">{{ todayCalories || '--' }}</text>
				<text class="stat-label">今日热量</text>
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
		</view>

		<!-- 退出登录 -->
		<button class="logout-btn" @tap="handleLogout">退出登录</button>
	</view>
</template>

<script>
import { getProfile, getLatestWeight, getDietSummary, updateProfile } from '@/utils/api'

export default {
	data() {
		return {
			userInfo: {},
			latestWeight: null,
			todayCalories: 0,
			showProfileEdit: false,
			editNickname: '',
			editHeight: '',
			editTargetWeight: ''
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
		},
		goWeight() {
			uni.navigateTo({ url: '/pages/profile/weight' })
		},
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
}

.glass-card {
	background: rgba(255,255,255,0.75);
	backdrop-filter: blur(20px);
	border-radius: 20px;
	border: 1px solid rgba(255,255,255,0.6);
	box-shadow: 0 8px 32px rgba(0,0,0,0.08);
	padding: 32rpx;
	margin-bottom: 24rpx;
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
	background: linear-gradient(135deg, #667eea, #764ba2);
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
	color: #1a1a2e;
}

.user-desc {
	font-size: 24rpx;
	color: #999;
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
	color: #667eea;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
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

.menu-text {
	flex: 1;
	font-size: 28rpx;
	color: #333;
	margin-left: 20rpx;
}

.menu-arrow {
	font-size: 36rpx;
	color: #ccc;
}

.menu-divider {
	height: 1px;
	background: #f0f0f0;
	margin: 0 32rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	background: #fff;
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
