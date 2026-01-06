import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface Job {
  id: string
  status: string
  input_file: string
  target_lang: string
  source_lang?: string
  progress_percent: number
  created_at?: string
  completed_at?: string
  processing_time_seconds?: number
}

export const useJobStore = defineStore('jobs', () => {
  const jobs = ref<Job[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeJobs = computed(() => 
    jobs.value.filter(j => ['queued', 'running', 'paused'].includes(j.status))
  )

  const completedJobs = computed(() => 
    jobs.value.filter(j => j.status === 'completed')
  )

  const failedJobs = computed(() => 
    jobs.value.filter(j => j.status === 'failed')
  )

  async function fetchJobs(status?: string) {
    loading.value = true
    error.value = null
    try {
      const params = status ? { status } : {}
      const response = await axios.get('/api/jobs', { params })
      jobs.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch jobs'
      console.error('Failed to fetch jobs', err)
    } finally {
      loading.value = false
    }
  }

  async function createJob(jobData: {
    input_file: string
    target_lang: string
    source_lang?: string
    priority?: number
  }) {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post('/api/jobs', jobData)
      await fetchJobs() // Refresh list
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create job'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function pauseJob(jobId: string) {
    try {
      await axios.patch(`/api/jobs/${jobId}/pause`)
      await fetchJobs()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to pause job'
      throw err
    }
  }

  async function resumeJob(jobId: string) {
    try {
      await axios.patch(`/api/jobs/${jobId}/resume`)
      await fetchJobs()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to resume job'
      throw err
    }
  }

  async function cancelJob(jobId: string) {
    try {
      await axios.delete(`/api/jobs/${jobId}`)
      await fetchJobs()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to cancel job'
      throw err
    }
  }

  async function getJob(jobId: string) {
    try {
      const response = await axios.get(`/api/jobs/${jobId}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch job'
      throw err
    }
  }

  return {
    jobs,
    loading,
    error,
    activeJobs,
    completedJobs,
    failedJobs,
    fetchJobs,
    createJob,
    pauseJob,
    resumeJob,
    cancelJob,
    getJob,
  }
})

