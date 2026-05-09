/**
 * api.js — 后端 API 客户端，失败时自动回退到 mock 数据
 *
 * API 字段为 snake_case（如 heart_rate），自动映射为前端 camelCase（如 heartRate）
 */

import { generateMockData } from '@/utils/mock'

const API_BASE = 'http://localhost:5001/api'
const REQUEST_TIMEOUT = 5000

// snake_case → camelCase 字段映射
const SNAKE_TO_CAMEL = {
	heart_rate: 'heartRate',
	hr_min: 'hrMin',
	hr_avg: 'hrAvg',
	hr_max: 'hrMax',
	health_score: 'healthScore',
	created_at: 'createdAt',
	updated_at: 'updatedAt'
}

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

/**
 * 将单条 API 记录(snake_case)转为前端 camelCase 格式
 */
function mapRecord(record) {
	const result = {}
	for (const [key, value] of Object.entries(record)) {
		result[SNAKE_TO_CAMEL[key] || key] = value
	}
	// 补充 dayLabel
	if (result.date) {
		const d = new Date(result.date)
		result.dayLabel = WEEKDAYS[d.getDay()]
	}
	return result
}

/**
 * 封装 uni.request 为 Promise
 */
function request(endpoint, options = {}) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: API_BASE + endpoint,
			timeout: REQUEST_TIMEOUT,
			dataType: 'json',
			...options,
			success: (res) => {
				if (res.data && res.data.code === 200) {
					resolve(res.data.data)
				} else {
					reject(new Error((res.data && res.data.message) || '请求失败'))
				}
			},
			fail: (err) => {
				console.warn('[API] 请求失败:', err.errMsg || err)
				reject(err)
			}
		})
	})
}

// ───────────── 公开 API 方法 ─────────────

/**
 * 获取记录列表
 * @param {string} [startDate] - YYYY-MM-DD
 * @param {string} [endDate]   - YYYY-MM-DD
 * @returns {Promise<Array>} 已转 camelCase 的记录数组
 */
export function fetchRecords(startDate, endDate) {
	let url = '/records'
	const params = []
	if (startDate) params.push('start_date=' + startDate)
	if (endDate)   params.push('end_date=' + endDate)
	if (params.length) url += '?' + params.join('&')

	return request(url).then(data => {
		return (Array.isArray(data) ? data : []).map(mapRecord)
	})
}

/**
 * 获取单条记录
 */
export function fetchRecordById(id) {
	return request('/records/' + id).then(mapRecord)
}

/**
 * 新增记录
 */
export function createRecord(data) {
	return request('/records', {
		method: 'POST',
		data: data
	})
}

/**
 * 更新记录
 */
export function updateRecord(id, data) {
	return request('/records/' + id, {
		method: 'PUT',
		data: data
	})
}

/**
 * 删除记录
 */
export function deleteRecord(id) {
	return request('/records/' + id, {
		method: 'DELETE'
	})
}

/**
 * 生成模拟数据（调用后端接口）
 */
export function generateMockOnServer(days = 30) {
	return request('/mock/generate', {
		method: 'POST',
		data: { days }
	})
}

// ───────────── 智能加载（推荐给页面使用） ─────────────

/**
 * 智能加载健康数据：先尝试 API，失败则回退到本地 mock
 * @returns {Promise<{ source: 'api'|'mock', data: Array }>}
 */
export function loadHealthData() {
	return fetchRecords()
		.then(data => {
			console.log('[API] 数据加载成功，来源: 后端')
			return { source: 'api', data }
		})
		.catch(() => {
			console.warn('[API] 后端不可用，回退到本地 mock 数据')
			const data = generateMockData(60)
			return { source: 'mock', data }
		})
}
