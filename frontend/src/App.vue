<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Dashboard from './views/Dashboard.vue'
import { LayoutDashboard, History, Settings, Info } from 'lucide-vue-next'

const activeView = ref('dashboard')
</script>

<template>
  <div class="app-container">
    <aside class="sidebar glass-card">
      <div class="logo">
        <div class="logo-icon">S2ST</div>
        <span class="logo-text">Translator</span>
      </div>
      <nav class="nav-links">
        <a @click="activeView = 'dashboard'" :class="{ active: activeView === 'dashboard' }">
          <LayoutDashboard :size="20" />
          Dashboard
        </a>
        <a @click="activeView = 'history'" :class="{ active: activeView === 'history' }">
          <History :size="20" />
          History
        </a>
        <a @click="activeView = 'settings'" :class="{ active: activeView === 'settings' }">
          <Settings :size="20" />
          Settings
        </a>
      </nav>
      <div class="sidebar-footer">
        <a href="#">
          <Info :size="20" />
          Help & Info
        </a>
      </div>
    </aside>

    <main class="main-content">
      <Dashboard v-if="activeView === 'dashboard'" />
      <div v-else class="placeholder-view glass-card fade-in">
        <h2>{{ activeView.charAt(0).toUpperCase() + activeView.slice(1) }}</h2>
        <p>This view is coming soon in Phase 2/3.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  padding: 20px;
  gap: 20px;
  background: radial-gradient(circle at top right, #1a1a2e, #0d0d0d);
}

.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
  padding-left: 8px;
}

.logo-icon {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-family: 'Outfit', sans-serif;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  font-family: 'Outfit', sans-serif;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-grow: 1;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-links a:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.nav-links a.active {
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-color);
  font-weight: 500;
}

.sidebar-footer {
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.sidebar-footer a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.placeholder-view {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}

.placeholder-view h2 {
  margin-bottom: 12px;
}

.placeholder-view p {
  color: var(--text-secondary);
}
</style>
