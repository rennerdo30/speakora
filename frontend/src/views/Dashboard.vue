import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { Plus, Play, Pause, X, RefreshCw, Cpu, Activity, Clock, Trash2, ExternalLink } from 'lucide-vue-next'
import NewJobModal from '../components/NewJobModal.vue'
import JobDetails from '../components/JobDetails.vue'

interface Job {
  id: string
  status: string
  input_file: string
  target_lang: string
  progress_percent: number
}

const jobs = ref<Job[]>([])
const loading = ref(true)
const systemInfo = ref<any>(null)
const showNewJobModal = ref(false)
const selectedJobId = ref<string | null>(null)
const showDetailsModal = ref(false)
const detailsRef = ref<any>(null)

const openDetails = (id: string) => {
  selectedJobId.value = id
  showDetailsModal.value = true
}

watch(showDetailsModal, (newVal) => {
  if (newVal && detailsRef.value) {
    detailsRef.value.fetchJobDetails()
  }
})

const fetchJobs = async () => {
  try {
    const res = await axios.get('/api/jobs')
    jobs.value = res.data
  } catch (err) {
    console.error('Failed to fetch jobs', err)
  } finally {
    loading.value = false
  }
}

const fetchSystemInfo = async () => {
  try {
    const res = await axios.get('/api/system/info')
    systemInfo.value = res.data
  } catch (err) {
    console.error('Failed to fetch system info', err)
  }
}

const cancelJob = async (id: string) => {
  if (confirm('Are you sure you want to cancel this job?')) {
    try {
      await axios.delete(`/api/jobs/${id}`)
      fetchJobs()
    } catch (err) {
      console.error('Failed to cancel job', err)
    }
  }
}

const toggleJobStatus = async (job: Job) => {
  const action = job.status === 'paused' ? 'resume' : 'pause'
  try {
    await axios.patch(`/api/jobs/${job.id}/${action}`)
    fetchJobs()
  } catch (err) {
    console.error(`Failed to ${action} job`, err)
  }
}

onMounted(() => {
  fetchJobs()
  fetchSystemInfo()
  const interval = setInterval(fetchJobs, 3000)
  return () => clearInterval(interval)
})

const getStatusBadgeClass = (status: string) => {
  return `badge badge-${status.toLowerCase()}`
}
</script>

<template>
  <div class="dashboard fade-in">
    <header class="header">
      <div class="header-content">
        <h1>Dashboard</h1>
        <p class="text-secondary">Overview of your translation jobs</p>
      </div>
      <button class="btn btn-primary" @click="showNewJobModal = true">
        <Plus :size="18" />
        New Translation
      </button>
    </header>

    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon cpu"><Cpu :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Device</span>
          <span class="stat-value">{{ systemInfo?.available_devices?.[0]?.toUpperCase() || 'CPU' }}</span>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon activity"><Activity :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Active Jobs</span>
          <span class="stat-value">{{ jobs.filter(j => j.status === 'running').length }}</span>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon clock"><Clock :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Total Jobs</span>
          <span class="stat-value">{{ jobs.length }}</span>
        </div>
      </div>
    </div>

    <div class="section glass-card">
      <div class="section-header">
        <h2>Recent Jobs</h2>
        <button class="btn btn-secondary btn-sm" @click="fetchJobs">
          <RefreshCw :size="14" :class="{ 'spin': loading }" />
          Refresh
        </button>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Input File</th>
              <th>Language</th>
              <th>Progress</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in jobs" :key="job.id">
              <td>
                <span :class="getStatusBadgeClass(job.status)">{{ job.status }}</span>
              </td>
              <td class="file-cell" :title="job.input_file">
                {{ job.input_file.split('/').pop() }}
              </td>
              <td>{{ job.target_lang.toUpperCase() }}</td>
              <td>
                <div class="progress-bar-container">
                  <div class="progress-bar" :style="{ width: job.progress_percent + '%' }"></div>
                  <span class="progress-text">{{ Math.round(job.progress_percent) }}%</span>
                </div>
              </td>
              <td class="actions-cell">
                <button 
                  v-if="job.status === 'running' || job.status === 'paused' || job.status === 'queued'" 
                  class="action-btn" 
                  :title="job.status === 'paused' ? 'Resume' : 'Pause'"
                  @click="toggleJobStatus(job)"
                >
                  <Pause v-if="job.status === 'running'" :size="16" />
                  <Play v-else :size="16" />
                </button>
                <button class="action-btn" title="View Details" @click="openDetails(job.id)">
                  <ExternalLink :size="16" />
                </button>
                <button class="action-btn delete" title="Cancel" @click="cancelJob(job.id)">
                  <X :size="16" />
                </button>
              </td>
            </tr>
            <tr v-if="jobs.length === 0">
              <td colspan="5" class="empty-state">No jobs found. Start a new translation to see it here.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <NewJobModal 
      :show="showNewJobModal" 
      @close="showNewJobModal = false"
      @submitted="fetchJobs"
    />

    <JobDetails
      ref="detailsRef"
      :show="showDetailsModal"
      :jobId="selectedJobId"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<style scoped>
/* Styles same as before ... */
.dashboard { padding: 10px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 32px; }
.stat-card { padding: 24px; display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-icon.cpu { background: rgba(59, 130, 246, 0.1); color: var(--primary-color); }
.stat-icon.activity { background: rgba(139, 92, 246, 0.1); color: var(--secondary-color); }
.stat-icon.clock { background: rgba(16, 185, 129, 0.1); color: var(--accent-color); }
.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.8125rem; color: var(--text-muted); }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); }
.section { padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px 16px; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color); }
td { padding: 16px; border-bottom: 1px solid var(--border-color); font-size: 0.875rem; }
.file-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.progress-bar-container { width: 120px; height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; position: relative; }
.progress-bar { height: 100%; background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); border-radius: 4px; }
.progress-text { position: absolute; right: -35px; top: -4px; font-size: 0.75rem; color: var(--text-secondary); }
.actions-cell { display: flex; gap: 8px; }
.action-btn { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; }
.action-btn:hover { background: var(--surface-hover); color: var(--text-primary); border-color: var(--text-muted); }
.action-btn.delete:hover { background: rgba(239, 68, 68, 0.1); color: #f87171; border-color: rgba(239, 68, 68, 0.2); }
.empty-state { text-align: center; color: var(--text-muted); padding: 40px !important; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }
</style>
