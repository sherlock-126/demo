import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Script endpoints
  generateScript: async (data: any) => {
    const response = await apiClient.post('/api/v1/scripts/generate', data)
    return response.data
  },

  getScript: async (scriptId: string) => {
    const response = await apiClient.get(`/api/v1/scripts/${scriptId}`)
    return response.data
  },

  listScripts: async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/api/v1/scripts/', {
      params: { skip, limit }
    })
    return response.data
  },

  // Image endpoints
  generateImages: async (scriptId: string) => {
    const response = await apiClient.post('/api/v1/images/generate', {
      script_id: scriptId
    })
    return response.data
  },

  getImageStatus: async (taskId: string) => {
    const response = await apiClient.get(`/api/v1/images/status/${taskId}`)
    return response.data
  },

  // Video endpoints
  createVideo: async (data: any) => {
    const response = await apiClient.post('/api/v1/videos/create', data)
    return response.data
  },

  getVideoStatus: async (videoId: string) => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}/status`)
    return response.data
  },

  listVideos: async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/api/v1/videos/', {
      params: { skip, limit }
    })
    return response.data
  },
}