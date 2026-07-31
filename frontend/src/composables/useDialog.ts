import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

/**
 * Shared modal-dialog behaviour: Escape to close, background scroll lock,
 * initial focus, a simple Tab focus trap and focus restoration on close.
 *
 * Usage:
 *   const { dialogRef } = useDialog(() => props.show, () => emit('close'))
 * and bind `ref="dialogRef"` to the dialog element. Mark the element that
 * should receive initial focus with `data-autofocus`.
 */

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])'
].join(', ')

/** Number of dialogs currently open, so the scroll lock survives stacking. */
let openDialogCount = 0

function lockScroll() {
  openDialogCount += 1
  document.body.style.overflow = 'hidden'
}

function unlockScroll() {
  openDialogCount = Math.max(0, openDialogCount - 1)
  if (openDialogCount === 0) {
    document.body.style.overflow = ''
  }
}

export function useDialog(isOpen: () => boolean, close: () => void) {
  const dialogRef = ref<HTMLElement | null>(null)
  let previouslyFocused: HTMLElement | null = null
  let locked = false

  const focusableElements = () =>
    dialogRef.value
      ? Array.from(dialogRef.value.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
          (el) => el.offsetParent !== null
        )
      : []

  const onKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
      return
    }

    if (event.key !== 'Tab') return

    const focusable = focusableElements()
    if (focusable.length === 0) return

    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }

  const activate = () => {
    previouslyFocused = document.activeElement as HTMLElement | null
    document.addEventListener('keydown', onKeydown)
    lockScroll()
    locked = true

    nextTick(() => {
      const dialog = dialogRef.value
      if (!dialog) return
      const target =
        dialog.querySelector<HTMLElement>('[data-autofocus]') ?? focusableElements()[0] ?? dialog
      target.focus()
    })
  }

  const deactivate = () => {
    document.removeEventListener('keydown', onKeydown)
    if (locked) {
      unlockScroll()
      locked = false
    }
    previouslyFocused?.focus()
    previouslyFocused = null
  }

  watch(isOpen, (open) => (open ? activate() : deactivate()), { immediate: true })
  onBeforeUnmount(deactivate)

  return { dialogRef }
}
