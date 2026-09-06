import { MB_PER_GB } from '../constants'

/**
 * Locale-aware formatting helpers.
 *
 * All helpers use the browser locale (`undefined` locale argument) so numbers,
 * dates and units follow the user's regional settings.
 */

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short'
})

const dateFormatter = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' })

const decimalFormatter = new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 })

const integerFormatter = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })

const gigabyteFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 1,
  maximumFractionDigits: 2
})

/** Placeholder shown when a value is missing. */
export const EMPTY_VALUE = '—'

export function formatDateTime(value: string | number | Date | null | undefined): string {
  if (!value) return EMPTY_VALUE
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? EMPTY_VALUE : dateTimeFormatter.format(date)
}

export function formatDate(value: string | number | Date | null | undefined): string {
  if (!value) return EMPTY_VALUE
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? EMPTY_VALUE : dateFormatter.format(date)
}

/** Milliseconds since epoch, or 0 when the value cannot be parsed. */
export function toTimestamp(value: string | number | Date | null | undefined): number {
  if (!value) return 0
  const time = new Date(value).getTime()
  return Number.isNaN(time) ? 0 : time
}

/** `95s` / `3m 05s` / `1h 04m` */
export function formatDuration(totalSeconds: number | null | undefined): string {
  if (totalSeconds === null || totalSeconds === undefined || Number.isNaN(totalSeconds)) {
    return EMPTY_VALUE
  }

  const seconds = Math.max(0, Math.round(totalSeconds))
  if (seconds < 60) return `${integerFormatter.format(seconds)}s`

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    return `${minutes}m ${String(seconds % 60).padStart(2, '0')}s`
  }

  const hours = Math.floor(minutes / 60)
  return `${hours}h ${String(minutes % 60).padStart(2, '0')}m`
}

/** Megabytes rendered as MB below 1 GB, GB above. */
export function formatMegabytes(megabytes: number | null | undefined): string {
  if (megabytes === null || megabytes === undefined || Number.isNaN(megabytes)) return EMPTY_VALUE
  if (megabytes >= MB_PER_GB) return `${gigabyteFormatter.format(megabytes / MB_PER_GB)} GB`
  return `${integerFormatter.format(megabytes)} MB`
}

export function formatPercent(value: number | null | undefined, fractionDigits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return EMPTY_VALUE
  const formatter = fractionDigits > 0 ? decimalFormatter : integerFormatter
  return `${formatter.format(value)}%`
}

export function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return EMPTY_VALUE
  return integerFormatter.format(value)
}

/** Clamp a raw ratio into a safe 0–100 percentage, guarding against 0/0. */
export function toSafePercent(used: number | null | undefined, total: number | null | undefined) {
  if (!used || !total || total <= 0) return 0
  return Math.min(100, Math.max(0, (used / total) * 100))
}

/** Last path segment of a file path, for compact table cells. */
export function fileNameOf(path: string | null | undefined): string {
  if (!path) return EMPTY_VALUE
  return path.split(/[\\/]/).pop() || path
}
