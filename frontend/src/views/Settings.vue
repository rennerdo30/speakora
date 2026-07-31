<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Save, Cpu, Folder, Mic2, ShieldCheck, Zap, AlertTriangle, RefreshCw } from 'lucide-vue-next'
import { TOAST_DURATION_MS } from '../constants'

type ToastType = 'success' | 'error'

const SAMPLE_RATES = [
  { value: 16000, label: '16 kHz (standard)' },
  { value: 24000, label: '24 kHz' },
  { value: 44100, label: '44.1 kHz (high fidelity)' },
  { value: 48000, label: '48 kHz' }
]

const config = ref<any>(null)
const loading = ref(true)
const saving = ref(false)
const loadError = ref('')
const toast = ref<{ text: string; type: ToastType } | null>(null)
let toastTimer: ReturnType<typeof setTimeout> | undefined

const showToast = (text: string, type: ToastType) => {
  clearTimeout(toastTimer)
  toast.value = { text, type }
  toastTimer = setTimeout(() => (toast.value = null), TOAST_DURATION_MS)
}

const fetchConfig = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await axios.get('/api/system/config')
    config.value = res.data
  } catch (err: unknown) {
    console.error('Failed to fetch config', err)
    loadError.value = 'Could not load the configuration. Check that the backend is running.'
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await axios.patch('/api/system/config', config.value)
    showToast('Settings saved.', 'success')
  } catch (err: unknown) {
    console.error('Failed to save config', err)
    showToast('Could not save the settings.', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>

<template>
  <div class="settings-view fade-in">
    <header class="page-header">
      <div>
        <h1>Settings</h1>
        <p class="page-subtitle">Configure translation, audio and system preferences</p>
      </div>
      <button
        type="button"
        class="btn btn-primary"
        :disabled="saving || loading || !config"
        :aria-busy="saving"
        @click="saveConfig"
      >
        <Save :size="18" aria-hidden="true" />
        {{ saving ? 'Saving…' : 'Save settings' }}
      </button>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner" aria-hidden="true"></div>
      <p role="status">Loading configuration…</p>
    </div>

    <div v-else-if="loadError" class="glass-card error-state" role="alert">
      <span class="empty-state-icon"><AlertTriangle :size="22" aria-hidden="true" /></span>
      <p class="empty-state-title">Configuration unavailable</p>
      <p class="empty-state-body">{{ loadError }}</p>
      <button type="button" class="btn btn-secondary" @click="fetchConfig">
        <RefreshCw :size="16" aria-hidden="true" />
        Try again
      </button>
    </div>

    <div v-else-if="config" class="settings-grid">
      <section class="settings-card glass-card" aria-labelledby="settings-model">
        <div class="card-header">
          <Cpu :size="20" class="icon-primary" aria-hidden="true" />
          <h2 id="settings-model">Model</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="model-size">Model size</label>
            <select id="model-size" v-model="config.model.size" class="form-input">
              <option value="small">Small (fastest)</option>
              <option value="medium">Medium</option>
              <option value="large">Large (highest quality)</option>
            </select>
            <span class="hint">Larger models translate better but need more memory.</span>
          </div>
          <div class="form-group">
            <label for="model-device">Device</label>
            <select id="model-device" v-model="config.model.device" class="form-input">
              <option value="auto">Auto-detect</option>
              <option value="cuda">NVIDIA GPU (CUDA)</option>
              <option value="mps">Apple GPU (MPS)</option>
              <option value="cpu">CPU</option>
            </select>
          </div>
          <div class="checkbox-label">
            <input id="model-expressive" v-model="config.model.expressive" type="checkbox" />
            <label for="model-expressive">
              <Zap :size="14" aria-hidden="true" />
              Expressive mode (voice preservation)
            </label>
          </div>
        </div>
      </section>

      <section class="settings-card glass-card" aria-labelledby="settings-audio">
        <div class="card-header">
          <Mic2 :size="20" class="icon-secondary" aria-hidden="true" />
          <h2 id="settings-audio">Audio processing</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="audio-sample-rate">Target sample rate</label>
            <select
              id="audio-sample-rate"
              v-model="config.audio.target_sample_rate"
              class="form-input"
            >
              <option v-for="rate in SAMPLE_RATES" :key="rate.value" :value="rate.value">
                {{ rate.label }}
              </option>
            </select>
          </div>
          <div class="checkbox-label">
            <input id="audio-mono" v-model="config.audio.to_mono" type="checkbox" />
            <label for="audio-mono">Convert to mono</label>
          </div>
          <div class="checkbox-label">
            <input id="audio-normalize" v-model="config.audio.normalize" type="checkbox" />
            <label for="audio-normalize">Normalise volume</label>
          </div>
        </div>
      </section>

      <section class="settings-card glass-card" aria-labelledby="settings-paths">
        <div class="card-header">
          <Folder :size="20" class="icon-accent" aria-hidden="true" />
          <h2 id="settings-paths">Paths &amp; storage</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="paths-input">Input directory</label>
            <input
              id="paths-input"
              v-model="config.paths.input_dir"
              type="text"
              class="form-input"
              spellcheck="false"
            />
          </div>
          <div class="form-group">
            <label for="paths-output">Output directory</label>
            <input
              id="paths-output"
              v-model="config.paths.output_dir"
              type="text"
              class="form-input"
              spellcheck="false"
            />
          </div>
        </div>
      </section>

      <section class="settings-card glass-card" aria-labelledby="settings-advanced">
        <div class="card-header">
          <ShieldCheck :size="20" class="icon-success" aria-hidden="true" />
          <h2 id="settings-advanced">Advanced &amp; logging</h2>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="log-level">Log level</label>
            <select id="log-level" v-model="config.logging.level" class="form-input">
              <option value="DEBUG">Debug (verbose)</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
          <div class="checkbox-label">
            <input
              id="resume-checkpoint"
              v-model="config.processing.resume_from_checkpoint"
              type="checkbox"
            />
            <label for="resume-checkpoint">Resume from checkpoint</label>
          </div>
        </div>
      </section>
    </div>

    <!-- Live region so the save result is announced, not just shown. -->
    <div class="toast-region" role="status" aria-live="polite">
      <p v-if="toast" :class="['toast', toast.type]">{{ toast.text }}</p>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.page-subtitle {
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-md);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
  gap: var(--space-5);
  align-items: start;
}

.settings-card {
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: var(--surface-raised);
  border-bottom: 1px solid var(--border-color);
}

.card-header h2 {
  font-size: var(--text-lg);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: var(--space-5);
}

.icon-primary {
  color: var(--primary-color);
}

.icon-secondary {
  color: var(--secondary-color);
}

.icon-accent {
  color: var(--info-color);
}

.icon-success {
  color: var(--success-color);
}

.checkbox-label label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-md);
  color: var(--text-secondary);
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-16) var(--space-6);
  color: var(--text-muted);
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-12) var(--space-6);
  text-align: center;
  color: var(--text-muted);
}

.toast-region {
  position: fixed;
  right: var(--page-gutter);
  bottom: var(--page-gutter);
  z-index: var(--z-toast);
  pointer-events: none;
}

.toast {
  padding: var(--space-4) var(--space-5);
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-md);
  animation: slideUp var(--duration-base) var(--ease-out);
}

.toast.success {
  border-color: var(--success-color);
  color: var(--success-color);
}

.toast.error {
  border-color: var(--danger-color);
  color: var(--danger-color);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(0.75rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
