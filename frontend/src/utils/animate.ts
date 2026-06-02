/**
 * Number animation utility — count-up from 0 to target
 * Uses requestAnimationFrame for smooth 60fps animation.
 * Usage: animateNumber(el, 0, 5630, 1200) — counts 0→5,630 over 1.2s
 */

export interface AnimateNumberOptions {
  /** Animation duration in ms (default 1000) */
  duration?: number
  /** Easing function (default easeOutCubic) */
  easing?: (t: number) => number
  /** Thousands separator (default ',') */
  separator?: string
  /** Decimal places (default 0 for integers) */
  decimals?: number
  /** Optional prefix (e.g. '¥') */
  prefix?: string
  /** Optional suffix (e.g. '%') */
  suffix?: string
  /** Callback on completion */
  onComplete?: () => void
}

const EASINGS = {
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeOutQuart: (t: number) => 1 - Math.pow(1 - t, 4),
  easeOutExpo: (t: number) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  easeOutBack: (t: number) => {
    const c1 = 1.70158
    const c3 = c1 + 1
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2)
  },
  linear: (t: number) => t,
}

export function animateNumber(
  el: HTMLElement,
  from: number,
  to: number,
  options: AnimateNumberOptions = {},
) {
  const {
    duration = 1000,
    easing = EASINGS.easeOutCubic,
    separator = ',',
    decimals = 0,
    prefix = '',
    suffix = '',
    onComplete,
  } = options

  if (!el) return

  const start = performance.now()
  const range = to - from

  function formatValue(v: number): string {
    const fixed = v.toFixed(decimals)
    const [intPart, decPart] = fixed.split('.')
    const formatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, separator)
    return prefix + formatted + (decPart ? '.' + decPart : '') + suffix
  }

  function tick(now: number) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const easedProgress = easing(progress)
    const current = from + range * easedProgress

    el.textContent = formatValue(current)

    if (progress < 1) {
      requestAnimationFrame(tick)
    } else {
      el.textContent = formatValue(to)
      onComplete?.()
    }
  }

  el.textContent = formatValue(from)
  requestAnimationFrame(tick)
}

/**
 * Shorthand: animate the textContent of an element to a number.
 * Finds the element by querySelector within a container.
 */
export function countUp(
  container: HTMLElement | null,
  selector: string,
  to: number,
  options?: AnimateNumberOptions,
) {
  if (!container) return
  const el = container.querySelector(selector) as HTMLElement | null
  if (!el) return
  animateNumber(el, 0, to, options)
}
