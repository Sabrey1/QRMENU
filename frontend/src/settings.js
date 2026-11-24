import { ref } from 'vue'

let savedSize
try { savedSize = localStorage.getItem('sabrey-font-size') } catch { /* Storage may be unavailable. */ }

const previousSizes = { normal: 100, large: 115, extraLarge: 125 }
const savedNumber = previousSizes[savedSize] ?? Number(savedSize)
export const fontSize = ref(Number.isFinite(savedNumber) && savedNumber >= 80 && savedNumber <= 150 ? savedNumber : 100)

export function setFontSize(value) {
  const size = Number(value)
  if (!Number.isFinite(size) || size < 80 || size > 150) return
  fontSize.value = size
  document.documentElement.style.setProperty('--menu-font-scale', String(size / 100))
  try { localStorage.setItem('sabrey-font-size', String(size)) } catch { /* Keep the setting for this visit. */ }
}

setFontSize(fontSize.value)

let savedTheme
try { savedTheme = localStorage.getItem('sabrey-theme') } catch { /* Storage may be unavailable. */ }
const themes = ['system', 'light', 'dark']
export const theme = ref(themes.includes(savedTheme) ? savedTheme : 'system')
const colorScheme = window.matchMedia('(prefers-color-scheme: dark)')

function applyTheme() {
  document.documentElement.dataset.theme = theme.value === 'system'
    ? (colorScheme.matches ? 'dark' : 'light')
    : theme.value
}

export function setTheme(value) {
  if (!themes.includes(value)) return
  theme.value = value
  applyTheme()
  try { localStorage.setItem('sabrey-theme', value) } catch { /* Keep the setting for this visit. */ }
}

colorScheme.addEventListener('change', applyTheme)
applyTheme()
