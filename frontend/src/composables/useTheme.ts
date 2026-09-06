import { ref, readonly } from 'vue'

/**
 * Light/dark theme handling.
 *
 * The resolved theme is written to `<html data-theme="…">`; all colours are
 * CSS custom properties keyed off that attribute (see `src/index.css`).
 *
 * `index.html` contains a tiny inline bootstrap that applies the stored or
 * system theme before first paint. It must use the same storage key and
 * attribute name as this module.
 */

export const THEME_STORAGE_KEY = 'speakora:theme'
export const THEME_ATTRIBUTE = 'data-theme'

export type Theme = 'light' | 'dark'

const prefersLight = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: light)').matches

const readStoredTheme = (): Theme | null => {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    return stored === 'light' || stored === 'dark' ? stored : null
  } catch {
    // Private-browsing modes can throw on storage access; fall back to system.
    return null
  }
}

const resolveInitialTheme = (): Theme => readStoredTheme() ?? (prefersLight() ? 'light' : 'dark')

// Module-level state so every component shares a single source of truth.
const theme = ref<Theme>(resolveInitialTheme())

const applyTheme = (next: Theme) => {
  theme.value = next
  document.documentElement.setAttribute(THEME_ATTRIBUTE, next)
}

/** Whether the user has expressed an explicit preference. */
const hasExplicitPreference = ref(readStoredTheme() !== null)

// Follow the operating system until the user picks a theme themselves.
if (typeof window !== 'undefined' && window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (event) => {
    if (!hasExplicitPreference.value) {
      applyTheme(event.matches ? 'light' : 'dark')
    }
  })
}

export function useTheme() {
  const setTheme = (next: Theme) => {
    applyTheme(next)
    hasExplicitPreference.value = true
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next)
    } catch {
      // Persisting the choice is best-effort only.
    }
  }

  const toggleTheme = () => setTheme(theme.value === 'dark' ? 'light' : 'dark')

  // Make sure the attribute matches the reactive state on first use.
  applyTheme(theme.value)

  return { theme: readonly(theme), setTheme, toggleTheme }
}
