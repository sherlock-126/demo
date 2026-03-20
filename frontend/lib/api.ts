import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  async generateScript(data: {
    topic: string
    num_slides: number
    language: string
  }) {
    const response = await api.post('/scripts/generate', data)
    return response.data
  },

  async getScript(scriptId: string) {
    const response = await api.get(`/scripts/${scriptId}`)
    return response.data
  },

  async generateImages(data: { script_id: string }) {
    const response = await api.post('/images/generate', data)
    return response.data
  },

  async getImageStatus(taskId: string) {
    const response = await api.get(`/images/${taskId}/status`)
    return response.data
  },

  async createVideo(data: {
    image_paths: string[]
    music_path?: string
    duration_per_slide: number
    transition_duration: number
  }) {
    const response = await api.post('/videos/create', data)
    return response.data
  },

  async getVideoStatus(taskId: string) {
    const response = await api.get(`/videos/${taskId}/status`)
    return response.data
  },
}

export default api