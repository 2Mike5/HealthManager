<template>
	<view class="register-page">
		<view class="register-header">
			<text class="header-title">创建账号</text>
			<text class="header-sub">开启你的健康管理之旅</text>
		</view>

		<view class="register-card">
			<view class="form-item">
				<text class="form-label">用户名</text>
				<input class="form-input" v-model="username" placeholder="至少2个字符" placeholder-class="placeholder" @input="clearError('username')" />
				<text v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</text>
			</view>

			<view class="form-item">
				<text class="form-label">昵称（可选）</text>
				<input class="form-input" v-model="nickname" placeholder="给自己取个名字" placeholder-class="placeholder" />
			</view>

			<view class="form-item">
				<text class="form-label">密码</text>
				<input class="form-input" v-model="password" password placeholder="至少6个字符" placeholder-class="placeholder" @input="clearError('password')" />
				<text v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</text>
			</view>

			<view class="form-item">
				<text class="form-label">确认密码</text>
				<input class="form-input" v-model="confirmPwd" password placeholder="再次输入密码" placeholder-class="placeholder" @input="clearError('confirmPwd')" />
				<text v-if="fieldErrors.confirmPwd" class="field-error">{{ fieldErrors.confirmPwd }}</text>
			</view>

			<view v-if="errorMsg" class="error-text">{{ errorMsg }}</view>

			<button class="register-btn" :disabled="submitting" @tap="handleRegister">
				<text v-if="submitting" class="btn-loading">注册中...</text>
				<text v-else>注 册</text>
			</button>

			<view class="login-link" @tap="goLogin">
				<text>已有账号？<text class="link-text">返回登录</text></text>
			</view>
		</view>
	</view>
</template>

<script>
import { register } from '@/utils/api'

export default {
	data() {
		return {
			username: '',
			nickname: '',
			password: '',
			confirmPwd: '',
			errorMsg: '',
			fieldErrors: {},
			submitting: false
		}
	},
	methods: {
		clearError(field) {
			this.errorMsg = ''
			if (field) {
				const errs = { ...this.fieldErrors }
				delete errs[field]
				this.fieldErrors = errs
			}
		},
		validate() {
			const errs = {}
			if (!this.username.trim() || this.username.trim().length < 2) {
				errs.username = '用户名至少2个字符'
			}
			if (!this.password || this.password.length < 6) {
				errs.password = '密码至少6个字符'
			}
			if (this.password !== this.confirmPwd) {
				errs.confirmPwd = '两次密码输入不一致'
			}
			this.fieldErrors = errs
			return Object.keys(errs).length === 0
		},
		handleRegister() {
			if (!this.validate()) return

			this.submitting = true
			this.errorMsg = ''
			register(this.username.trim(), this.password, this.nickname.trim() || undefined)
				.then(res => {
					uni.setStorageSync('token', res.token)
					uni.setStorageSync('userInfo', res.user)
					uni.switchTab({ url: '/pages/dashboard/index' })
				})
				.catch(err => {
					this.errorMsg = err.message || '注册失败，请检查网络连接'
				})
				.finally(() => {
					this.submitting = false
				})
		},
		goLogin() {
			uni.navigateBack()
		}
	}
}
</script>

<style lang="scss">
.register-page {
	min-height: 100vh;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	flex-direction: column;
	align-items: center;
}

.register-header {
	padding-top: 100rpx;
	padding-bottom: 40rpx;
	text-align: center;
}

.header-title {
	font-size: 44rpx;
	font-weight: bold;
	color: #fff;
}

.header-sub {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.7);
	margin-top: 12rpx;
	display: block;
}

.register-card {
	width: 85%;
	background: rgba(255, 255, 255, 0.95);
	border-radius: 24px;
	padding: 40rpx;
	backdrop-filter: blur(20px);
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.form-item {
	margin-bottom: 24rpx;
}

.form-label {
	font-size: 26rpx;
	color: #333;
	margin-bottom: 10rpx;
	display: block;
}

.form-input {
	height: 80rpx;
	background: #f5f7fa;
	border-radius: 14rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333;
}

.placeholder {
	color: #bbb;
	font-size: 28rpx;
}

.field-error {
	color: #e74c3c;
	font-size: 22rpx;
	margin-top: 6rpx;
	display: block;
}

.error-text {
	color: #e74c3c;
	font-size: 24rpx;
	margin-bottom: 12rpx;
	text-align: center;
}

.register-btn {
	width: 100%;
	height: 84rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 42rpx;
	color: #fff;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	margin-top: 16rpx;
}

.register-btn[disabled] {
	opacity: 0.7;
}

.btn-loading {
	font-size: 28rpx;
}

.login-link {
	text-align: center;
	margin-top: 28rpx;
	font-size: 26rpx;
	color: #666;
}

.link-text {
	color: #667eea;
	font-weight: 500;
}
</style>
