<script>
	export default {
		globalData: {
			isDarkMode: false
		},
		onLaunch: function() {
			const dm = uni.getStorageSync('darkMode') === true
			this.globalData.isDarkMode = dm
			this.applyTheme(dm)
		},
		onShow: function() {
			// #ifndef MP
			document.documentElement.setAttribute('data-theme', this.globalData.isDarkMode ? 'dark' : 'light')
			// #endif
		},
		methods: {
			applyTheme(isDark) {
				this.globalData.isDarkMode = isDark
				// #ifndef MP
				document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
				// #endif
				const bg = isDark ? '#0F172A' : '#F1F5F9'
				const fc = isDark ? '#ffffff' : '#000000'
				uni.setNavigationBarColor({ frontColor: fc, backgroundColor: bg })
			}
		}
	}
</script>

<style lang="scss">
	/*每个页面公共css */
	@import '@/uni_modules/uni-scss/index.scss';
	/* #ifndef APP-NVUE */
	@import '@/static/customicons.css';

	/* ═══════════ 主题色变量 ═══════════ */
	:root {
		--bg: #F1F5F9;
		--card-bg: #FFFFFF;
		--card-bg-glass: rgba(255, 255, 255, 0.75);
		--card-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
		--text-1: #1A1A2E;
		--text-2: #555555;
		--text-3: #999999;
		--divider: #F0F0F0;
		--input-bg: #F5F7FA;
		--food-entry-bg: #FAFBFC;
		--hero-bg-start: #6B73FF;
		--hero-bg-end: #3B27FE;
		--page-bg: #F1F5F9;
		--nav-bg: #4F46E5;
		--trend-bg: #FFFFFF;
		--shadow-card: 0 4px 24px rgba(0, 0, 0, 0.05);
		--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.08);
	}

	[data-theme="dark"] {
		--bg: #0F172A;
		--card-bg: #1E293B;
		--card-bg-glass: rgba(30, 41, 59, 0.85);
		--card-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
		--text-1: #E2E8F0;
		--text-2: #94A3B8;
		--text-3: #64748B;
		--divider: #1E293B;
		--input-bg: #1E293B;
		--food-entry-bg: #1A2332;
		--hero-bg-start: #1E3A5F;
		--hero-bg-end: #0F172A;
		--page-bg: #0F172A;
		--nav-bg: #1E3A5F;
		--trend-bg: #1E293B;
		--shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
		--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.3);
	}

	page {
		background-color: var(--page-bg);
		transition: background-color 0.3s ease;
		color: var(--text-1);
	}

	/* #endif */
	.example-info {
		font-size: 14px;
		color: #333;
		padding: 10px;
	}
</style>
