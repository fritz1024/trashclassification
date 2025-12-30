import request from '../utils/request.js'

/**
 * 单张图片识别
 */
export function predictSingle(filePath) {
  return request.upload('/predict/single', filePath, 'file')
}

/**
 * 批量图片识别
 */
export function predictBatch(filePaths) {
  // 小程序不支持多文件上传，需要逐个调用单张识别接口
  const promises = filePaths.map(filePath => {
    return request.upload('/predict/single', filePath, 'file')
  })
  return Promise.all(promises)
}

/**
 * 获取识别历史
 */
export function getHistory(params) {
  return request.get('/predict/history', params)
}

/**
 * 删除识别记录
 */
export function deleteRecord(id) {
  return request.request({
    url: `/predict/${id}`,
    method: 'DELETE'
  })
}
