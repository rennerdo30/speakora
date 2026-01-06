import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface SystemStatus {
  device: any
  gpu_memory: any
  cpu: {
    percent: number
    count: number
  }
  memory: {
    total_mb: number
    available_mb: number
    used_mb: number
    percent: number
  }
  queue: {
    total: number
    queued: number
    running: number
    paused: number
    completed: number
    failed: number
  }
}

export interface SystemStats {
  total_jobs: number
  completion_rate: number
  average_processing_time: number
  total_processing_time: number
  completed_count: number
  failed_count: number
  by_status: Record<string, number>
  by_language: Record<string, number>
}

export const useSystemStore = defineStore('system', () => {
  const status = ref<SystemStatus | null>(null)
  const stats = ref<SystemStats | null>(null)
  const info = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus() {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get('/api/system/status')
      status.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch system status'
      console.error('Failed to fetch system status', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get('/api/stats')
      stats.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch stats'
      console.error('Failed to fetch stats', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchInfo() {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get('/api/system/info')
      info.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch system info'
      console.error('Failed to fetch system info', err)
    } finally {
      loading.value = false
    }
  }

  return {
    status,
    stats,
    info,
    loading,
    error,
    fetchStatus,
    fetchStats,
    fetchInfo,
  }
})

