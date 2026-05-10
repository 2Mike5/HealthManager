<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
			// 认证守卫：检查 token
			const token = uni.getStorageSync('token')
			if (!token) {
				const pages = getCurrentPages()
				const currentPage = pages.length > 0 ? pages[pages.length - 1].route : ''
				if (currentPage !== 'pages/login/index' && currentPage !== 'pages/register/index') {
					uni.reLaunch({ url: '/pages/login/index' })
				}
			}
			// 初始化暗黑模式
			const darkMode = uni.getStorageSync('darkMode')
			if (darkMode) {
				document.documentElement.setAttribute('data-theme', 'dark')
			}
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	/*每个页面公共css */
	@import '@/uni_modules/uni-scss/index.scss';
	/* #ifndef APP-NVUE */
	@import '@/static/customicons.css';
	// 设置整个项目的背景色
	page {
		background-color: #f5f5f5;
	}

	/* #endif */
	.example-info {
		font-size: 14px;
		color: #333;
		padding: 10px;
	}

	/* ── 暗黑模式 ── */
	[data-theme="dark"] page {
		background: #0f0f23;
	}
	[data-theme="dark"] {
		--bg-page: #0f0f23;
		--bg-card: rgba(255, 255, 255, 0.06);
		--text-primary: #e8e8f0;
		--text-secondary: #a0a0b8;
		--text-tertiary: #6a6a82;
	}
	[data-theme="dark"] .glass-card,
	[data-theme="dark"] .menu-section,
	[data-theme="dark"] .login-card,
	[data-theme="dark"] .register-card,
	[data-theme="dark"] .date-section {
		background: rgba(255, 255, 255, 0.06) !important;
		border-color: rgba(255, 255, 255, 0.08) !important;
	}
	[data-theme="dark"] .dark-card {
		background: linear-gradient(135deg, #0a0a1a, #0f0f2e, #0a1a3a) !important;
	}
	[data-theme="dark"] .greeting-card {
		background: linear-gradient(135deg, #2a2a5a, #3a2a6a) !important;
	}
	[data-theme="dark"] .card-title,
	[data-theme="dark"] .section-title,
	[data-theme="dark"] .form-label,
	[data-theme="dark"] .menu-text,
	[data-theme="dark"] .ring-value,
	[data-theme="dark"] .current-value,
	[data-theme="dark"] .date-text {
		color: var(--text-primary) !important;
	}
	[data-theme="dark"] .card-footer text,
	[data-theme="dark"] .stat-label,
	[data-theme="dark"] .greeting-sub,
	[data-theme="dark"] .user-desc,
	[data-theme="dark"] .stat-num,
	[data-theme="dark"] .summary-num {
		color: var(--text-secondary) !important;
	}
	[data-theme="dark"] .bubble.ai {
		background: rgba(255, 255, 255, 0.08) !important;
		color: var(--text-primary) !important;
	}
	[data-theme="dark"] .bubble.user {
		background: linear-gradient(135deg, #4a4a8a, #5a3d8a) !important;
	}
	[data-theme="dark"] .form-input,
	[data-theme="dark"] .add-input,
	[data-theme="dark"] .field-input,
	[data-theme="dark"] .uni-easyinput {
		background: rgba(255, 255, 255, 0.08) !important;
		color: var(--text-primary) !important;
	}
	[data-theme="dark"] .input-bar {
		background: #0f0f23 !important;
		border-top-color: rgba(255,255,255,0.08) !important;
	}
	[data-theme="dark"] .dashboard,
	[data-theme="dark"] .ai-page,
	[data-theme="dark"] .record-page,
	[data-theme="dark"] .weight-page,
	[data-theme="dark"] .diet-page,
	[data-theme="dark"] .exercise-page,
	[data-theme="dark"] .profile-page,
	[data-theme="dark"] .login-page,
	[data-theme="dark"] .register-page {
		background: #0f0f23 !important;
	}
	[data-theme="dark"] .quick-item {
		background: rgba(255,255,255,0.06) !important;
		border-color: rgba(255,255,255,0.08) !important;
		color: var(--text-secondary) !important;
	}
	[data-theme="dark"] .history-item,
	[data-theme="dark"] .food-item {
		border-bottom-color: rgba(255,255,255,0.06) !important;
	}
	[data-theme="dark"] .food-entry {
		background: rgba(255,255,255,0.04) !important;
	}
	[data-theme="dark"] .stepper-btn {
		background: rgba(255,255,255,0.1) !important;
	}
	[data-theme="dark"] .mood-star {
		color: rgba(255,255,255,0.2) !important;
	}
	[data-theme="dark"] .mood-star.active {
		color: #FFA94D !important;
	}
	[data-theme="dark"] .menu-divider {
		background: rgba(255,255,255,0.08) !important;
	}
</style>
