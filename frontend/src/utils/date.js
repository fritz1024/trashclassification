/**
 * 时间格式化工具函数
 */

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期字符串或Date对象
 * @param {string} format - 格式化模板，默认 'yyyy-MM-dd HH:mm:ss'
 * @returns {string} 格式化后的日期时间字符串
 *
 * 注意：当传入UTC时间字符串时，会自动转换为用户本地时区时间
 */
export function formatDateTime(date, format = 'yyyy-MM-dd HH:mm:ss') {
  if (!date) return ''

  // 如果是字符串且不包含时区信息，添加Z表示UTC时间
  let dateStr = date
  if (typeof date === 'string' && !date.includes('Z') && !date.includes('+') && !date.includes('-', 10)) {
    // 如果时间字符串包含T但没有时区标识，添加Z
    if (date.includes('T')) {
      dateStr = date + 'Z'
    }
  }

  const d = new Date(dateStr)

  // 检查日期是否有效
  if (isNaN(d.getTime())) return ''

  // 使用本地时间的各个部分（JavaScript会自动转换UTC到本地时区）
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('yyyy', year)
    .replace('MM', month)
    .replace('dd', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期（不含时间）
 * @param {string|Date} date - 日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date) {
  return formatDateTime(date, 'yyyy-MM-dd')
}

/**
 * 格式化时间（不含日期）
 * @param {string|Date} date - 日期字符串或Date对象
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(date) {
  return formatDateTime(date, 'HH:mm:ss')
}
