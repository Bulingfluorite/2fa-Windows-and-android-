<template>
	<view class="container">
		<view class="header">
			<text class="header-title">TOTP验证码</text>
		</view>

		<view class="card">
			<view class="form-group">
				<text class="form-label">输入密钥</text>
				<view class="input-row">
					<input
						class="form-control"
						:type="showSecret ? 'text' : 'password'"
						v-model="secretInput"
						placeholder="输入密钥"
						@input="handleSecretInput"
					/>
					<view class="btn-toggle" @click="showSecret = !showSecret">
						<text class="btn-toggle-text">{{ showSecret ? '隐藏' : '显示' }}</text>
					</view>
				</view>
			</view>
		</view>

		<view class="card" v-if="tokenVisible">
			<view class="token-display">
				<text class="token-code" @click="copyToken">{{ formattedCode }}</text>
				<text class="token-hint">点击复制验证码</text>
				<view class="timer-container">
					<view class="timer-bar">
						<view
							class="timer-progress"
							:style="{ width: progressPercent + '%', background: countdown <= 5 ? 'linear-gradient(90deg, #ff4d4d 0%, #ff8080 100%)' : '' }"
						></view>
					</view>
					<view class="timer-text">
						<text>剩余 {{ countdown }} 秒</text>
					</view>
					<view class="offset-row">
						<view class="offset-btn" @click="adjustOffset(-5)"><text class="offset-btn-text">-5s</text></view>
						<text class="offset-label">偏移: {{ timeOffset }}s</text>
						<view class="offset-btn" @click="adjustOffset(5)"><text class="offset-btn-text">+5s</text></view>
					</view>
				</view>
			</view>
		</view>

		<view class="footer">
			<text class="footer-text">本工具在本地运行，不会存储或传输您的密钥</text>
		</view>
	</view>
</template>

<script>
	import { parseSecret, generateTOTP, formatCode } from '@/utils/totp.js'

	export default {
		data() {
			return {
				secretInput: '',
				showSecret: false,
				tokenVisible: false,
				currentSecret: '',
				digits: 6,
				period: 30,
				algorithm: 'SHA1',
				formattedCode: '000 000',
				countdown: 30,
				progressPercent: 100,
				timeOffset: 0,
				updateInterval: null
			}
		},
		onLoad() {
			this.timeOffset = uni.getStorageSync('timeOffset') || 0
		},
		onUnload() {
			if (this.updateInterval) {
				clearInterval(this.updateInterval)
			}
		},
		methods: {
			handleSecretInput() {
				const secret = this.secretInput.trim()

				if (!secret) {
					this.tokenVisible = false
					if (this.updateInterval) {
						clearInterval(this.updateInterval)
						this.updateInterval = null
					}
					return
				}

				try {
					const result = parseSecret(secret)
					if (result.success) {
						this.currentSecret = result.secret
						this.digits = result.digits
						this.period = result.period
						this.algorithm = result.algorithm
						this.tokenVisible = true
						this.startTokenUpdate()
					} else {
						this.tokenVisible = false
					}
				} catch (error) {
					this.tokenVisible = false
				}
			},

			startTokenUpdate() {
				if (this.updateInterval) {
					clearInterval(this.updateInterval)
				}
				this.updateToken()
				this.updateInterval = setInterval(() => {
					this.updateToken()
				}, 1000)
			},

			updateToken() {
				if (!this.currentSecret) return

				try {
					const code = generateTOTP(this.currentSecret, this.digits, this.period, this.algorithm, this.timeOffset)
					this.formattedCode = formatCode(code)

					const epoch = Math.floor(Date.now() / 1000) + this.timeOffset
					this.countdown = this.period - (epoch % this.period)
					this.progressPercent = (this.countdown / this.period) * 100
				} catch (error) {
					this.formattedCode = '错误'
				}
			},

			copyToken() {
				const code = this.formattedCode.replace(/\s/g, '')
				uni.setClipboardData({
					data: code,
					success: () => {
						uni.showToast({
							title: '已复制到剪贴板',
							icon: 'success',
							duration: 2000
						})
					}
				})
			},

			adjustOffset(delta) {
				this.timeOffset += delta
				uni.setStorageSync('timeOffset', this.timeOffset)
				this.updateToken()
			}
		}
	}
</script>

<style>
	page {
		background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
		min-height: 100vh;
	}

	.container {
		padding: 30rpx;
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.header {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-bottom: 40rpx;
		padding-bottom: 30rpx;
		border-bottom: 1rpx solid #dee2e6;
	}

	.header-title {
		font-size: 48rpx;
		font-weight: 600;
		color: #4e54c8;
	}

	.card {
		background-color: #ffffff;
		border-radius: 24rpx;
		padding: 40rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.08);
	}

	.form-group {
		width: 100%;
	}

	.form-label {
		font-size: 28rpx;
		font-weight: 500;
		color: #212529;
		margin-bottom: 16rpx;
		display: block;
	}

	.input-row {
		display: flex;
		flex-direction: row;
		align-items: center;
	}

	.form-control {
		flex: 1;
		background-color: #f8f9fa;
		color: #212529;
		border: 2rpx solid #ced4da;
		border-right: none;
		border-radius: 16rpx 0 0 16rpx;
		padding: 20rpx 24rpx;
		font-size: 28rpx;
		height: 80rpx;
		box-sizing: border-box;
	}

	.btn-toggle {
		background-color: #f8f9fa;
		border: 2rpx solid #ced4da;
		border-radius: 0 16rpx 16rpx 0;
		padding: 0 24rpx;
		height: 80rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.btn-toggle-text {
		color: #6c757d;
		font-size: 24rpx;
	}

	.token-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40rpx 0;
		text-align: center;
	}

	.token-code {
		font-family: 'Courier New', monospace;
		font-size: 80rpx;
		font-weight: bold;
		letter-spacing: 6rpx;
		margin-bottom: 20rpx;
		color: #4e54c8;
	}

	.token-hint {
		color: #6c757d;
		font-size: 24rpx;
		margin-bottom: 30rpx;
	}

	.timer-container {
		width: 100%;
		max-width: 500rpx;
	}

	.timer-bar {
		height: 12rpx;
		background-color: rgba(0, 0, 0, 0.1);
		border-radius: 6rpx;
		overflow: hidden;
	}

	.timer-progress {
		height: 100%;
		background: linear-gradient(90deg, #4e54c8 0%, #8f94fb 100%);
		border-radius: 6rpx;
	}

	.timer-text {
		margin-top: 16rpx;
		font-size: 24rpx;
		color: #6c757d;
		text-align: center;
	}

	.offset-row {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		margin-top: 20rpx;
	}

	.offset-btn {
		width: 80rpx;
		height: 60rpx;
		background-color: #f0f0f0;
		border-radius: 10rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.offset-btn-text {
		font-size: 24rpx;
		color: #4e54c8;
	}

	.offset-label {
		font-size: 24rpx;
		color: #6c757d;
		margin: 0 20rpx;
	}

	.footer {
		text-align: center;
		padding: 40rpx 0;
		margin-top: auto;
		border-top: 1rpx solid #dee2e6;
	}

	.footer-text {
		font-size: 24rpx;
		color: #6c757d;
	}
</style>
