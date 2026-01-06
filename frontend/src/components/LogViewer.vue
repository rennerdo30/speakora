<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import axios from 'axios'
import { Search, X } from 'lucide-vue-next'

const props = defineProps<{
  jobId: string | null
  autoRefresh?: boolean
}>()

const emit = defineEmits(['close'])

const logs = ref('')
const loading = ref(false)
const searchQuery = ref('')
const autoScroll = ref(true)
const refreshInterval = ref<number | null>(null)

const fetchLogs = async () => {
  if (!props.jobId) return
  
  loading.value = true
  try {
    const response = await axios.get(`/api/jobs/${props.jobId}/logs`)
    logs.value = response.data.logs || 'No logs available for this job yet.'
  } catch (err) {
    console.error('Failed to fetch logs', err)
    logs.value = 'Failed to load logs.'
  } finally {
    loading.value = false
  }
}

const filteredLogs = () => {
  if (!searchQuery.value) return logs.value
  
  const lines = logs.value.split('\n')
  const query = searchQuery.value.toLowerCase()
  return lines
    .filter(line => line.toLowerCase().includes(query))
    .join('\n')
}

const scrollToBottom = () => {
  const container = document.getElementById('log-container')
  if (container && autoScroll.value) {
    container.scrollTop = container.scrollHeight
  }
}

watch(() => props.jobId, () => {
  if (props.jobId) {
    fetchLogs()
  }
}, { immediate: true })

watch(() => logs.value, () => {
  if (autoScroll.value) {
    setTimeout(scrollToBottom, 100)
  }
})

onMounted(() => {
  if (props.autoRefresh) {
    refreshInterval.value = setInterval(fetchLogs, 2000) // Refresh every 2 seconds
  }
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<template>
  <div class="log-viewer glass-card">
    <div class="log-header">
      <h3>Job Logs</h3>
      <div class="log-controls">
        <div class="search-box">
          <Search :size="16" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search logs..."
            class="search-input"
          />
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="clear-search"
          >
            <X :size="14" />
          </button>
        </div>
        <label class="auto-scroll-toggle">
          <input 
            type="checkbox" 
            v-model="autoScroll"
          />
          Auto-scroll
        </label>
        <button @click="fetchLogs" class="refresh-btn">Refresh</button>
      </div>
    </div>
    
    <div 
      id="log-container" 
      class="log-container"
      @scroll="autoScroll = false"
    >
      <div v-if="loading && !logs" class="loading">
        Loading logs...
      </div>
      <pre v-else class="log-content">{{ filteredLogs() }}</pre>
    </div>
  </div>
</template>

<style scoped>
.log-viewer {
  padding: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 600px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.log-header h3 {
  font-size: 1.125rem;
  margin: 0;
}

.log-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 6px 12px;
  position: relative;
}

.search-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.875rem;
  width: 200px;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.clear-search {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.auto-scroll-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.refresh-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: var(--primary-hover);
}

.log-container {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
  overflow-x: auto;
  min-height: 300px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

.log-content {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.8125rem;
  color: #a78bfa;
  white-space: pre-wrap;
  line-height: 1.5;
  word-break: break-all;
}

@media (max-width: 768px) {
  .log-viewer {
    padding: 16px;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .log-controls {
    width: 100%;
  }
  
  .search-input {
    width: 150px;
  }
}
</style>

