<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Save, RefreshCw, Cpu, Folder, Radio, Mic2, ShieldCheck, Zap } from 'lucide-vue-next'

const config = ref<any>(null)
const loading = ref(true)
const saving = ref(false)
const message = ref({ text: '', type: '' })

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/system/config')
    config.value = res.data
  } catch (err) {
    console.error('Failed to fetch config', err)
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  message.value = { text: '', type: '' }
  try {
    await axios.patch('/api/system/config', config.value)
    message.value = { text: 'Settings saved successfully!', type: 'success' }
    setTimeout(() => { message.value = { text: '', type: '' } }, 3000)
  } catch (err) {
    message.value = { text: 'Failed to save settings.', type: 'error' }
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>

<template>
  <div class="settings-view fade-in">
    <header class="header">
      <div class="header-content">
        <h1>Settings</h1>
        <p class="text-secondary">Configure your translation and system preferences</p>
      </div>
      <button class="btn btn-primary" @click="saveConfig" :disabled="saving">
        <Save :size="18" />
        {{ saving ? 'Saving...' : 'Save Settings' }}
      </button>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="config" class="settings-grid">
      <!-- Model Settings -->
      <section class="settings-card glass-card">
        <div class="card-header">
          <Cpu :size="20" class="icon-primary" />
          <h3>Model Configuration</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Model Size</label>
            <select v-model="config.model.size" class="form-input">
              <option value="small">Small (Fast)</option>
              <option value="medium">Medium</option>
              <option value="large">Large (High Quality)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Device</label>
            <select v-model="config.model.device" class="form-input">
              <option value="auto">Auto-detect</option>
              <option value="cuda">NVIDIA GPU (CUDA)</option>
              <option value="mps">Mac GPU (MPS)</option>
              <option value="cpu">CPU</option>
            </select>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" v-model="config.model.expressive" id="expressive" />
            <label for="expressive">
              <Zap :size="14" />
              Expressive Mode (Voice Preservation)
            </label>
          </div>
        </div>
      </section>

      <!-- Audio Settings -->
      <section class="settings-card glass-card">
        <div class="card-header">
          <Mic2 :size="20" class="icon-secondary" />
          <h3>Audio Processing</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Target Sample Rate (Hz)</label>
            <select v-model="config.audio.target_sample_rate" class="form-input">
              <option :value="16000">16,000 (Standard)</option>
              <option :value="24000">24,000</option>
              <option :value="44100">44,100 (High Fidelity)</option>
              <option :value="48000">48,000</option>
            </select>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" v-model="config.audio.to_mono" id="to_mono" />
            <label for="to_mono">Convert to Mono</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" v-model="config.audio.normalize" id="normalize" />
            <label for="normalize">Normalize Volume</label>
          </div>
        </div>
      </section>

      <!-- Path Settings -->
      <section class="settings-card glass-card">
        <div class="card-header">
          <Folder :size="20" class="icon-accent" />
          <h3>Paths & Storage</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Input Directory</label>
            <input type="text" v-model="config.paths.input_dir" class="form-input" />
          </div>
          <div class="form-group">
            <label>Output Directory</label>
            <input type="text" v-model="config.paths.output_dir" class="form-input" />
          </div>
        </div>
      </section>

      <!-- Logging & Advanced -->
      <section class="settings-card glass-card">
        <div class="card-header">
          <ShieldCheck :size="20" class="icon-success" />
          <h3>Advanced & Logging</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Log Level</label>
            <select v-model="config.logging.level" class="form-input">
              <option value="DEBUG">Debug (Verbose)</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" v-model="config.processing.resume_from_checkpoint" id="resume" />
            <label for="resume">Resume from Checkpoint</label>
          </div>
        </div>
      </section>
    </div>

    <div v-if="message.text" :class="['floating-message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<style scoped>
.settings-view { padding: 10px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.settings-card { padding: 0; overflow: hidden; }
.card-header {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 12px;
}
.card-header h3 { font-size: 1rem; margin: 0; }
.card-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }

.icon-primary { color: var(--primary-color); }
.icon-secondary { color: var(--secondary-color); }
.icon-accent { color: var(--accent-color); }
.icon-success { color: #10b981; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.8125rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.form-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 14px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.9375rem;
}

.checkbox-group { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.checkbox-group input { width: 16px; height: 16px; cursor: pointer; }
.checkbox-group label { display: flex; align-items: center; gap: 8px; font-size: 0.9375rem; color: var(--text-secondary); cursor: pointer; }

.floating-message {
  position: fixed;
  bottom: 40px;
  right: 40px;
  padding: 16px 24px;
  border-radius: 12px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  z-index: 2000;
  animation: slideUp 0.3s ease-out;
}
.floating-message.success { border-color: #10b981; color: #34d399; }
.floating-message.error { border-color: #ef4444; color: #f87171; }

@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes spin { to { transform: rotate(360deg); } }
.spinner { width: 40px; height: 40px; border: 3px solid var(--border-color); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 60px auto; }
</style>
