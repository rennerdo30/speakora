<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { X, Clock, FileAudio, Globe, AlertCircle, Terminal } from 'lucide-vue-next'

const props = defineProps<{
  show: boolean
  jobId: string | null
}>()

const emit = defineEmits(['close'])

const job = ref<any>(null)
const logs = ref('')
const loading = ref(false)

const fetchJobDetails = async () => {
  if (!props.jobId) return
  loading.value = true
  try {
    const res = await axios.get(`/api/jobs/${props.jobId}`)
    job.value = res.data
    
    const logRes = await axios.get(`/api/jobs/${props.jobId}/logs`)
    logs.value = logRes.data.logs
  } catch (err) {
    console.error('Failed to fetch job details', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.show) fetchJobDetails()
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
        </div>

        <div class="logs-section">
          <h3><Terminal :size="16" /> Processing Logs</h3>
          <div class="logs-container">
            <pre>{{ logs || 'No logs available for this job yet.' }}</pre>
          </div>
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
</style>
