import axios from 'axios'

const api = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
    delete config.headers['content-type']
  }
  return config
})

api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const response = await axios.post('/api/token/refresh/', { refresh })
          const { access } = response.data
          localStorage.setItem('token', access)
          api.defaults.headers.common['Authorization'] = `Bearer ${access}`
          error.config.headers['Authorization'] = `Bearer ${access}`
          return api.request(error.config)
        } catch {
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
