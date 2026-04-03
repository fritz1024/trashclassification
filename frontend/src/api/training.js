import request from '@/utils/request'

// 数据集管理
export const createDatasetFromHistory = (name, minImagesPerClass = 10) => {
  return request.post('/admin/training/datasets/from-history', null, {
    params: { name, min_images_per_class: minImagesPerClass }
  })
}

export const getDatasets = (params) => {
  return request.get('/admin/training/datasets', { params })
}

export const getDatasetDetail = (id) => {
  return request.get(`/admin/training/datasets/${id}/detail`)
}

export const deleteDataset = (id) => {
  return request.delete(`/admin/training/datasets/${id}`)
}

// 训练任务管理
export const createTrainingJob = (data) => {
  return request.post('/admin/training/jobs', null, {
    params: data
  })
}

export const getTrainingJobs = (params) => {
  return request.get('/admin/training/jobs', { params })
}

export const getTrainingJob = (id) => {
  return request.get(`/admin/training/jobs/${id}`)
}

export const startTraining = (id) => {
  return request.post(`/admin/training/jobs/${id}/start`)
}

export const cancelTraining = (id) => {
  return request.post(`/admin/training/jobs/${id}/cancel`)
}

export const deleteTrainingJob = (id) => {
  return request.delete(`/admin/training/jobs/${id}`)
}
