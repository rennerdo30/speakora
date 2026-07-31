<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { Download, Check, AlertCircle, X } from 'lucide-vue-next'
import { MODAL_AUTO_CLOSE_MS } from '../constants'
import { useDialog } from '../composables/useDialog'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])

const MODEL_OPTIONS = [
  { value: 'small', name: 'Small', description: 'About 1.2 GB — fastest, lower quality' },
  { value: 'medium', name: 'Medium', description: 'About 3.5 GB — balanced' },
  { value: 'large', name: 'Large', description: 'About 10 GB — best quality' }
]

const modelSize = ref('large')
const status = ref<'idle' | 'downloading' | 'success' | 'error'>('idle')
const error = ref('')

const { dialogRef } = useDialog(
  () => props.show,
  () => emit('close')
)

const startDownload = async () => {
  status.value = 'downloading'
  error.value = ''

  try {
    await axios.post('/api/system/download', { model_size: modelSize.value })
    status.value = 'success'
    setTimeout(() => {
      emit('close')
      status.value = 'idle'
    }, MODAL_AUTO_CLOSE_MS)
  } catch (err: any) {
    status.value = 'error'
    error.value = err.response?.data?.detail || 'Could not start the download.'
  }
}
</script>

<template>
  <Transition name="modal">
    <div v-if="show" class="modal-overlay" @click.self="emit('close')">
      <div
        ref="dialogRef"
        class="modal-content glass-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="download-model-title"
        tabindex="-1"
      >
        <div class="modal-header">
          <h2 id="download-model-title">Download models</h2>
          <button
            type="button"
            class="icon-btn is-borderless"
            aria-label="Close dialog"
            @click="emit('close')"
          >
            <X :size="20" aria-hidden="true" />
          </button>
        </div>

        <div class="modal-body">
          <p class="description">
            Pre-download the SeamlessM4T v2 weights into the local cache so the first translation
            starts immediately.
          </p>

          <fieldset class="model-options">
            <legend class="form-label">Model size</legend>
            <label
              v-for="option in MODEL_OPTIONS"
              :key="option.value"
              class="model-option"
              :class="{ 'is-selected': modelSize === option.value }"
            >
              <input
                v-model="modelSize"
                type="radio"
                name="model-size"
                :value="option.value"
                :data-autofocus="modelSize === option.value ? '' : undefined"
              />
              <span class="option-content">
                <span class="option-name">{{ option.name }}</span>
                <span class="option-description">{{ option.description }}</span>
              </span>
            </label>
          </fieldset>

          <p v-if="status === 'success'" class="alert alert-success" role="status">
            <Check :size="18" aria-hidden="true" />
            <span>Download started. You can close this dialog.</span>
          </p>

          <p v-else-if="status === 'error'" class="alert alert-danger" role="alert">
            <AlertCircle :size="18" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="emit('close')">Cancel</button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="status === 'downloading' || status === 'success'"
            :aria-busy="status === 'downloading'"
            @click="startDownload"
          >
            <span v-if="status === 'downloading'" class="spinner spinner-sm" aria-hidden="true"></span>
            <Download v-else :size="18" aria-hidden="true" />
            {{ status === 'downloading' ? 'Starting…' : 'Start download' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
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
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.modal-content {
  display: flex;
  flex-direction: column;
  width: var(--modal-width-sm);
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
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.modal-header h2 {
  font-size: var(--text-xl);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.description {
  color: var(--text-secondary);
  font-size: var(--text-md);
}

.model-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  border: none;
}

.model-options legend {
  margin-bottom: var(--space-3);
}

.model-option {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--surface-raised);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition-colors);
}

.model-option:hover {
  border-color: var(--border-strong);
  background: var(--surface-hover);
}

.model-option:has(input:focus-visible) {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.model-option.is-selected {
  border-color: var(--primary-color);
  background: var(--primary-soft);
}

.option-content {
  display: flex;
  flex-direction: column;
}

.option-name {
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

.option-description {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.btn-primary .spinner {
  border-color: currentColor;
  border-top-color: transparent;
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
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .modal-footer .btn {
    width: 100%;
  }
}
</style>
