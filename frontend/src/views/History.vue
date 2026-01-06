<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Search, Filter, Trash2, ExternalLink, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import JobDetails from '../components/JobDetails.vue'

interface Job {
  id: string
  status: string
  input_file: string
  target_lang: string
  completed_at: string | null
}

const jobs = ref<Job[]>([])
const loading = ref(true)
const searchQuery = ref('')
const statusFilter = ref('all')
const selectedJobId = ref<string | null>(null)
const showDetailsModal = ref(false)

const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/jobs')
    // For history, we usually show completed, failed, or just all in descending order
    jobs.value = res.data.sort((a: any, b: any) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  } catch (err) {
    console.error('Failed to fetch history', err)
  } finally {
    loading.value = false
  }
}

const filteredJobs = () => {
  return jobs.value.filter(job => {
    const matchesSearch = job.input_file.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         job.id.includes(searchQuery.value)
    const matchesStatus = statusFilter.value === 'all' || job.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
}

const openDetails = (id: string) => {
  selectedJobId.value = id
  showDetailsModal.value = true
}

const deleteJob = async (id: string) => {
  if (confirm('Are you sure you want to delete this job record?')) {
    try {
      await axios.delete(`/api/jobs/${id}`)
      fetchHistory()
    } catch (err) {
      console.error('Failed to delete job', err)
    }
  }
}

onMounted(fetchHistory)
</script>

<template>
  <div class="history-view fade-in">
    <header class="header">
      <div class="header-content">
        <h1>Translation History</h1>
        <p class="text-secondary">View and manage past translation jobs</p>
      </div>
    </header>

    <div class="filters-bar glass-card">
      <div class="search-box">
        <Search :size="18" />
        <input v-model="searchQuery" type="text" placeholder="Search by file name or ID..." />
      </div>
      <div class="status-select">
        <Filter :size="18" />
        <select v-model="statusFilter">
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="paused">Paused</option>
        </select>
      </div>
    </div>

    <div class="history-list glass-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
      <div v-else-if="filteredJobs().length === 0" class="empty-state">
        No records found matching your criteria.
      </div>
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Status</th>
              <th>Input File</th>
              <th>Language</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in filteredJobs()" :key="job.id">
              <td>{{ new Date(job.created_at).toLocaleDateString() }}</td>
              <td>
                <span :class="'badge badge-' + job.status.toLowerCase()">{{ job.status }}</span>
              </td>
              <td class="file-cell" :title="job.input_file">
                {{ job.input_file.split('/').pop() }}
              </td>
              <td>{{ job.target_lang.toUpperCase() }}</td>
              <td class="actions-cell">
                <button class="action-btn" @click="openDetails(job.id)">
                  <ExternalLink :size="16" />
                </button>
                <button class="action-btn delete" @click="deleteJob(job.id)">
                  <Trash2 :size="16" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
        <button class="btn btn-secondary btn-sm" disabled><ChevronLeft :size="16" /></button>
        <span class="page-info">Page 1 of 1</span>
        <button class="btn btn-secondary btn-sm" disabled><ChevronRight :size="16" /></button>
      </div>
    </div>

    <JobDetails
      :show="showDetailsModal"
      :jobId="selectedJobId"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<style scoped>
.history-view { padding: 10px; }
.header { margin-bottom: 24px; }
.filters-bar { padding: 16px; display: flex; gap: 20px; margin-bottom: 20px; }
.search-box { flex-grow: 1; position: relative; display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border-color); }
.search-box input { background: transparent; border: none; color: white; width: 100%; outline: none; }
.status-select { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border-color); }
.status-select select { background: transparent; border: none; color: white; outline: none; cursor: pointer; }

.history-list { padding: 0; overflow: hidden; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 16px; color: var(--text-muted); font-size: 0.75rem; border-bottom: 1px solid var(--border-color); }
td { padding: 16px; border-bottom: 1px solid var(--border-color); font-size: 0.875rem; }
.file-cell { max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.actions-cell { display: flex; gap: 8px; justify-content: flex-end; }
.action-btn { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.action-btn:hover { background: var(--surface-hover); color: white; }
.action-btn.delete:hover { color: #f87171; }

.pagination { padding: 16px; display: flex; justify-content: center; align-items: center; gap: 20px; }
.page-info { font-size: 0.875rem; color: var(--text-muted); }

.loading-state, .empty-state { padding: 60px; text-align: center; color: var(--text-muted); }
.spinner { width: 30px; height: 30px; border: 2px solid var(--border-color); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
