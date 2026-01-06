<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useJobStore } from '../stores/jobStore'
import { useSystemStore } from '../stores/systemStore'
import { Plus, Play, Pause, X, RefreshCw, Cpu, Activity, Clock, Trash2, ExternalLink } from 'lucide-vue-next'
import NewJobModal from '../components/NewJobModal.vue'
import JobDetails from '../components/JobDetails.vue'
import DownloadModelModal from '../components/DownloadModelModal.vue'
import SystemMonitor from '../components/SystemMonitor.vue'
import { JobWebSocket } from '../utils/websocket'

const jobStore = useJobStore()
const systemStore = useSystemStore()

const showNewJobModal = ref(false)
const showDownloadModal = ref(false)
const selectedJobId = ref<string | null>(null)
const showDetailsModal = ref(false)
const detailsRef = ref<any>(null)
const activeWebSockets = ref<Map<string, JobWebSocket>>(new Map())

const openDetails = (id: string) => {
  selectedJobId.value = id
  showDetailsModal.value = true
}

watch(showDetailsModal, (newVal) => {
  if (newVal && detailsRef.value) {
    detailsRef.value.fetchJobDetails()
  }
})

const cancelJob = async (id: string) => {
  if (confirm('Are you sure you want to cancel this job?')) {
    try {
      await jobStore.cancelJob(id)
      // Disconnect WebSocket if exists
      const ws = activeWebSockets.value.get(id)
      if (ws) {
        ws.disconnect()
        activeWebSockets.value.delete(id)
      }
    } catch (err) {
      console.error('Failed to cancel job', err)
    }
  }
}

const toggleJobStatus = async (job: any) => {
  try {
    if (job.status === 'paused') {
      await jobStore.resumeJob(job.id)
    } else {
      await jobStore.pauseJob(job.id)
    }
  } catch (err) {
    console.error(`Failed to toggle job status`, err)
  }
}

const setupJobWebSocket = (jobId: string) => {
  // Don't setup if already exists or job is completed/failed
  if (activeWebSockets.value.has(jobId)) return
  
  const job = jobStore.jobs.find(j => j.id === jobId)
  if (!job || ['completed', 'failed'].includes(job.status)) return
  
  const ws = new JobWebSocket(jobId)
  ws.on('progress', (data) => {
    // Update job progress in store
    const job = jobStore.jobs.find(j => j.id === jobId)
    if (job) {
      job.progress_percent = data.progress_percent || 0
      job.status = data.status || job.status
    }
  })
  
  ws.on('status', (data) => {
    if (data.final) {
      // Job completed, refresh list and disconnect
      jobStore.fetchJobs()
      ws.disconnect()
      activeWebSockets.value.delete(jobId)
    }
  })
  
  ws.connect()
  activeWebSockets.value.set(jobId, ws)
}

onMounted(() => {
  jobStore.fetchJobs()
  systemStore.fetchInfo()
  
  // Refresh jobs every 3 seconds
  const interval = setInterval(() => {
    jobStore.fetchJobs()
  }, 3000)
  
  // Setup WebSockets for active jobs
  watch(() => jobStore.jobs, (jobs) => {
    jobs.forEach(job => {
      if (['queued', 'running', 'paused'].includes(job.status)) {
        setupJobWebSocket(job.id)
      }
    })
  }, { immediate: true })
  
  onUnmounted(() => {
    clearInterval(interval)
    // Cleanup all WebSockets
    activeWebSockets.value.forEach(ws => ws.disconnect())
    activeWebSockets.value.clear()
  })
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

    <SystemMonitor />
    
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon cpu"><Cpu :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Device</span>
          <span class="stat-value">{{ systemStore.info?.available_devices?.[0]?.toUpperCase() || 'CPU' }}</span>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon activity"><Activity :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Active Jobs</span>
          <span class="stat-value">{{ jobStore.activeJobs.length }}</span>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon clock"><Clock :size="24" /></div>
        <div class="stat-info">
          <span class="stat-label">Total Jobs</span>
          <span class="stat-value">{{ jobStore.jobs.length }}</span>
        </div>
      </div>
    </div>

    <div class="section glass-card">
      <div class="section-header">
        <h2>Recent Jobs</h2>
        <button class="btn btn-secondary btn-sm" @click="jobStore.fetchJobs()">
          <RefreshCw :size="14" :class="{ 'spin': jobStore.loading }" />
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
            <tr v-for="job in jobStore.jobs" :key="job.id">
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
            <tr v-if="jobStore.jobs.length === 0">
              <td colspan="5" class="empty-state">No jobs found. Start a new translation to see it here.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <NewJobModal 
      :show="showNewJobModal" 
      @close="showNewJobModal = false"
      @submitted="jobStore.fetchJobs()"
    />

    <JobDetails
      ref="detailsRef"
      :show="showDetailsModal"
      :jobId="selectedJobId"
      @close="showDetailsModal = false"
    />

    <DownloadModelModal
      :show="showDownloadModal"
      @close="showDownloadModal = false"
    />
  </div>
</template>

<style scoped>
.dashboard { padding: 10px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; flex-wrap: wrap; gap: 16px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 32px; }
.stat-card { padding: 24px; display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon.cpu { background: rgba(59, 130, 246, 0.1); color: var(--primary-color); }
.stat-icon.activity { background: rgba(139, 92, 246, 0.1); color: var(--secondary-color); }
.stat-icon.clock { background: rgba(16, 185, 129, 0.1); color: var(--accent-color); }
.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.8125rem; color: var(--text-muted); }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); }
.section { padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.table-container { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; min-width: 600px; }
th { text-align: left; padding: 12px 16px; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color); }
td { padding: 16px; border-bottom: 1px solid var(--border-color); font-size: 0.875rem; }
.file-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.progress-bar-container { width: 120px; height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; position: relative; }
.progress-bar { height: 100%; background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); border-radius: 4px; }
.progress-text { position: absolute; right: -35px; top: -4px; font-size: 0.75rem; color: var(--text-secondary); }
.actions-cell { display: flex; gap: 8px; flex-wrap: wrap; }
.action-btn { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; }
.action-btn:hover { background: var(--surface-hover); color: var(--text-primary); border-color: var(--text-muted); }
.action-btn.delete:hover { background: rgba(239, 68, 68, 0.1); color: #f87171; border-color: rgba(239, 68, 68, 0.2); }
.empty-state { text-align: center; color: var(--text-muted); padding: 40px !important; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .dashboard { padding: 8px; }
  .header { margin-bottom: 24px; }
  .header h1 { font-size: 1.5rem; }
  .stats-grid { grid-template-columns: 1fr; gap: 12px; margin-bottom: 24px; }
  .stat-card { padding: 16px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-value { font-size: 1.125rem; }
  .section { padding: 16px; }
  .section-header h2 { font-size: 1.125rem; }
  th, td { padding: 10px 12px; font-size: 0.8125rem; }
  .progress-bar-container { width: 80px; }
  .progress-text { right: -30px; font-size: 0.6875rem; }
  .action-btn { width: 28px; height: 28px; }
}

@media (max-width: 480px) {
  .dashboard { padding: 6px; }
  .header { margin-bottom: 16px; }
  .header h1 { font-size: 1.25rem; }
  .header p { font-size: 0.8125rem; }
  .stats-grid { gap: 8px; }
  .stat-card { padding: 12px; gap: 12px; }
  .stat-icon { width: 36px; height: 36px; }
  .stat-label { font-size: 0.75rem; }
  .stat-value { font-size: 1rem; }
  .section { padding: 12px; }
  .section-header { margin-bottom: 12px; }
  .section-header h2 { font-size: 1rem; }
  table { min-width: 500px; }
  th, td { padding: 8px; font-size: 0.75rem; }
  .file-cell { max-width: 120px; }
  .progress-bar-container { width: 60px; }
  .progress-text { right: -25px; font-size: 0.625rem; }
  .actions-cell { gap: 4px; }
  .action-btn { width: 24px; height: 24px; }
  .empty-state { padding: 24px !important; font-size: 0.8125rem; }
}
</style>
