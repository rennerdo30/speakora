<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { X, Send, FileAudio, Globe, Zap, AlertCircle } from 'lucide-vue-next'
import { TARGET_LANGUAGES } from '../constants'
import { useDialog } from '../composables/useDialog'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'submitted'])

const PRIORITY_MIN = 0
const PRIORITY_MAX = 100

const input_file = ref('')
const target_lang = ref('deu')
const source_lang = ref('auto')
const priority = ref(PRIORITY_MIN)
const expressive = ref(false)
const reference_audio = ref('')
const submitting = ref(false)
const error = ref('')

const { dialogRef } = useDialog(
  () => props.show,
  () => emit('close')
)

const submitJob = async () => {
  if (!input_file.value.trim()) {
    error.value = 'Please provide the path to an input file.'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    await axios.post('/api/jobs', {
      input_file: input_file.value.trim(),
      target_lang: target_lang.value,
      source_lang: source_lang.value,
      priority: priority.value,
      expressive: expressive.value,
      reference_audio: expressive.value && reference_audio.value ? reference_audio.value : null
    })
    emit('submitted')
    emit('close')
    input_file.value = ''
    reference_audio.value = ''
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Could not submit the job. Please try again.'
  } finally {
    submitting.value = false
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
        aria-labelledby="new-job-title"
        tabindex="-1"
      >
        <div class="modal-header">
          <h2 id="new-job-title">New translation</h2>
          <button
            type="button"
            class="icon-btn is-borderless"
            aria-label="Close dialog"
            @click="emit('close')"
          >
            <X :size="20" aria-hidden="true" />
          </button>
        </div>

        <form class="modal-body" @submit.prevent="submitJob">
          <div class="form-group">
            <label for="job-input-file">
              <FileAudio :size="16" aria-hidden="true" />
              Input file path
            </label>
            <input
              id="job-input-file"
              v-model="input_file"
              data-autofocus
              type="text"
              class="form-input"
              placeholder="/path/to/audio.wav"
              spellcheck="false"
              autocomplete="off"
              aria-describedby="job-input-file-hint"
            />
            <span id="job-input-file-hint" class="hint">
              Absolute path to a .wav or .mp3 file on the machine running Speakora.
            </span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="job-source-lang">
                <Globe :size="16" aria-hidden="true" />
                Source language
              </label>
              <select id="job-source-lang" v-model="source_lang" class="form-input">
                <option value="auto">Auto-detect</option>
                <option v-for="lang in TARGET_LANGUAGES" :key="lang.code" :value="lang.code">
                  {{ lang.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="job-target-lang">
                <Globe :size="16" aria-hidden="true" />
                Target language
              </label>
              <select id="job-target-lang" v-model="target_lang" class="form-input">
                <option v-for="lang in TARGET_LANGUAGES" :key="lang.code" :value="lang.code">
                  {{ lang.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="job-priority">
              <Zap :size="16" aria-hidden="true" />
              Priority
            </label>
            <input
              id="job-priority"
              v-model.number="priority"
              type="number"
              :min="PRIORITY_MIN"
              :max="PRIORITY_MAX"
              class="form-input"
              aria-describedby="job-priority-hint"
            />
            <span id="job-priority-hint" class="hint">
              Higher values are picked up first ({{ PRIORITY_MIN }}–{{ PRIORITY_MAX }}).
            </span>
          </div>

          <div class="form-group">
            <div class="checkbox-label">
              <input id="job-expressive" v-model="expressive" type="checkbox" />
              <label for="job-expressive">Expressive voice mode</label>
            </div>
            <span class="hint">
              Preserves the speaker's prosody and tone in the translated audio.
            </span>
          </div>

          <div v-if="expressive" class="form-group">
            <label for="job-reference-audio">
              <FileAudio :size="16" aria-hidden="true" />
              Reference audio (optional)
            </label>
            <input
              id="job-reference-audio"
              v-model="reference_audio"
              type="text"
              class="form-input"
              placeholder="/path/to/reference.wav"
              spellcheck="false"
              autocomplete="off"
              aria-describedby="job-reference-audio-hint"
            />
            <span id="job-reference-audio-hint" class="hint">
              Used for voice cloning. Leave empty to use the input file itself.
            </span>
          </div>

          <p v-if="error" class="alert alert-danger" role="alert">
            <AlertCircle :size="18" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="emit('close')">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting" :aria-busy="submitting">
              <span v-if="submitting" class="spinner spinner-sm" aria-hidden="true"></span>
              <Send v-else :size="18" aria-hidden="true" />
              {{ submitting ? 'Submitting…' : 'Submit job' }}
            </button>
          </div>
        </form>
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
  margin-bottom: var(--space-6);
}

.modal-header h2 {
  font-size: var(--text-xl);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr));
  gap: var(--space-4);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

/* The spinner inherits the button's text colour while submitting. */
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
