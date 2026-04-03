import request from '@/utils/request'

export const getAnnouncements = (params) => {
  return request.get('/announcements/list', { params })
}

export const getAnnouncement = (id) => {
  return request.get(`/announcements/${id}`)
}

export const createAnnouncement = (data) => {
  return request.post('/announcements/create', data)
}

export const updateAnnouncement = (id, data) => {
  return request.put(`/announcements/update/${id}`, data)
}

export const deleteAnnouncement = (id) => {
  return request.delete(`/announcements/delete/${id}`)
}
