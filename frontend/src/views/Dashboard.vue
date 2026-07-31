<script setup lang="ts">
import { computed, ref, onMounted, watch, onUnmounted } from 'vue'
import { useJobStore, type Job } from '../stores/jobStore'
import { useSystemStore } from '../stores/systemStore'
import {
  Plus,
  Play,
  Pause,
  X,
  RefreshCw,
  Cpu,
  Activity,
  Clock,
  ExternalLink,
  Inbox,
  AlertTriangle
} from 'lucide-vue-next'
import NewJobModal from '../components/NewJobModal.vue'
import JobDetails from '../components/JobDetails.vue'
import SystemMonitor from '../components/SystemMonitor.vue'
import { JobWebSocket } from '../utils/websocket'
import {
  ACTIVE_JOB_STATUSES,
  JOB_LIST_POLL_MS,
  SKELETON_ROW_COUNT,
  TERMINAL_JOB_STATUSES
} from '../constants'
import { fileNameOf, formatCount, formatPercent } from '../utils/format'

const jobStore = useJobStore()
const systemStore = useSystemStore()

const showNewJobModal = ref(false)
const selectedJobId = ref<string | null>(null)
const showDetailsModal = ref(false)
const activeWebSockets = ref<Map<string, JobWebSocket>>(new Map())
let pollTimer: ReturnType<typeof setInterval> | undefined

/** True only for the very first load, when there is nothing to show yet. */
const isInitialLoad = computed(() => jobStore.loading && jobStore.jobs.length === 0)

const openDetails = (id: string) => {
  selectedJobId.value = id
  showDetailsModal.value = true
}

const cancelJob = async (job: Job) => {
  const name = fileNameOf(job.input_file)
  if (!confirm(`Cancel the translation of "${name}"?`)) return

  try {
    await jobStore.cancelJob(job.id)
    activeWebSockets.value.get(job.id)?.disconnect()
    activeWebSockets.value.delete(job.id)
  } catch (err) {
    console.error('Failed to cancel job', err)
  }
}

const toggleJobStatus = async (job: Job) => {
  try {
    if (job.status === 'paused') {
      await jobStore.resumeJob(job.id)
    } else {
      await jobStore.pauseJob(job.id)
    }
  } catch (err) {
    console.error('Failed to toggle job status', err)
  }
}

const setupJobWebSocket = (jobId: string) => {
  if (activeWebSockets.value.has(jobId)) return

  const job = jobStore.jobs.find((candidate) => candidate.id === jobId)
  if (!job || TERMINAL_JOB_STATUSES.includes(job.status as never)) return

  const ws = new JobWebSocket(jobId)

  ws.on('progress', (data) => {
    const target = jobStore.jobs.find((candidate) => candidate.id === jobId)
    if (target) {
      target.progress_percent = data.progress_percent || 0
      target.status = data.status || target.status
    }
  })

  ws.on('status', (data) => {
    if (data.final) {
      jobStore.fetchJobs()
      ws.disconnect()
      activeWebSockets.value.delete(jobId)
    }
  })

  ws.connect()
  activeWebSockets.value.set(jobId, ws)
}

watch(
  () => jobStore.jobs,
  (jobs) => {
    jobs.forEach((job) => {
      if (ACTIVE_JOB_STATUSES.includes(job.status as never)) setupJobWebSocket(job.id)
    })
  },
  { immediate: true }
)

onMounted(() => {
  jobStore.fetchJobs()
  systemStore.fetchInfo()
  pollTimer = setInterval(() => jobStore.fetchJobs(), JOB_LIST_POLL_MS)
})

onUnmounted(() => {
  clearInterval(pollTimer)
  activeWebSockets.value.forEach((ws) => ws.disconnect())
  activeWebSockets.value.clear()
})

const activeDevice = computed(
  () => systemStore.info?.available_devices?.[0]?.toUpperCase() || 'CPU'
)

const isPausable = (status: string) => ACTIVE_JOB_STATUSES.includes(status as never)
</script>

<template>
  <div class="dashboard fade-in">
    <header class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p class="page-subtitle">Overview of your translation jobs</p>
      </div>
      <button
        type="button"
        class="btn btn-primary"
        aria-haspopup="dialog"
        @click="showNewJobModal = true"
      >
        <Plus :size="18" aria-hidden="true" />
        New translation
      </button>
    </header>

    <SystemMonitor />

    <ul class="stats-grid">
      <li class="stat-card glass-card">
        <span class="stat-icon is-primary"><Cpu :size="22" aria-hidden="true" /></span>
        <span class="stat-info">
          <span class="stat-label">Device</span>
          <span class="stat-value">{{ activeDevice }}</span>
        </span>
      </li>
      <li class="stat-card glass-card">
        <span class="stat-icon is-secondary"><Activity :size="22" aria-hidden="true" /></span>
        <span class="stat-info">
          <span class="stat-label">Active jobs</span>
          <span class="stat-value">{{ formatCount(jobStore.activeJobs.length) }}</span>
        </span>
      </li>
      <li class="stat-card glass-card">
        <span class="stat-icon is-success"><Clock :size="22" aria-hidden="true" /></span>
        <span class="stat-info">
          <span class="stat-label">Total jobs</span>
          <span class="stat-value">{{ formatCount(jobStore.jobs.length) }}</span>
        </span>
      </li>
    </ul>

    <section class="section glass-card" aria-labelledby="recent-jobs-heading">
      <div class="section-header">
        <h2 id="recent-jobs-heading">Recent jobs</h2>
        <button
          type="button"
          class="btn btn-secondary btn-sm"
          :disabled="jobStore.loading"
          @click="jobStore.fetchJobs()"
        >
          <RefreshCw :size="14" :class="{ spin: jobStore.loading }" aria-hidden="true" />
          Refresh
        </button>
      </div>

      <p v-if="jobStore.error" class="alert alert-danger" role="alert">
        <AlertTriangle :size="18" aria-hidden="true" />
        <span>{{ jobStore.error }}</span>
      </p>

      <!-- First load: placeholder rows keep the layout stable. -->
      <div v-if="isInitialLoad" class="skeleton-rows">
        <div
          v-for="row in SKELETON_ROW_COUNT"
          :key="row"
          class="skeleton skeleton-row"
          aria-hidden="true"
        ></div>
        <p class="sr-only" role="status">Loading jobs…</p>
      </div>

      <div v-else-if="jobStore.jobs.length === 0" class="empty-state">
        <span class="empty-state-icon"><Inbox :size="22" aria-hidden="true" /></span>
        <p class="empty-state-title">No translation jobs yet</p>
        <p class="empty-state-body">
          Queue your first file and its progress, logs and output will appear here.
        </p>
        <button
          type="button"
          class="btn btn-primary"
          aria-haspopup="dialog"
          @click="showNewJobModal = true"
        >
          <Plus :size="18" aria-hidden="true" />
          New translation
        </button>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <caption class="sr-only">
            Recent translation jobs, newest first
          </caption>
          <thead>
            <tr>
              <th scope="col">Status</th>
              <th scope="col">Input file</th>
              <th scope="col">Language</th>
              <th scope="col">Progress</th>
              <th scope="col"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in jobStore.jobs" :key="job.id">
              <td data-label="Status">
                <span :class="`badge badge-${job.status.toLowerCase()}`">{{ job.status }}</span>
              </td>
              <td data-label="File" class="file-cell">
                <span :title="job.input_file">{{ fileNameOf(job.input_file) }}</span>
              </td>
              <td data-label="Language">{{ job.target_lang.toUpperCase() }}</td>
              <td data-label="Progress">
                <div class="progress">
                  <div
                    class="meter"
                    role="progressbar"
                    :aria-valuenow="Math.round(job.progress_percent)"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    :aria-label="`Progress for ${fileNameOf(job.input_file)}`"
                  >
                    <div class="meter-fill" :style="{ width: `${job.progress_percent}%` }"></div>
                  </div>
                  <span class="progress-value">{{ formatPercent(job.progress_percent) }}</span>
                </div>
              </td>
              <td class="actions-cell is-stacked-full">
                <button
                  v-if="isPausable(job.status)"
                  type="button"
                  class="icon-btn"
                  :aria-label="job.status === 'paused' ? 'Resume job' : 'Pause job'"
                  :title="job.status === 'paused' ? 'Resume' : 'Pause'"
                  @click="toggleJobStatus(job)"
                >
                  <Pause v-if="job.status === 'running'" :size="16" aria-hidden="true" />
                  <Play v-else :size="16" aria-hidden="true" />
                </button>
                <button
                  type="button"
                  class="icon-btn"
                  aria-label="View job details"
                  title="View details"
                  aria-haspopup="dialog"
                  @click="openDetails(job.id)"
                >
                  <ExternalLink :size="16" aria-hidden="true" />
                </button>
                <button
                  type="button"
                  class="icon-btn is-danger"
                  aria-label="Cancel job"
                  title="Cancel"
                  @click="cancelJob(job)"
                >
                  <X :size="16" aria-hidden="true" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <NewJobModal
      :show="showNewJobModal"
      @close="showNewJobModal = false"
      @submitted="jobStore.fetchJobs()"
    />

    <JobDetails
      :show="showDetailsModal"
      :jobId="selectedJobId"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.page-subtitle {
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-md);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr));
  gap: var(--space-4);
  list-style: none;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  transition: border-color var(--duration-fast) var(--ease-out),
    box-shadow var(--duration-fast) var(--ease-out);
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
  border-radius: var(--radius-lg);
}

.stat-icon.is-primary {
  background: var(--primary-soft);
  color: var(--primary-color);
}

.stat-icon.is-secondary {
  background: var(--secondary-soft);
  color: var(--secondary-color);
}

.stat-icon.is-success {
  background: var(--success-soft);
  color: var(--success-color);
}

.stat-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.stat-value {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
}

.section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.section-header h2 {
  font-size: var(--text-xl);
}

.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-inline: calc(var(--space-6) * -1);
  padding-inline: var(--space-6);
}

.data-table {
  min-width: 40rem;
}

.file-cell span {
  display: block;
  max-width: 18rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 8rem;
}

.progress .meter {
  width: 7rem;
}

.progress-value {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-variant-numeric: tabular-nums;
}

.actions-cell {
  display: flex;
  gap: var(--space-2);
}

.skeleton-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-block: var(--space-2);
}

.skeleton-row {
  height: 2.75rem;
}

@media (max-width: 640px) {
  .section {
    padding: var(--space-4);
  }

  .table-container {
    margin-inline: calc(var(--space-4) * -1);
    padding-inline: 0;
    overflow-x: visible;
  }

  .data-table {
    min-width: 0;
  }

  .file-cell span {
    max-width: none;
  }
}
</style>
