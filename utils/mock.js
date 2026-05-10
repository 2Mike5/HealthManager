/**
 * mock.js — 健康数据模拟生成器
 *
 * 生成每日的健康数据，支持按日/周/月视图过滤
 */

function randInt(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min
}

function randFloat(min, max, decimals = 1) {
	const val = Math.random() * (max - min) + min
	return Math.round(val * Math.pow(10, decimals)) / Math.pow(10, decimals)
}

function formatDate(date) {
	const y = date.getFullYear()
	const m = String(date.getMonth() + 1).padStart(2, '0')
	const d = String(date.getDate()).padStart(2, '0')
	return `${y}-${m}-${d}`
}

function formatDayLabel(date) {
	const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
	return weekdays[date.getDay()]
}

/**
 * 生成单日健康数据
 */
function generateDailyData(date) {
	const steps = randInt(3000, 15000)

	// 心率：基础 60-75，加上步数波动
	const baseHR = randInt(62, 72)
	const hrMin = baseHR + randInt(-5, 0)
	const hrAvg = baseHR + randInt(0, 8)
	const hrMax = baseHR + randInt(8, 25)

	const heartRate = hrAvg // 兼容旧字段

	const sleep = randFloat(5, 9.5, 1)
	const water = randInt(3, 10)
	const exercise = randInt(0, 90)   // 运动时长（分钟）
	const mood = randInt(40, 100)      // 情绪评分

	// 健康评分计算
	let score = 60
	if (steps > 10000) score += 25; else if (steps > 8000) score += 20; else if (steps > 5000) score += 10; else score -= 10
	if (hrAvg >= 60 && hrAvg <= 80) score += 10; else if (hrAvg <= 90) score += 5; else score -= 5
	if (sleep >= 7 && sleep <= 8) score += 10; else if (sleep >= 6) score += 5; else score -= 5
	if (water >= 8) score += 10; else if (water >= 5) score += 5; else score -= 5
	if (exercise >= 30) score += 10; else if (exercise >= 15) score += 5; else score -= 5
	if (mood >= 70) score += 10; else if (mood >= 50) score += 5; else score -= 5

	const healthScore = Math.max(0, Math.min(100, score))

	return {
		date: formatDate(date),
		dayLabel: formatDayLabel(date),
		steps,
		heartRate,
		hrMin: Math.max(45, hrMin),
		hrAvg,
		hrMax: Math.min(140, hrMax),
		sleep,
		water,
		exercise,
		exerciseType: null,
		mood,
		healthScore
	}
}

/**
 * 生成近 N 天的健康数据（今天在第一个）
 */
export function generateMockData(days = 30) {
	const today = new Date()
	const result = []
	for (let i = 0; i < days; i++) {
		const d = new Date(today)
		d.setDate(today.getDate() - i)
		result.push(generateDailyData(d))
	}
	return result
}

/**
 * 获取今日数据
 */
export function getTodayData(data) {
	return data && data.length > 0 ? data[0] : null
}

/**
 * 获取指定日期所在周的日期范围
 */
export function getWeekRange(date = new Date()) {
	const d = new Date(date)
	const day = d.getDay()
	const diff = d.getDate() - day + (day === 0 ? -6 : 1) // 周一为一周开始
	const monday = new Date(d.setDate(diff))
	const sunday = new Date(monday)
	sunday.setDate(monday.getDate() + 6)
	return { start: monday, end: sunday }
}

/**
 * 获取指定日期所在月的日期范围
 */
export function getMonthRange(date = new Date()) {
	const d = new Date(date)
	const start = new Date(d.getFullYear(), d.getMonth(), 1)
	const end = new Date(d.getFullYear(), d.getMonth() + 1, 0)
	return { start, end }
}

/**
 * 按视图过滤数据
 * @param {Array} data - 全量数据
 * @param {'day'|'week'|'month'} view
 * @param {Date} refDate - 参考日期
 * @returns {Array}
 */
export function filterByView(data, view, refDate = new Date()) {
	if (!data || data.length === 0) return []
	if (view === 'day') return data.slice(0, 1)

	let rangeStart, rangeEnd
	if (view === 'week') {
		const r = getWeekRange(refDate)
		rangeStart = r.start
		rangeEnd = r.end
	} else {
		const r = getMonthRange(refDate)
		rangeStart = r.start
		rangeEnd = r.end
	}

	const fmtStart = formatDate(rangeStart)
	const fmtEnd = formatDate(rangeEnd)

	return data.filter(d => d.date >= fmtStart && d.date <= fmtEnd)
}

/**
 * 计算平均值
 */
export function average(data, field) {
	if (!data || data.length === 0) return 0
	const sum = data.reduce((acc, d) => acc + (d[field] || 0), 0)
	return Math.round((sum / data.length) * 10) / 10
}

/**
 * 获取某个月份的日历网格数据
 * @param {number} year
 * @param {number} month (1-12)
 * @param {Array} sleepData - 含 date, sleep 字段的数据
 * @returns {Array<{date, day, sleep, isCurrentMonth}>}
 */
export function getMonthCalendar(year, month, sleepData = []) {
	const firstDay = new Date(year, month - 1, 1)
	const lastDay = new Date(year, month, 0)
	const daysInMonth = lastDay.getDate()
	const startWeekday = firstDay.getDay() // 0=Sun

	const dataMap = {}
	sleepData.forEach(d => {
		if (d.date) dataMap[d.date] = d.sleep
	})

	const grid = []
	// 空白填充
	for (let i = 0; i < startWeekday; i++) {
		grid.push({ date: '', day: 0, sleep: null, isCurrentMonth: false })
	}
	// 日期填充
	for (let d = 1; d <= daysInMonth; d++) {
		const dateObj = new Date(year, month - 1, d)
		const dateStr = formatDate(dateObj)
		grid.push({
			date: dateStr,
			day: d,
			sleep: dataMap[dateStr] || null,
			isCurrentMonth: true
		})
	}
	return grid
}

/**
 * 获取鼓励语
 */
export function getEncouragement() {
	const messages = [
		'今天也是元气满满的一天！',
		'每一次坚持，都是健康的积累 💪',
		'照顾好自己的身体，是对未来最好的投资',
		'健康的生活方式，从每一个小习惯开始',
		'你今天的努力，是明天健康的基石',
		'听身体的话，它会给你最好的回报',
		'运动是最好的医生，坚持是最好的良药',
		'每一天都是重新开始的机会',
	]
	return messages[randInt(0, messages.length - 1)]
}
