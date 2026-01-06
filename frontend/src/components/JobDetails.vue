<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useJobStore } from '../stores/jobStore'
import { X, Clock, FileAudio, Globe, AlertCircle, History, Timer } from 'lucide-vue-next'
import LogViewer from './LogViewer.vue'

const props = defineProps<{
  show: boolean
  jobId: string | null
}>()

const emit = defineEmits(['close'])

const jobStore = useJobStore()
const job = ref<any>(null)
const checkpoints = ref<any[]>([])
const loading = ref(false)

const fetchJobDetails = async () => {
  if (!props.jobId) return
  loading.value = true
  try {
    job.value = await jobStore.getJob(props.jobId)
    
    // Fetch checkpoints
    try {
      const response = await fetch(`/api/jobs/${props.jobId}/checkpoints`)
      if (response.ok) {
        const data = await response.json()
        checkpoints.value = data.checkpoints || []
      }
    } catch (err) {
      console.error('Failed to fetch checkpoints', err)
    }
  } catch (err) {
    console.error('Failed to fetch job details', err)
  } finally {
    loading.value = false
  }
}

const calculateEstimatedTime = () => {
  if (!job.value || !job.value.progress_percent || job.value.progress_percent === 0) {
    return null
  }
  
  if (job.value.processing_time_seconds && job.value.progress_percent > 0) {
    const elapsed = job.value.processing_time_seconds
    const progress = job.value.progress_percent / 100
    const totalEstimated = elapsed / progress
    const remaining = totalEstimated - elapsed
    return Math.max(0, Math.round(remaining))
  }
  
  return null
}

const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

watch(() => props.show, (newVal) => {
  if (newVal && props.jobId) {
    fetchJobDetails()
  }
})

onMounted(() => {
  if (props.show && props.jobId) {
    fetchJobDetails()
  }
})

defineExpose({ fetchJobDetails })
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content glass-card fade-in">
      <div class="modal-header">
        <div class="header-title">
          <h2>Job Details</h2>
          <span class="job-id">{{ jobId }}</span>
        </div>
        <button class="close-btn" @click="emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="modal-body" v-if="job">
        <div class="details-grid">
          <div class="detail-item">
            <span class="label"><FileAudio :size="14" /> Input File</span>
            <span class="value">{{ job.input_file }}</span>
          </div>
          <div class="detail-item">
            <span class="label"><Globe :size="14" /> Target Lang</span>
            <span class="value">{{ job.target_lang.toUpperCase() }}</span>
          </div>
          <div class="detail-item">
            <span class="label"><AlertCircle :size="14" /> Status</span>
            <span :class="'badge badge-' + job.status.toLowerCase()">{{ job.status }}</span>
          </div>
          <div class="detail-item">
            <span class="label"><Clock :size="14" /> Created</span>
            <span class="value">{{ new Date(job.created_at).toLocaleString() }}</span>
          </div>
          <div v-if="job.processing_time_seconds" class="detail-item">
            <span class="label"><Timer :size="14" /> Processing Time</span>
            <span class="value">{{ formatDuration(Math.round(job.processing_time_seconds)) }}</span>
          </div>
          <div v-if="calculateEstimatedTime() !== null" class="detail-item">
            <span class="label"><Timer :size="14" /> Est. Remaining</span>
            <span class="value">{{ formatDuration(calculateEstimatedTime()!) }}</span>
          </div>
        </div>

        <!-- Checkpoint History -->
        <div v-if="checkpoints.length > 0" class="checkpoints-section">
          <h3><History :size="16" /> Checkpoint History</h3>
          <div class="checkpoints-list">
            <div v-for="cp in checkpoints" :key="cp.id" class="checkpoint-item">
              <div class="checkpoint-time">{{ new Date(cp.created_at).toLocaleString() }}</div>
              <div class="checkpoint-info">
                <span>Audio Position: {{ cp.audio_position }} bytes</span>
                <span v-if="cp.last_successful_frame">Frame: {{ cp.last_successful_frame }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="logs-section">
          <LogViewer :jobId="jobId" :autoRefresh="true" />
        </div>
      </div>
      
      <div v-else-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading details...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.modal-content {
  width: 700px;
  max-width: 95vw;
  max-height: 85vh;
  padding: 32px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.job-id {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;
}

.checkpoints-section {
  margin-bottom: 32px;
}

.checkpoints-section h3 {
  font-size: 1rem;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkpoints-list {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.checkpoint-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.checkpoint-item:last-child {
  border-bottom: none;
}

.checkpoint-time {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.checkpoint-info {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item .value {
  font-size: 0.9375rem;
  color: var(--text-primary);
  word-break: break-all;
}

.logs-section h3 {
  font-size: 1rem;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logs-container {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.logs-container pre {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8125rem;
  color: #a78bfa;
  white-space: pre-wrap;
  line-height: 1.4;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(59, 130, 246, 0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .modal-content {
    width: 90vw;
    padding: 24px;
    max-height: 90vh;
  }
  
  .modal-header {
    margin-bottom: 20px;
  }
  
  .modal-header h2 {
    font-size: 1.25rem;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .logs-container {
    max-height: 250px;
  }
}

@media (max-width: 480px) {
  .modal-content {
    width: 95vw;
    padding: 16px;
    max-height: 95vh;
  }
  
  .modal-header h2 {
    font-size: 1.125rem;
  }
  
  .job-id {
    font-size: 0.6875rem;
  }
  
  .detail-item .label {
    font-size: 0.6875rem;
  }
  
  .detail-item .value {
    font-size: 0.875rem;
  }
  
  .logs-section h3 {
    font-size: 0.9375rem;
  }
  
  .logs-container {
    padding: 12px;
    max-height: 200px;
  }
  
  .logs-container pre {
    font-size: 0.75rem;
  }
}
</style>
