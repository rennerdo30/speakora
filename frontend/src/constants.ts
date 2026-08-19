/**
 * Shared, non-visual constants for the Speakora dashboard.
 *
 * Visual constants (colours, spacing, radii, durations) live as CSS custom
 * properties in `src/index.css`.
 */

/** Poll intervals, in milliseconds. */
export const JOB_LIST_POLL_MS = 3_000
export const SYSTEM_STATUS_POLL_MS = 5_000
export const JOB_LOG_POLL_MS = 2_000

/** How long transient toasts stay on screen, in milliseconds. */
export const TOAST_DURATION_MS = 3_000

/** Delay before a successful model download closes its modal, in milliseconds. */
export const MODAL_AUTO_CLOSE_MS = 2_000

/** Rows per page in the history table. */
export const HISTORY_PAGE_SIZE = 15

/** Job statuses that are still in flight and therefore worth polling. */
export const ACTIVE_JOB_STATUSES = ['queued', 'running', 'paused'] as const

/** Job statuses that will never change again. */
export const TERMINAL_JOB_STATUSES = ['completed', 'failed', 'cancelled'] as const

/** Utilisation thresholds (percent) used to colour the system meters. */
export const METER_WARNING_PERCENT = 75
export const METER_DANGER_PERCENT = 90

/** Number of placeholder rows rendered while a table is loading. */
export const SKELETON_ROW_COUNT = 4

/** Bytes per megabyte / megabytes per gigabyte, for human-readable sizes. */
export const MB_PER_GB = 1024

/** Project home, linked from the sidebar. */
export const PROJECT_REPO_URL = 'https://github.com/rennerdo30/speakora'

/** Target languages offered when creating a job (ISO 639-3 codes). */
export const TARGET_LANGUAGES = [
  { code: 'eng', name: 'English' },
  { code: 'deu', name: 'German' },
  { code: 'fra', name: 'French' },
  { code: 'spa', name: 'Spanish' },
  { code: 'ita', name: 'Italian' },
  { code: 'jpn', name: 'Japanese' },
  { code: 'kor', name: 'Korean' },
  { code: 'rus', name: 'Russian' },
  { code: 'zho', name: 'Chinese' }
] as const
