<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useJobStore } from '../stores/jobStore'
import { X, Clock, FileAudio, Globe, AlertCircle, History, Timer, AlertTriangle } from 'lucide-vue-next'
import LogViewer from './LogViewer.vue'
import { useDialog } from '../composables/useDialog'
import { formatCount, formatDateTime, formatDuration } from '../utils/format'

const props = defineProps<{
  show: boolean
  jobId: string | null
}>()

const emit = defineEmits(['close'])

const jobStore = useJobStore()
const job = ref<any>(null)
const checkpoints = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const { dialogRef } = useDialog(
  () => props.show,
  () => emit('close')
)

const fetchJobDetails = async () => {
  if (!props.jobId) return
  loading.value = true
  error.value = ''

  try {
    job.value = await jobStore.getJob(props.jobId)
  } catch (err) {
    console.error('Failed to fetch job details', err)
    error.value = 'Could not load the details for this job.'
    loading.value = false
    return
  }

  try {
    const response = await fetch(`/api/jobs/${props.jobId}/checkpoints`)
    if (response.ok) {
      const data = await response.json()
      checkpoints.value = data.checkpoints || []
    }
  } catch (err) {
    // Checkpoints are supplementary — the job details are still usable.
    console.error('Failed to fetch checkpoints', err)
  } finally {
    loading.value = false
  }
}

/** Remaining seconds, extrapolated from elapsed time and progress. */
const estimatedRemainingSeconds = computed<number | null>(() => {
  const progressPercent = job.value?.progress_percent
  const elapsed = job.value?.processing_time_seconds

  if (!progressPercent || progressPercent <= 0 || !elapsed) return null

  const total = elapsed / (progressPercent / 100)
  return Math.max(0, Math.round(total - elapsed))
})

watch(
  () => props.show,
  (isOpen) => {
    if (isOpen && props.jobId) fetchJobDetails()
  }
)

onMounted(() => {
  if (props.show && props.jobId) fetchJobDetails()
})

defineExpose({ fetchJobDetails })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="emit('close')">
        <div
          ref="dialogRef"
          class="modal-content glass-card"
          role="dialog"
          aria-modal="true"
          aria-labelledby="job-details-title"
          tabindex="-1"
        >
          <div class="modal-header">
            <div class="header-title">
              <h2 id="job-details-title">Job details</h2>
              <span class="job-id">{{ jobId }}</span>
            </div>
            <button
              type="button"
              class="icon-btn is-borderless"
              aria-label="Close dialog"
              data-autofocus
              @click="emit('close')"
            >
              <X :size="20" aria-hidden="true" />
            </button>
          </div>

          <p v-if="error" class="alert alert-danger" role="alert">
            <AlertTriangle :size="18" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>

          <div v-else-if="loading && !job" class="loading-state">
            <div class="spinner" aria-hidden="true"></div>
            <p role="status">Loading details…</p>
          </div>

          <div v-else-if="job" class="modal-body">
            <dl class="details-grid">
              <div class="detail-item">
                <dt><FileAudio :size="14" aria-hidden="true" /> Input file</dt>
                <dd class="is-path">{{ job.input_file }}</dd>
              </div>
              <div class="detail-item">
                <dt><Globe :size="14" aria-hidden="true" /> Target language</dt>
                <dd>{{ job.target_lang?.toUpperCase() }}</dd>
              </div>
              <div class="detail-item">
                <dt><AlertCircle :size="14" aria-hidden="true" /> Status</dt>
                <dd>
                  <span :class="`badge badge-${String(job.status).toLowerCase()}`">
                    {{ job.status }}
                  </span>
                </dd>
              </div>
              <div class="detail-item">
                <dt><Clock :size="14" aria-hidden="true" /> Created</dt>
                <dd>{{ formatDateTime(job.created_at) }}</dd>
              </div>
              <div v-if="job.processing_time_seconds" class="detail-item">
                <dt><Timer :size="14" aria-hidden="true" /> Processing time</dt>
                <dd>{{ formatDuration(job.processing_time_seconds) }}</dd>
              </div>
              <div v-if="estimatedRemainingSeconds !== null" class="detail-item">
                <dt><Timer :size="14" aria-hidden="true" /> Estimated remaining</dt>
                <dd>{{ formatDuration(estimatedRemainingSeconds) }}</dd>
              </div>
            </dl>

            <section v-if="checkpoints.length > 0" aria-labelledby="checkpoints-heading">
              <h3 id="checkpoints-heading">
                <History :size="16" aria-hidden="true" />
                Checkpoint history
              </h3>
              <ul class="checkpoints-list">
                <li v-for="checkpoint in checkpoints" :key="checkpoint.id" class="checkpoint-item">
                  <span class="checkpoint-time">{{ formatDateTime(checkpoint.created_at) }}</span>
                  <span class="checkpoint-info">
                    <span>Audio position: {{ formatCount(checkpoint.audio_position) }} bytes</span>
                    <span v-if="checkpoint.last_successful_frame">
                      Frame: {{ formatCount(checkpoint.last_successful_frame) }}
                    </span>
                  </span>
                </li>
              </ul>
            </section>

            <LogViewer :jobId="jobId" :autoRefresh="true" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--page-gutter);
  background: var(--overlay-backdrop);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  width: var(--modal-width-lg);
  max-width: 100%;
  max-height: calc(100vh - var(--page-gutter) * 2);
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-content:focus {
  outline: none;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

.modal-header h2 {
  font-size: var(--text-xl);
}

.job-id {
  display: block;
  margin-top: var(--space-1);
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  word-break: break-all;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
  gap: var(--space-5);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.detail-item dt {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.detail-item dd {
  font-size: var(--text-base);
  color: var(--text-primary);
}

.detail-item dd.is-path {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  word-break: break-all;
}

h3 {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.checkpoints-list {
  max-height: 12rem;
  overflow-y: auto;
  padding: var(--space-2) var(--space-4);
  background: var(--surface-raised);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  list-style: none;
}

.checkpoint-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-color);
}

.checkpoint-item:last-child {
  border-bottom: none;
}

.checkpoint-time {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.checkpoint-info {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-12);
  color: var(--text-muted);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--duration-base) var(--ease-out);
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform var(--duration-base) var(--ease-out);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(0.75rem) scale(0.98);
}

@media (max-width: 640px) {
  .modal-content {
    padding: var(--space-5);
    gap: var(--space-4);
  }
}
</style>
