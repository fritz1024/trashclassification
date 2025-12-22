import request from '@/utils/request'

// 单张图片识别
export const predictSingle = (formData) => {
  return request.post('/predict/single', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 批量图片识别
export const predictBatch = (formData) => {
  return request.post('/predict/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取识别历史
export const getPredictionHistory = (params) => {
  return request.get('/predict/history', { params })
}

// 删除识别记录
export const deletePrediction = (id) => {
  return request.delete(`/predict/${id}`)
}

// 提交识别反馈
export const submitFeedback = (data) => {
  return request.post('/predict/feedback', data)
}
