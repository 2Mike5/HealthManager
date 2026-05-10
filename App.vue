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
</style>
