import axios from 'axios'

export const api = axios.create({ baseURL: '' })

export const listApps = () => api.get('/api/apps').then(r => r.data)
export const createApp = body => api.post('/api/apps', body).then(r => r.data)
export const updateApp = (name, body) => api.patch(`/api/apps/${name}`, body).then(r => r.data)
export const deleteApp = name => api.delete(`/api/apps/${name}`).then(r => r.data)
export const throughput = () => api.get('/api/analytics/throughput').then(r => r.data)

export const logEvent = (apiKey, body) =>
  api.post('/api/log', body, { headers: { 'X-API-Key': apiKey } }).then(r => r.data)
export const listIssues = (app, params = {}) =>
  api.get('/api/issues', { params: { app, ...params } }).then(r => r.data)
export const getIssue = id => api.get(`/api/issues/${id}`).then(r => r.data)
export const updateIssue = (id, body) => api.patch(`/api/issues/${id}`, body).then(r => r.data)
export const deleteIssue = id => api.delete(`/api/issues/${id}`).then(r => r.data)
export const trend = (app, hours = 24) =>
  api.get('/api/analytics/trend', { params: { app, hours } }).then(r => r.data)
export const severity = (app, hours = 24) =>
  api.get('/api/analytics/severity', { params: { app, hours } }).then(r => r.data)
export const topIssues = (app, n = 5) =>
  api.get('/api/analytics/top-issues', { params: { app, n } }).then(r => r.data)
