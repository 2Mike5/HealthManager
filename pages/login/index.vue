<template>
	<view class="login-page">
		<view class="login-header">
			<view class="logo-area">
				<text class="logo-icon">&#x1f3d7;</text>
				<text class="logo-title">健康管理</text>
				<text class="logo-subtitle">Health Manager</text>
			</view>
		</view>

		<view class="login-card">
			<text class="card-title">欢迎回来</text>
			<text class="card-subtitle">登录以继续使用</text>

			<view class="form-item">
				<text class="form-label">用户名</text>
				<input class="form-input" v-model="username" placeholder="请输入用户名" placeholder-class="placeholder" @input="clearError" />
			</view>

			<view class="form-item">
				<text class="form-label">密码</text>
				<input class="form-input" v-model="password" password placeholder="请输入密码" placeholder-class="placeholder" @input="clearError" />
			</view>

			<view v-if="errorMsg" class="error-text">{{ errorMsg }}</view>

			<button class="login-btn" :disabled="submitting" @tap="handleLogin">
				<text v-if="submitting" class="btn-loading">登录中...</text>
				<text v-else>登 录</text>
			</button>

			<view class="register-link" @tap="goRegister">
				<text>还没有账号？<text class="link-text">立即注册</text></text>
			</view>
		</view>
	</view>
</template>

<script>
import { login } from '@/utils/api'

export default {
	data() {
		return {
			username: '',
			password: '',
			errorMsg: '',
			submitting: false
		}
	},
	methods: {
		clearError() {
			this.errorMsg = ''
		},
		handleLogin() {
			if (!this.username.trim()) {
				this.errorMsg = '请输入用户名'
				return
			}
			if (!this.password) {
				this.errorMsg = '请输入密码'
				return
			}
			this.submitting = true
			this.errorMsg = ''
			login(this.username.trim(), this.password)
				.then(res => {
					uni.setStorageSync('token', res.token)
					uni.setStorageSync('userInfo', res.user)
					uni.switchTab({ url: '/pages/dashboard/index' })
				})
				.catch(err => {
					this.errorMsg = err.message || '登录失败，请检查网络连接'
				})
				.finally(() => {
					this.submitting = false
				})
		},
		goRegister() {
			uni.navigateTo({ url: '/pages/register/index' })
		}
	}
}
</script>

<style lang="scss">
.login-page {
	min-height: 100vh;
	background: linear-gradient(145deg, #4F46E5 0%, #3730A3 100%);
	display: flex;
	flex-direction: column;
	align-items: center;
}

.login-header {
	padding-top: 120rpx;
	padding-bottom: 60rpx;
	text-align: center;
}

.logo-area {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.logo-icon {
	font-size: 80rpx;
}

.logo-title {
	font-size: 48rpx;
	font-weight: bold;
	color: #fff;
	margin-top: 16rpx;
}

.logo-subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.7);
	margin-top: 8rpx;
}

.login-card {
	width: 85%;
	background: rgba(255, 255, 255, 0.95);
	border-radius: 24px;
	padding: 48rpx 40rpx;
	backdrop-filter: blur(20px);
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.card-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #1a1a2e;
}

.card-subtitle {
	font-size: 26rpx;
	color: #666;
	margin-top: 8rpx;
	margin-bottom: 40rpx;
	display: block;
}

.form-item {
	margin-bottom: 28rpx;
}

.form-label {
	font-size: 26rpx;
	color: #333;
	margin-bottom: 12rpx;
	display: block;
}

.form-input {
	height: 88rpx;
	background: #f5f7fa;
	border-radius: 16rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333;
	border: 2rpx solid transparent;
	transition: border-color 0.3s;
}

.form-input:focus {
	border-color: #4F46E5;
}

.placeholder {
	color: #bbb;
	font-size: 28rpx;
}

.error-text {
	color: #e74c3c;
	font-size: 24rpx;
	margin-bottom: 16rpx;
}

.login-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(145deg, #4F46E5 0%, #3730A3 100%);
	border-radius: 44rpx;
	color: #fff;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	margin-top: 16rpx;
}

.login-btn[disabled] {
	opacity: 0.7;
}

.btn-loading {
	font-size: 28rpx;
}

.register-link {
	text-align: center;
	margin-top: 32rpx;
	font-size: 26rpx;
	color: #666;
}

.link-text {
	color: #4F46E5;
	font-weight: 500;
}
</style>
