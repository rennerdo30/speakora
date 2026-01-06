<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { X, Send, FileAudio, Globe, Zap } from 'lucide-vue-next'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'submitted'])

const input_file = ref('')
const target_lang = ref('deu')
const source_lang = ref('auto')
const priority = ref(0)
const submitting = ref(false)
const error = ref('')

const languages = [
  { code: 'deu', name: 'German' },
  { code: 'fra', name: 'French' },
  { code: 'spa', name: 'Spanish' },
  { code: 'ita', name: 'Italian' },
  { code: 'jpn', name: 'Japanese' },
  { code: 'zho', name: 'Chinese' },
  { code: 'rus', name: 'Russian' },
  { code: 'kor', name: 'Korean' }
]

const submitJob = async () => {
  if (!input_file.value) {
    error.value = 'Please provide an input file path.'
    return
  }

  submitting.value = true
  error.value = ''
  
  try {
    await axios.post('/api/jobs', {
      input_file: input_file.value,
      target_lang: target_lang.value,
      source_lang: source_lang.value,
      priority: priority.value
    })
    emit('submitted')
    emit('close')
    input_file.value = ''
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit job.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content glass-card fade-in">
      <div class="modal-header">
        <h2>New Translation</h2>
        <button class="close-btn" @click="emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>
            <FileAudio :size="16" />
            Input File Path
          </label>
          <input 
            v-model="input_file" 
            type="text" 
            placeholder="/path/to/audio.wav"
            class="form-input"
          />
          <span class="hint">Absolute path to a .wav or .mp3 file.</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>
              <Globe :size="16" />
              Source Language
            </label>
            <select v-model="source_lang" class="form-input">
              <option value="auto">Auto-detect</option>
              <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>
              <Globe :size="16" />
              Target Language
            </label>
            <select v-model="target_lang" class="form-input">
              <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>
            <Zap :size="16" />
            Priority
          </label>
          <input 
            v-model.number="priority" 
            type="number" 
            min="0" 
            max="100"
            class="form-input"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="submitJob"
          :disabled="submitting"
        >
          <Send :size="18" />
          {{ submitting ? 'Submitting...' : 'Submit Job' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  width: 500px;
  max-width: 95vw;
  padding: 32px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 14px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.08);
}

.hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.error-message {
  color: #f87171;
  font-size: 0.875rem;
  margin-top: 12px;
  background: rgba(239, 68, 68, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
