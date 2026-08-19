<script setup lang="ts">
import { ref } from 'vue'
import Dashboard from './views/Dashboard.vue'
import HistoryView from './views/History.vue'
import SettingsView from './views/Settings.vue'
import {
  LayoutDashboard,
  History,
  Settings,
  Download,
  Github,
  Sun,
  Moon,
  type Icon
} from 'lucide-vue-next'
import DownloadModelModal from './components/DownloadModelModal.vue'
import { useTheme } from './composables/useTheme'
import { PROJECT_REPO_URL } from './constants'

type ViewId = 'dashboard' | 'history' | 'settings'

const NAV_ITEMS: { id: ViewId; label: string; icon: Icon }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'history', label: 'History', icon: History },
  { id: 'settings', label: 'Settings', icon: Settings }
]

const ICON_SIZE = 20

const activeView = ref<ViewId>('dashboard')
const showDownloadModal = ref(false)

const { theme, toggleTheme } = useTheme()
</script>

<template>
  <div class="app-shell">
    <a class="skip-link" href="#main-content">Skip to main content</a>

    <aside class="sidebar glass-panel">
      <div class="sidebar-brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" width="22" height="22">
            <path
              d="M6 8h14a4 4 0 014 4v6a4 4 0 01-4 4H12l-4 4v-4H6a4 4 0 01-4-4v-6a4 4 0 014-4z"
              stroke="currentColor"
              stroke-width="2"
            />
            <circle cx="9" cy="15" r="1.5" fill="currentColor" />
            <circle cx="14" cy="15" r="1.5" fill="currentColor" />
            <circle cx="19" cy="15" r="1.5" fill="currentColor" />
          </svg>
        </span>
        <span class="brand-name">Speakora</span>
      </div>

      <nav class="sidebar-nav" aria-label="Main">
        <ul class="nav-list">
          <li v-for="item in NAV_ITEMS" :key="item.id">
            <button
              type="button"
              class="nav-link"
              :class="{ 'is-active': activeView === item.id }"
              :aria-current="activeView === item.id ? 'page' : undefined"
              :aria-label="item.label"
              @click="activeView = item.id"
            >
              <component :is="item.icon" :size="ICON_SIZE" aria-hidden="true" />
              <span class="nav-label">{{ item.label }}</span>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="nav-link"
              aria-haspopup="dialog"
              aria-label="Download models"
              @click="showDownloadModal = true"
            >
              <Download :size="ICON_SIZE" aria-hidden="true" />
              <span class="nav-label">Download models</span>
            </button>
          </li>
        </ul>
      </nav>

      <div class="sidebar-footer">
        <button
          type="button"
          class="nav-link"
          :aria-label="theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'"
          @click="toggleTheme"
        >
          <Sun v-if="theme === 'dark'" :size="ICON_SIZE" aria-hidden="true" />
          <Moon v-else :size="ICON_SIZE" aria-hidden="true" />
          <span class="nav-label">{{ theme === 'dark' ? 'Light theme' : 'Dark theme' }}</span>
        </button>
        <a
          class="nav-link"
          :href="PROJECT_REPO_URL"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Documentation and source on GitHub (opens in a new tab)"
        >
          <Github :size="ICON_SIZE" aria-hidden="true" />
          <span class="nav-label">Help &amp; source</span>
        </a>
      </div>
    </aside>

    <main id="main-content" class="main-content">
      <div class="main-inner">
        <Dashboard v-if="activeView === 'dashboard'" />
        <HistoryView v-else-if="activeView === 'history'" />
        <SettingsView v-else />
      </div>
    </main>

    <DownloadModelModal :show="showDownloadModal" @close="showDownloadModal = false" />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  align-items: flex-start;
  gap: var(--page-gutter);
  min-height: 100vh;
  padding: var(--page-gutter);
  background: var(--app-bg-gradient);
  background-attachment: fixed;
}

.sidebar {
  position: sticky;
  top: var(--page-gutter);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  width: var(--sidebar-width);
  flex-shrink: 0;
  max-height: calc(100vh - var(--page-gutter) * 2);
  padding: var(--space-6) var(--space-4);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-inline: var(--space-2);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  background: var(--brand-gradient);
  color: var(--text-on-brand);
}

.brand-name {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  letter-spacing: -0.01em;
}

.sidebar-nav {
  flex-grow: 1;
  min-width: 0;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  list-style: none;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-md);
  font-weight: var(--weight-medium);
  text-align: left;
  text-decoration: none;
  transition: var(--transition-colors);
}

.nav-link:hover {
  background: var(--overlay-hover);
  color: var(--text-primary);
}

.nav-link:active {
  background: var(--surface-hover);
}

.nav-link.is-active {
  background: var(--primary-soft);
  border-color: var(--primary-soft);
  color: var(--primary-color);
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.main-content {
  flex-grow: 1;
  min-width: 0;
}

.main-inner {
  max-width: var(--layout-max-width);
  margin-inline: auto;
}

/* Tablet and below: the sidebar becomes a sticky top bar. */
@media (max-width: 900px) {
  .app-shell {
    flex-direction: column;
    gap: var(--space-4);
    padding-top: var(--space-3);
  }

  .sidebar {
    position: sticky;
    top: var(--space-3);
    z-index: var(--z-sticky);
    flex-direction: row;
    align-items: center;
    gap: var(--space-4);
    width: 100%;
    max-height: none;
    padding: var(--space-2) var(--space-3);
    overflow-x: auto;
  }

  .sidebar-brand {
    padding-inline: var(--space-1);
  }

  .brand-name {
    font-size: var(--text-lg);
  }

  .nav-list,
  .sidebar-footer {
    flex-direction: row;
    align-items: center;
  }

  .sidebar-footer {
    padding-top: 0;
    padding-left: var(--space-3);
    border-top: none;
    border-left: 1px solid var(--border-color);
  }

  .nav-link {
    width: auto;
    padding: var(--space-2) var(--space-3);
  }
}

/* Phones: icon-only navigation (each control keeps its aria-label). */
@media (max-width: 620px) {
  .nav-label {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }

  .brand-name {
    display: none;
  }

  .sidebar {
    gap: var(--space-2);
  }
}
</style>
