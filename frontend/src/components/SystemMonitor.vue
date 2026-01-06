<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/systemStore'
import { Cpu, HardDrive, Activity, Database } from 'lucide-vue-next'

const systemStore = useSystemStore()
const updateInterval = ref<number | null>(null)

onMounted(() => {
  systemStore.fetchStatus()
  systemStore.fetchStats()
  
  // Update every 5 seconds
  updateInterval.value = setInterval(() => {
    systemStore.fetchStatus()
    systemStore.fetchStats()
  }, 5000)
})

onUnmounted(() => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})

const formatMB = (mb: number) => {
  if (mb >= 1024) {
    return `${(mb / 1024).toFixed(2)} GB`
  }
  return `${mb.toFixed(0)} MB`
}
</script>

<template>
  <div class="system-monitor glass-card fade-in">
    <h2>System Monitor</h2>
    
    <div v-if="systemStore.loading && !systemStore.status" class="loading">
      Loading system information...
    </div>
    
    <div v-else-if="systemStore.status" class="monitor-grid">
      <!-- GPU Memory -->
      <div class="monitor-card">
        <div class="card-header">
          <HardDrive :size="20" />
          <span>GPU Memory</span>
        </div>
        <div class="card-content">
          <div v-if="systemStore.status.gpu_memory.allocated_mb !== undefined" class="memory-info">
            <div class="memory-bar">
              <div 
                class="memory-fill" 
                :style="{ 
                  width: `${(systemStore.status.gpu_memory.allocated_mb / systemStore.status.gpu_memory.total_mb) * 100}%` 
                }"
              ></div>
            </div>
            <div class="memory-stats">
              <span>{{ formatMB(systemStore.status.gpu_memory.allocated_mb) }} / {{ formatMB(systemStore.status.gpu_memory.total_mb) }}</span>
            </div>
          </div>
          <div v-else class="memory-info">
            <span>{{ systemStore.status.gpu_memory.info || 'GPU not available' }}</span>
          </div>
        </div>
      </div>

      <!-- CPU Usage -->
      <div class="monitor-card">
        <div class="card-header">
          <Cpu :size="20" />
          <span>CPU Usage</span>
        </div>
        <div class="card-content">
          <div class="cpu-info">
            <div class="cpu-bar">
              <div 
                class="cpu-fill" 
                :style="{ width: `${systemStore.status.cpu.percent}%` }"
              ></div>
            </div>
            <div class="cpu-stats">
              <span>{{ systemStore.status.cpu.percent.toFixed(1) }}%</span>
              <span class="cpu-count">{{ systemStore.status.cpu.count }} cores</span>
            </div>
          </div>
        </div>
      </div>

      <!-- System Memory -->
      <div class="monitor-card">
        <div class="card-header">
          <Activity :size="20" />
          <span>System Memory</span>
        </div>
        <div class="card-content">
          <div class="memory-info">
            <div class="memory-bar">
              <div 
                class="memory-fill" 
                :style="{ width: `${systemStore.status.memory.percent}%` }"
              ></div>
            </div>
            <div class="memory-stats">
              <span>{{ formatMB(systemStore.status.memory.used_mb) }} / {{ formatMB(systemStore.status.memory.total_mb) }}</span>
              <span class="memory-percent">{{ systemStore.status.memory.percent.toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Queue Status -->
      <div class="monitor-card">
        <div class="card-header">
          <Database :size="20" />
          <span>Job Queue</span>
        </div>
        <div class="card-content">
          <div class="queue-stats">
            <div class="queue-item">
              <span class="label">Total:</span>
              <span class="value">{{ systemStore.status.queue.total }}</span>
            </div>
            <div class="queue-item">
              <span class="label">Queued:</span>
              <span class="value queued">{{ systemStore.status.queue.queued }}</span>
            </div>
            <div class="queue-item">
              <span class="label">Running:</span>
              <span class="value running">{{ systemStore.status.queue.running }}</span>
            </div>
            <div class="queue-item">
              <span class="label">Paused:</span>
              <span class="value paused">{{ systemStore.status.queue.paused }}</span>
            </div>
            <div class="queue-item">
              <span class="label">Completed:</span>
              <span class="value completed">{{ systemStore.status.queue.completed }}</span>
            </div>
            <div class="queue-item">
              <span class="label">Failed:</span>
              <span class="value failed">{{ systemStore.status.queue.failed }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div v-if="systemStore.stats" class="stats-section">
      <h3>Statistics</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">Completion Rate</span>
          <span class="stat-value">{{ systemStore.stats.completion_rate }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avg Processing Time</span>
          <span class="stat-value">{{ systemStore.stats.average_processing_time }}s</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Total Jobs</span>
          <span class="stat-value">{{ systemStore.stats.total_jobs }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Completed</span>
          <span class="stat-value">{{ systemStore.stats.completed_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-monitor {
  padding: 24px;
  margin-bottom: 24px;
}

.system-monitor h2 {
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.monitor-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.card-content {
  color: var(--text-primary);
}

.memory-bar, .cpu-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.memory-fill, .cpu-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transition: width 0.3s ease;
}

.memory-stats, .cpu-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.cpu-count, .memory-percent {
  color: var(--text-muted);
}

.queue-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.queue-item .label {
  color: var(--text-secondary);
}

.queue-item .value {
  font-weight: 600;
}

.queue-item .value.queued { color: var(--text-muted); }
.queue-item .value.running { color: var(--primary-color); }
.queue-item .value.paused { color: #fbbf24; }
.queue-item .value.completed { color: var(--accent-color); }
.queue-item .value.failed { color: #f87171; }

.stats-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.stats-section h3 {
  margin-bottom: 16px;
  font-size: 1.125rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .monitor-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

