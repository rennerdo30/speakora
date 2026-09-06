<script setup lang="ts">
import { computed, nextTick, ref, onMounted, watch, onUnmounted } from 'vue'
import axios from 'axios'
import { Search, X, RefreshCw, ScrollText } from 'lucide-vue-next'
import { JOB_LOG_POLL_MS } from '../constants'

const props = defineProps<{
  jobId: string | null
  autoRefresh?: boolean
}>()

/** How close to the bottom still counts as "following the tail", in pixels. */
const SCROLL_BOTTOM_TOLERANCE_PX = 24

const logs = ref('')
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const autoScroll = ref(true)
const logContainer = ref<HTMLElement | null>(null)
let refreshTimer: ReturnType<typeof setInterval> | undefined

const fetchLogs = async () => {
  if (!props.jobId) return

  loading.value = true
  try {
    const response = await axios.get(`/api/jobs/${props.jobId}/logs`)
    logs.value = response.data.logs || ''
    error.value = ''
  } catch (err) {
    console.error('Failed to fetch logs', err)
    error.value = 'Could not load the logs for this job.'
  } finally {
    loading.value = false
  }
}

const filteredLogs = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return logs.value

  return logs.value
    .split('\n')
    .filter((line) => line.toLowerCase().includes(query))
    .join('\n')
})

const matchCount = computed(() =>
  filteredLogs.value ? filteredLogs.value.split('\n').filter(Boolean).length : 0
)

const scrollToBottom = () => {
  const container = logContainer.value
  if (container && autoScroll.value) {
    container.scrollTop = container.scrollHeight
  }
}

/**
 * Follow the tail only while the reader is at the bottom. Programmatic scrolls
 * also land at the bottom, so they keep auto-scroll enabled.
 */
const onScroll = () => {
  const container = logContainer.value
  if (!container) return

  const distanceFromBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight
  autoScroll.value = distanceFromBottom <= SCROLL_BOTTOM_TOLERANCE_PX
}

watch(
  () => props.jobId,
  (jobId) => {
    logs.value = ''
    if (jobId) fetchLogs()
  },
  { immediate: true }
)

watch(filteredLogs, () => {
  if (autoScroll.value) nextTick(scrollToBottom)
})

onMounted(() => {
  if (props.autoRefresh) {
    refreshTimer = setInterval(fetchLogs, JOB_LOG_POLL_MS)
  }
})

onUnmounted(() => clearInterval(refreshTimer))
</script>

<template>
  <section class="log-viewer" aria-labelledby="job-logs-heading">
    <div class="log-header">
      <h3 id="job-logs-heading">
        <ScrollText :size="16" aria-hidden="true" />
        Job logs
      </h3>
      <div class="log-controls">
        <div class="search-field">
          <label class="sr-only" for="log-search">Search logs</label>
          <span class="search-icon" aria-hidden="true"><Search :size="16" /></span>
          <input
            id="log-search"
            v-model="searchQuery"
            type="search"
            class="form-input"
            placeholder="Search logs…"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="icon-btn is-borderless clear-search"
            aria-label="Clear log search"
            @click="searchQuery = ''"
          >
            <X :size="14" aria-hidden="true" />
          </button>
        </div>
        <label class="auto-scroll-toggle">
          <input v-model="autoScroll" type="checkbox" />
          Follow
        </label>
        <button
          type="button"
          class="btn btn-secondary btn-sm"
          :disabled="loading"
          @click="fetchLogs"
        >
          <RefreshCw :size="14" :class="{ spin: loading }" aria-hidden="true" />
          Refresh
        </button>
      </div>
    </div>

    <p v-if="error" class="alert alert-danger" role="alert">{{ error }}</p>

    <div
      ref="logContainer"
      class="log-container"
      tabindex="0"
      role="log"
      aria-label="Job log output"
      @scroll.passive="onScroll"
    >
      <p v-if="loading && !logs" class="log-placeholder" role="status">Loading logs…</p>
      <p v-else-if="!logs" class="log-placeholder">No log output for this job yet.</p>
      <p v-else-if="searchQuery && matchCount === 0" class="log-placeholder">
        No log lines match “{{ searchQuery }}”.
      </p>
      <pre v-else class="log-content">{{ filteredLogs }}</pre>
    </div>
  </section>
</template>

<style scoped>
.log-viewer {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  min-height: 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.log-header h3 {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.log-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.search-field {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  display: grid;
  place-items: center;
  color: var(--text-muted);
  pointer-events: none;
}

.search-field .form-input {
  width: 13rem;
  min-height: var(--control-height-sm);
  padding-left: var(--space-8);
  padding-right: var(--space-8);
  font-size: var(--text-md);
}

.search-field .form-input::-webkit-search-cancel-button {
  display: none;
}

.clear-search {
  position: absolute;
  right: var(--space-1);
  width: 1.5rem;
  height: 1.5rem;
}

.auto-scroll-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-secondary);
  font-size: var(--text-md);
  cursor: pointer;
}

.log-container {
  flex: 1;
  min-height: 12rem;
  max-height: 22rem;
  overflow: auto;
  padding: var(--space-4);
  background: var(--surface-sunken);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.log-placeholder {
  padding: var(--space-8) 0;
  color: var(--text-muted);
  font-size: var(--text-md);
  text-align: center;
}

.log-content {
  margin: 0;
  color: var(--code-fg);
  font-size: var(--text-sm);
  line-height: var(--leading-snug);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

@media (max-width: 640px) {
  .log-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .log-controls {
    width: 100%;
  }

  .search-field {
    flex: 1 1 10rem;
  }

  .search-field .form-input {
    width: 100%;
  }
}
</style>
