<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { Download, Check, AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])

const modelSize = ref('large')
const downloading = ref(false)
const status = ref<'idle' | 'downloading' | 'success' | 'error'>('idle')
const error = ref('')

const startDownload = async () => {
  downloading.value = true
  status.value = 'downloading'
  error.value = ''
  
  try {
    // This API call should trigger the backend download
    // Since backend download might take long, we shouldn't block
    // But for simplicity in this demo, we'll wait or use a background task
    await axios.post('/api/system/download', { model_size: modelSize.value })
    status.value = 'success'
    setTimeout(() => {
      emit('close')
      status.value = 'idle'
    }, 2000)
  } catch (err: any) {
    status.value = 'error'
    error.value = err.response?.data?.detail || 'Failed to start download.'
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content glass-card fade-in">
      <div class="modal-header">
        <h2>Download Models</h2>
        <button class="close-btn" @click="emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="modal-body">
        <p class="description">
          Pre-download the SeamlessM4T v2 models to your local cache for faster startup.
        </p>

        <div class="form-group">
          <label>Select Model Size</label>
          <div class="model-options">
            <label class="model-option" :class="{ active: modelSize === 'small' }">
              <input type="radio" v-model="modelSize" value="small" />
              <div class="option-content">
                <span class="size-name">Small</span>
                <span class="size-desc">~1.2GB - Faster, lower quality</span>
              </div>
            </label>
            <label class="model-option" :class="{ active: modelSize === 'medium' }">
              <input type="radio" v-model="modelSize" value="medium" />
              <div class="option-content">
                <span class="size-name">Medium</span>
                <span class="size-desc">~3.5GB - Balanced</span>
              </div>
            </label>
            <label class="model-option" :class="{ active: modelSize === 'large' }">
              <input type="radio" v-model="modelSize" value="large" />
              <div class="option-content">
                <span class="size-name">Large</span>
                <span class="size-desc">~10GB - Best quality</span>
              </div>
            </label>
          </div>
        </div>

        <div v-if="status === 'success'" class="success-message">
          <Check :size="18" />
          Model download started successfully!
        </div>
        
        <div v-if="status === 'error'" class="error-message">
          <AlertCircle :size="18" />
          {{ error }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="startDownload"
          :disabled="downloading || status === 'success'"
        >
          <Download :size="18" />
          {{ downloading ? 'Downloading...' : 'Start Download' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  width: 450px;
  max-width: 95vw;
  padding: 32px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 24px;
}

.model-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.model-option {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.model-option:hover {
  background: rgba(255, 255, 255, 0.06);
}

.model-option.active {
  border-color: var(--primary-color);
  background: rgba(59, 130, 246, 0.05);
}

.model-option input {
  margin-right: 16px;
}

.option-content {
  display: flex;
  flex-direction: column;
}

.size-name {
  font-weight: 600;
  color: var(--text-primary);
}

.size-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.success-message {
  margin-top: 20px;
  padding: 12px;
  background: rgba(16, 185, 129, 0.1);
  color: #34d399;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.error-message {
  margin-top: 20px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}
</style>
