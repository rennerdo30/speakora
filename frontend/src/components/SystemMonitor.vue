<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/systemStore'
import { Cpu, HardDrive, Activity, Database, AlertTriangle } from 'lucide-vue-next'
import {
  METER_DANGER_PERCENT,
  METER_WARNING_PERCENT,
  SYSTEM_STATUS_POLL_MS
} from '../constants'
import { formatCount, formatMegabytes, formatPercent, toSafePercent } from '../utils/format'

/** Placeholder cards rendered while the first status request is in flight. */
const MONITOR_SKELETON_COUNT = 4

const systemStore = useSystemStore()
let updateTimer: ReturnType<typeof setInterval> | undefined

const refresh = () => {
  systemStore.fetchStatus()
  systemStore.fetchStats()
}

onMounted(() => {
  refresh()
  updateTimer = setInterval(refresh, SYSTEM_STATUS_POLL_MS)
})

onUnmounted(() => clearInterval(updateTimer))

const isInitialLoad = computed(() => systemStore.loading && !systemStore.status)

const gpuMemory = computed(() => systemStore.status?.gpu_memory ?? null)
const hasGpuReading = computed(() => gpuMemory.value?.allocated_mb !== undefined)

const gpuPercent = computed(() =>
  toSafePercent(gpuMemory.value?.allocated_mb, gpuMemory.value?.total_mb)
)

const cpuPercent = computed(() => systemStore.status?.cpu.percent ?? 0)
const memoryPercent = computed(() => systemStore.status?.memory.percent ?? 0)

/** Meters turn amber, then red, as utilisation climbs. */
const meterClass = (percent: number) => ({
  'is-warning': percent >= METER_WARNING_PERCENT && percent < METER_DANGER_PERCENT,
  'is-danger': percent >= METER_DANGER_PERCENT
})

const QUEUE_ROWS = [
  { key: 'total', label: 'Total', tone: '' },
  { key: 'queued', label: 'Queued', tone: 'is-queued' },
  { key: 'running', label: 'Running', tone: 'is-running' },
  { key: 'paused', label: 'Paused', tone: 'is-paused' },
  { key: 'completed', label: 'Completed', tone: 'is-completed' },
  { key: 'failed', label: 'Failed', tone: 'is-failed' }
] as const

const queueCounts = computed(() => systemStore.status?.queue)
</script>

<template>
  <section class="system-monitor glass-card fade-in" aria-labelledby="system-monitor-heading">
    <h2 id="system-monitor-heading">System monitor</h2>

    <div v-if="isInitialLoad" class="monitor-grid">
      <div
        v-for="card in MONITOR_SKELETON_COUNT"
        :key="card"
        class="skeleton skeleton-card"
        aria-hidden="true"
      ></div>
      <p class="sr-only" role="status">Loading system information…</p>
    </div>

    <p v-else-if="!systemStore.status" class="alert alert-danger" role="alert">
      <AlertTriangle :size="18" aria-hidden="true" />
      <span>{{ systemStore.error || 'System status is currently unavailable.' }}</span>
    </p>

    <div v-else class="monitor-grid">
      <article class="monitor-card">
        <h3 class="card-header"><HardDrive :size="18" aria-hidden="true" /> GPU memory</h3>
        <template v-if="hasGpuReading">
          <div
            class="meter"
            role="progressbar"
            :aria-valuenow="Math.round(gpuPercent)"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-label="GPU memory in use"
          >
            <div
              class="meter-fill"
              :class="meterClass(gpuPercent)"
              :style="{ width: `${gpuPercent}%` }"
            ></div>
          </div>
          <p class="card-readout">
            <span>
              {{ formatMegabytes(gpuMemory?.allocated_mb) }} /
              {{ formatMegabytes(gpuMemory?.total_mb) }}
            </span>
            <span class="readout-muted">{{ formatPercent(gpuPercent) }}</span>
          </p>
        </template>
        <p v-else class="card-readout">
          <span class="readout-muted">{{ gpuMemory?.info || 'No GPU detected' }}</span>
        </p>
      </article>

      <article class="monitor-card">
        <h3 class="card-header"><Cpu :size="18" aria-hidden="true" /> CPU usage</h3>
        <div
          class="meter"
          role="progressbar"
          :aria-valuenow="Math.round(cpuPercent)"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-label="CPU usage"
        >
          <div
            class="meter-fill"
            :class="meterClass(cpuPercent)"
            :style="{ width: `${cpuPercent}%` }"
          ></div>
        </div>
        <p class="card-readout">
          <span>{{ formatPercent(cpuPercent, 1) }}</span>
          <span class="readout-muted">{{ formatCount(systemStore.status.cpu.count) }} cores</span>
        </p>
      </article>

      <article class="monitor-card">
        <h3 class="card-header"><Activity :size="18" aria-hidden="true" /> System memory</h3>
        <div
          class="meter"
          role="progressbar"
          :aria-valuenow="Math.round(memoryPercent)"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-label="System memory in use"
        >
          <div
            class="meter-fill"
            :class="meterClass(memoryPercent)"
            :style="{ width: `${memoryPercent}%` }"
          ></div>
        </div>
        <p class="card-readout">
          <span>
            {{ formatMegabytes(systemStore.status.memory.used_mb) }} /
            {{ formatMegabytes(systemStore.status.memory.total_mb) }}
          </span>
          <span class="readout-muted">{{ formatPercent(memoryPercent, 1) }}</span>
        </p>
      </article>

      <article class="monitor-card">
        <h3 class="card-header"><Database :size="18" aria-hidden="true" /> Job queue</h3>
        <dl class="queue-list">
          <div v-for="row in QUEUE_ROWS" :key="row.key" class="queue-row">
            <dt>{{ row.label }}</dt>
            <dd :class="row.tone">{{ formatCount(queueCounts?.[row.key]) }}</dd>
          </div>
        </dl>
      </article>
    </div>

    <div v-if="systemStore.stats" class="stats-section">
      <h3>Statistics</h3>
      <dl class="stats-grid">
        <div class="stat-item">
          <dt>Completion rate</dt>
          <dd>{{ formatPercent(systemStore.stats.completion_rate, 1) }}</dd>
        </div>
        <div class="stat-item">
          <dt>Average processing time</dt>
          <dd>{{ formatCount(systemStore.stats.average_processing_time) }}s</dd>
        </div>
        <div class="stat-item">
          <dt>Total jobs</dt>
          <dd>{{ formatCount(systemStore.stats.total_jobs) }}</dd>
        </div>
        <div class="stat-item">
          <dt>Completed</dt>
          <dd>{{ formatCount(systemStore.stats.completed_count) }}</dd>
        </div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.system-monitor {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: var(--space-6);
}

.system-monitor h2 {
  font-size: var(--text-xl);
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
  gap: var(--space-4);
}

.skeleton-card {
  height: 7rem;
  border-radius: var(--radius-lg);
}

.monitor-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--surface-raised);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
}

.card-readout {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}

.readout-muted {
  color: var(--text-muted);
}

.queue-list {
  display: grid;
  gap: var(--space-2);
}

.queue-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: var(--text-md);
}

.queue-row dt {
  color: var(--text-secondary);
}

.queue-row dd {
  font-weight: var(--weight-semibold);
  font-variant-numeric: tabular-nums;
}

.queue-row dd.is-queued {
  color: var(--text-muted);
}

.queue-row dd.is-running {
  color: var(--info-color);
}

.queue-row dd.is-paused {
  color: var(--warning-color);
}

.queue-row dd.is-completed {
  color: var(--success-color);
}

.queue-row dd.is-failed {
  color: var(--danger-color);
}

.stats-section {
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-color);
}

.stats-section h3 {
  margin-bottom: var(--space-4);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr));
  gap: var(--space-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-item dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.stat-item dd {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
  font-variant-numeric: tabular-nums;
}
</style>
