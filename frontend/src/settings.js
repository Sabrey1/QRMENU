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

const layoutFields = {
  columns: { min: 1, max: 4, property: '--menu-columns', unit: '' },
  cardWidth: { min: 80, max: 1200, property: '--menu-card-width', unit: 'px' },
  cardHeight: { min: 80, max: 1200, property: '--menu-card-height', unit: 'px' },
  imageWidth: { min: 20, max: 1200, property: '--menu-image-width', unit: 'px' },
  imageHeight: { min: 20, max: 1200, property: '--menu-image-height', unit: 'px' },
}

let savedLayout = {}
try { savedLayout = JSON.parse(localStorage.getItem('sabrey-menu-layout') || '{}') || {} } catch { /* Use the template defaults. */ }
export const menuLayout = ref(Object.fromEntries(Object.keys(layoutFields).map((key) => [key, ''])))

export function setMenuLayout(key, value) {
  const field = layoutFields[key]
  if (!field) return
  const number = Number(value)
  if (value !== '' && (!Number.isInteger(number) || number < field.min || number > field.max)) return
  menuLayout.value[key] = value === '' ? '' : number
  if (value === '') document.documentElement.style.removeProperty(field.property)
  else document.documentElement.style.setProperty(field.property, `${number}${field.unit}`)
  try { localStorage.setItem('sabrey-menu-layout', JSON.stringify(menuLayout.value)) } catch { /* Keep the setting for this visit. */ }
}

for (const key of Object.keys(layoutFields)) setMenuLayout(key, savedLayout[key] ?? '')

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
