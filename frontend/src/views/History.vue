<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import axios from 'axios'
import {
  Search,
  Filter,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  SearchX,
  Inbox
} from 'lucide-vue-next'
import JobDetails from '../components/JobDetails.vue'
import { HISTORY_PAGE_SIZE, SKELETON_ROW_COUNT } from '../constants'
import { fileNameOf, formatDate, toTimestamp } from '../utils/format'

interface HistoryJob {
  id: string
  status: string
  input_file: string
  target_lang: string
  created_at?: string
  completed_at: string | null
}

const STATUS_FILTERS = [
  { value: 'all', label: 'All statuses' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'paused', label: 'Paused' },
  { value: 'cancelled', label: 'Cancelled' }
]

const jobs = ref<HistoryJob[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const selectedJobId = ref<string | null>(null)
const showDetailsModal = ref(false)

const fetchHistory = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get<HistoryJob[]>('/api/jobs')
    jobs.value = [...res.data].sort(
      (a, b) => toTimestamp(b.created_at) - toTimestamp(a.created_at)
    )
  } catch (err: unknown) {
    console.error('Failed to fetch history', err)
    error.value = 'Could not load the translation history. Check that the backend is running.'
  } finally {
    loading.value = false
  }
}

const filteredJobs = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return jobs.value.filter((job) => {
    const matchesSearch =
      !query || job.input_file.toLowerCase().includes(query) || job.id.toLowerCase().includes(query)
    const matchesStatus = statusFilter.value === 'all' || job.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

const pageCount = computed(() => Math.max(1, Math.ceil(filteredJobs.value.length / HISTORY_PAGE_SIZE)))

const pagedJobs = computed(() => {
  const start = (currentPage.value - 1) * HISTORY_PAGE_SIZE
  return filteredJobs.value.slice(start, start + HISTORY_PAGE_SIZE)
})

const hasFilters = computed(() => searchQuery.value.trim() !== '' || statusFilter.value !== 'all')

// Filtering can shrink the list below the current page.
watch([filteredJobs, pageCount], () => {
  if (currentPage.value > pageCount.value) currentPage.value = pageCount.value
})

const goToPage = (page: number) => {
  currentPage.value = Math.min(Math.max(1, page), pageCount.value)
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
}

const openDetails = (id: string) => {
  selectedJobId.value = id
  showDetailsModal.value = true
}

const deleteJob = async (job: HistoryJob) => {
  if (!confirm(`Delete the record for "${fileNameOf(job.input_file)}"?`)) return

  try {
    await axios.delete(`/api/jobs/${job.id}`)
    await fetchHistory()
  } catch (err: unknown) {
    console.error('Failed to delete job', err)
    error.value = 'Could not delete that record. Please try again.'
  }
}

onMounted(fetchHistory)
</script>

<template>
  <div class="history-view fade-in">
    <header class="page-header">
      <div>
        <h1>Translation history</h1>
        <p class="page-subtitle">Review and manage past translation jobs</p>
      </div>
    </header>

    <form class="filters-bar glass-card" role="search" @submit.prevent>
      <div class="field">
        <label class="sr-only" for="history-search">Search history</label>
        <span class="field-icon" aria-hidden="true"><Search :size="18" /></span>
        <input
          id="history-search"
          v-model="searchQuery"
          type="search"
          class="form-input has-icon"
          placeholder="Search by file name or job ID…"
        />
      </div>
      <div class="field">
        <label class="sr-only" for="history-status">Filter by status</label>
        <span class="field-icon" aria-hidden="true"><Filter :size="18" /></span>
        <select id="history-status" v-model="statusFilter" class="form-input has-icon">
          <option v-for="option in STATUS_FILTERS" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
    </form>

    <section class="history-list glass-card" aria-label="Translation history">
      <p v-if="error" class="alert alert-danger error-banner" role="alert">
        <AlertTriangle :size="18" aria-hidden="true" />
        <span>{{ error }}</span>
        <button type="button" class="btn btn-secondary btn-sm" @click="fetchHistory">Retry</button>
      </p>

      <div v-if="loading" class="skeleton-rows">
        <p class="sr-only" role="status">Loading history…</p>
        <div
          v-for="row in SKELETON_ROW_COUNT"
          :key="row"
          class="skeleton skeleton-row"
          aria-hidden="true"
        ></div>
      </div>

      <div v-else-if="filteredJobs.length === 0" class="empty-state">
        <span class="empty-state-icon">
          <SearchX v-if="hasFilters" :size="22" aria-hidden="true" />
          <Inbox v-else :size="22" aria-hidden="true" />
        </span>
        <p class="empty-state-title">
          {{ hasFilters ? 'No matching records' : 'No history yet' }}
        </p>
        <p class="empty-state-body">
          {{
            hasFilters
              ? 'Try a different search term or status filter.'
              : 'Completed and failed translations are listed here once you have run a job.'
          }}
        </p>
        <button
          v-if="hasFilters"
          type="button"
          class="btn btn-secondary"
          @click="clearFilters"
        >
          Clear filters
        </button>
      </div>

      <template v-else>
        <div class="table-container">
          <table class="data-table">
            <caption class="sr-only">
              Past translation jobs, newest first
            </caption>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Status</th>
                <th scope="col">Input file</th>
                <th scope="col">Language</th>
                <th scope="col"><span class="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in pagedJobs" :key="job.id">
                <td data-label="Date">{{ formatDate(job.created_at) }}</td>
                <td data-label="Status">
                  <span :class="`badge badge-${job.status.toLowerCase()}`">{{ job.status }}</span>
                </td>
                <td data-label="File" class="file-cell">
                  <span :title="job.input_file">{{ fileNameOf(job.input_file) }}</span>
                </td>
                <td data-label="Language">{{ job.target_lang.toUpperCase() }}</td>
                <td class="actions-cell is-stacked-full">
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
                    aria-label="Delete job record"
                    title="Delete record"
                    @click="deleteJob(job)"
                  >
                    <Trash2 :size="16" aria-hidden="true" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <nav v-if="pageCount > 1" class="pagination" aria-label="History pages">
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            :disabled="currentPage === 1"
            aria-label="Previous page"
            @click="goToPage(currentPage - 1)"
          >
            <ChevronLeft :size="16" aria-hidden="true" />
          </button>
          <span class="page-info" aria-live="polite">
            Page {{ currentPage }} of {{ pageCount }}
          </span>
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            :disabled="currentPage === pageCount"
            aria-label="Next page"
            @click="goToPage(currentPage + 1)"
          >
            <ChevronRight :size="16" aria-hidden="true" />
          </button>
        </nav>
      </template>
    </section>

    <JobDetails
      :show="showDetailsModal"
      :jobId="selectedJobId"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<style scoped>
.history-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.page-subtitle {
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-md);
}

.filters-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  padding: var(--space-4);
}

.field {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 0;
}

.field:first-child {
  flex: 1 1 18rem;
}

.field-icon {
  position: absolute;
  left: var(--space-3);
  display: grid;
  place-items: center;
  color: var(--text-muted);
  pointer-events: none;
}

.form-input.has-icon {
  padding-left: var(--space-10);
}

.history-list {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.error-banner {
  align-items: center;
  margin: var(--space-4) var(--space-4) 0;
}

.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  min-width: 44rem;
}

.file-cell span {
  display: block;
  max-width: 20rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  gap: var(--space-2);
}

.skeleton-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-5);
}

.skeleton-row {
  height: 2.75rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.page-info {
  color: var(--text-muted);
  font-size: var(--text-md);
  font-variant-numeric: tabular-nums;
}

@media (max-width: 640px) {
  .data-table {
    min-width: 0;
  }

  .table-container {
    overflow-x: visible;
  }

  .file-cell span {
    max-width: none;
  }
}
</style>
