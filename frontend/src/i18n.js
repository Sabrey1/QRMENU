import { createI18n } from 'vue-i18n'
import en from './locals/en.json'
import km from './locals/km.json'

let savedLocale
try { savedLocale = localStorage.getItem('sabrey-locale') } catch { /* Storage may be unavailable. */ }

export const i18n = createI18n({
  legacy: false,
  locale: ['en', 'km'].includes(savedLocale) ? savedLocale : 'en',
  fallbackLocale: 'en',
  messages: { en, km },
})

export function setLocale(locale) {
  if (!['en', 'km'].includes(locale)) return
  i18n.global.locale.value = locale
  document.documentElement.lang = locale
  try { localStorage.setItem('sabrey-locale', locale) } catch { /* Language still works for this visit. */ }
}

document.documentElement.lang = i18n.global.locale.value
