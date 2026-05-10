<template>
	<view class="ai-page">
		<!-- 快捷提问 -->
		<view class="quick-section" v-if="messages.length <= 1">
			<text class="section-title">💡 试试问这些</text>
			<view class="quick-grid">
				<view
					class="quick-item"
					v-for="(q, i) in quickQuestions"
					:key="i"
					@click="sendQuickQuestion(q)"
				>
					<text class="quick-text">{{ q.text }}</text>
				</view>
			</view>
		</view>

		<!-- 聊天区域 -->
		<scroll-view
			class="chat-box"
			scroll-y="true"
			:scroll-into-view="scrollTo"
			show-scrollbar="false"
		>
			<view
				v-for="(msg, i) in messages"
				:key="i"
				:id="'msg-' + i"
				class="message-row"
				:class="msg.role === 'user' ? 'user-row' : 'ai-row'"
			>
				<view class="avatar" :class="msg.role">
					<uni-icons
						:type="msg.role === 'user' ? 'person-filled' : 'chatboxes'"
						size="18"
						color="#fff"
					></uni-icons>
				</view>
				<view class="bubble" :class="msg.role">
					<!-- 文字回答 -->
					<text class="msg-text">{{ msg.content }}</text>

					<!-- 图表（仅在 AI 回复有 chart_config 时显示） -->
					<view v-if="msg.chartConfig" class="chart-in-msg">
						<qiun-data-charts
							:type="msg.chartConfig.type"
							:chartData="msg.chartConfig.chartData"
							:opts="msg.chartConfig.opts"
							height="320rpx"
						/>
					</view>

					<!-- SQL 引用（调试 / 透明度） -->
					<text v-if="msg.sql" class="sql-ref">查询：{{ msg.sql }}</text>
				</view>
			</view>
			<view v-if="loading" class="message-row ai-row">
				<view class="avatar ai">
					<uni-icons type="chatboxes" size="18" color="#fff"></uni-icons>
				</view>
				<view class="bubble ai typing">
					<text class="dot-anim">.</text>
					<text class="dot-anim">.</text>
					<text class="dot-anim">.</text>
				</view>
			</view>
			<view id="bottom-anchor" style="height:1px"></view>
		</scroll-view>

		<!-- 输入区域 -->
		<view class="input-bar">
			<uni-easyinput
				v-model="inputText"
				placeholder="输入你的健康问题..."
				:inputBorder="false"
				class="input-field"
				@confirm="sendMessage"
			></uni-easyinput>
			<button class="send-btn" @click="sendMessage" :disabled="!inputText.trim()">
				<uni-icons type="paperplane" size="20" color="#fff"></uni-icons>
			</button>
		</view>
	</view>
</template>

<script>
const API_BASE = 'http://localhost:5001/api'

export default {
	data() {
		return {
			inputText: '',
			loading: false,
			scrollTo: '',
			messages: [
				{
					role: 'ai',
					content: '你好！我是你的 AI 健康助手。\n问我关于健康数据的问题，我会查询数据库并回答你。\n\n例如：\n• "今天步数多少"\n• "近7天心率趋势"\n• "上周睡眠怎么样"'
				}
			],
			quickQuestions: [
				{ text: '今天步数多少', icon: 'flag', color: '#4CAF50' },
				{ text: '近7天心率趋势', icon: 'heart', color: '#F44336' },
				{ text: '上周睡眠怎么样', icon: 'moon', color: '#3F51B5' },
				{ text: '本月健康评分', icon: 'star', color: '#FF9800' }
			]
		}
	},
	methods: {
		sendQuickQuestion(q) {
			this.addMessage('user', q.text)
			this.askAI(q.text)
		},
		sendMessage() {
			const text = this.inputText.trim()
			if (!text || this.loading) return
			this.inputText = ''
			this.addMessage('user', text)
			this.askAI(text)
		},
		addMessage(role, content, extras = {}) {
			this.messages.push({ role, content, ...extras })
			this.scrollToBottom()
		},
		askAI(question) {
			this.loading = true
			uni.request({
				url: API_BASE + '/ai/query',
				method: 'POST',
				data: {
					question,
					messages: this.messages.slice(-10).map(m => ({
						role: m.role,
						content: m.content
					}))
				},
				timeout: 20000,
				success: (res) => {
					if (res.data && res.data.code === 200) {
						const d = res.data.data
						if (d.type === 'chart' && d.chart_config) {
							this.addMessage('ai', d.answer, {
								chartConfig: d.chart_config,
								sql: d.sql
							})
						} else {
							this.addMessage('ai', d.answer, {
								sql: d.sql
							})
						}
					} else {
						this.addMessage('ai', '抱歉，查询出错了：' + ((res.data && res.data.message) || '未知错误'))
					}
				},
				fail: (err) => {
					let msg = "\u26a0 请求失败"
					if (err.errMsg && err.errMsg.indexOf("timeout") > -1)
						msg = "\u26a0 AI 响应超时，请稍后重试"
					else
						msg = "\u26a0 无法连接到服务器，请确认后端 Python 服务已启动。\n\n运行：`cd server && /f/anaconda/python app.py`"
					this.addMessage("ai", msg)
				},
				complete: () => {
					this.loading = false
				}
			})
		},
		scrollToBottom() {
			setTimeout(() => {
				this.scrollTo = 'bottom-anchor'
			}, 150)
		}
	}
}
</script>

<style lang="scss">
.ai-page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	overflow: hidden;
	box-sizing: border-box;
	background: #f5f6fa;
}

.quick-section {
	flex-shrink: 0;
	padding: 16px 16px 0;
}

.section-title {
	font-size: 16px;
	font-weight: bold;
	color: #333;
	display: block;
	margin-bottom: 10px;
}

.quick-grid {
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
	gap: 8px;
}

.quick-item {
	background: #fff;
	border-radius: 20px;
	padding: 10px 18px;
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 14px;
	color: #555;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	border: 1px solid #eee;
}

.chat-box {
	flex: 1;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
	padding: 16px;
}

.message-row {
	display: flex;
	margin-bottom: 16px;
	align-items: flex-start;
}

.user-row {
	flex-direction: row-reverse;
}

.ai-row {
	flex-direction: row;
}

.avatar {
	width: 36px;
	height: 36px;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;

	&.user {
		background: #4CAF50;
		margin-left: 8px;
	}

	&.ai {
		background: linear-gradient(135deg, #667eea, #764ba2);
		margin-right: 8px;
	}
}

.bubble {
	max-width: 75%;
	padding: 12px 16px;
	border-radius: 16px;
	font-size: 14px;
	line-height: 1.6;

	&.user {
		background: #4CAF50;
		color: #fff;
		border-radius: 16px 4px 16px 16px;
	}

	&.ai {
		background: #fff;
		color: #333;
		border-radius: 4px 16px 16px 16px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
	}

	&.typing {
		display: flex;
		gap: 2px;
		padding: 14px 18px;
	}
}

.msg-text {
	white-space: pre-wrap;
	word-break: break-word;
}

.chart-in-msg {
	margin-top: 12px;
	padding-top: 12px;
	border-top: 1px solid #f0f0f0;
	width: 100%;
}

.sql-ref {
	display: block;
	margin-top: 8px;
	font-size: 11px;
	color: #bbb;
	font-family: monospace;
}

.dot-anim {
	font-size: 24px;
	line-height: 1;
	animation: blink 1.4s infinite both;
}

.dot-anim:nth-child(2) {
	animation-delay: 0.2s;
}

.dot-anim:nth-child(3) {
	animation-delay: 0.4s;
}

@keyframes blink {
	0%, 80%, 100% { opacity: 0; }
	40% { opacity: 1; }
}

.input-bar {
	flex-shrink: 0;
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 8px;
	padding: 8px 16px;
	padding-bottom: calc(8px + env(safe-area-inset-bottom));
	background: #f5f6fa;
	border-top: 1px solid #eee;
}

.input-field {
	flex: 1;
	background: #fff;
	border-radius: 24px;
	padding: 0 12px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.send-btn {
	width: 44px;
	height: 44px;
	border-radius: 50%;
	background: linear-gradient(135deg, #667eea, #764ba2);
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0;
	margin: 0;
	line-height: 1;

	&:disabled {
		background: #ccc;
	}
}
</style>
