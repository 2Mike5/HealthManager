// ════════════════════════════════════
// 数字滚动动画 — 从 0 滚动到目标值
// 用法: <text>{{ animatedSteps }}</text>
// 在 onMounted 中调用 animateNumber('steps', 8520, 1200)
// ════════════════════════════════════

export default {
  data() {
    return {
      // ── 需要动态滚动的数值 ──
      animatedSteps: 0,
      animatedHeartAvg: 0,
      animatedSleep: 0,
      animatedWater: 0,
      animatedScore: 0,
    }
  },

  methods: {
    /**
     * 数字滚动动画
     * @param {string} key      - data 中对应的字段名（如 'animatedSteps'）
     * @param {number} target   - 目标值
     * @param {number} duration - 动画时长 ms（默认 1000）
     * @param {number} decimals - 小数位数（0 = 整数）
     */
    animateNumber(key, target, duration = 1000, decimals = 0) {
      // 如果目标为 0 或不存在，直接显示
      if (!target || target === 0) {
        this[key] = 0
        return
      }

      let startTime = null
      const startValue = 0
      const change = target - startValue

      const step = (timestamp) => {
        if (!startTime) startTime = timestamp
        const progress = Math.min((timestamp - startTime) / duration, 1)
        // easeOutExpo: 开始快结束慢
        const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
        this[key] = Number((startValue + change * eased).toFixed(decimals))
        if (progress < 1) {
          requestAnimationFrame(step)
        }
      }
      requestAnimationFrame(step)
    },

    /**
     * 批量启动多个数值动画
     * @param {Array} items - [{key, target, duration, decimals}, ...]
     */
    animateNumbers(items) {
      items.forEach(item => {
        this.animateNumber(
          item.key,
          item.target,
          item.duration || 1000,
          item.decimals || 0
        )
      })
    },

    /**
     * 开启动画后自动生成数值跳动时的弹性效果
     * （配合 CSS animation 使用，触发一次弹性脉冲）
     */
    triggerBounce(el) {
      if (!el) return
      el.classList.remove('bounce-effect')
      // 强制回流后重新添加以重播动画
      void el.offsetWidth
      el.classList.add('bounce-effect')
    }
  }
}
