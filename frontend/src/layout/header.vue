<script setup>
import { useI18n } from 'vue-i18n'
import { inject, onMounted, onUnmounted, ref, watch } from 'vue'
import { setLocale } from '../i18n'
import { fontSize, setFontSize, theme, setTheme } from '../settings'
import LanguageFlag from './language_flag.vue'

const { locale } = useI18n({ useScope: 'global' })
const props = defineProps({
  variant: { type: String, default: 'default' },
  shopName: { type: String, default: '' },
  logoUrl: { type: String, default: '' },
})
const logoFailed = ref(false)
watch(() => props.logoUrl, () => { logoFailed.value = false })
const dropdown = ref(null)
const languageDropdown = ref(null)
const settingsDialog = ref(null)
const templateSettings = inject('templateSettings')
const { state: templateState, currentTemplate, hasMenu, signIn, signOut, saveTemplate, showQr } = templateSettings
const email = ref('')
const password = ref('')
const selectedTemplate = ref('default_template')

function openSettings() {
  dropdown.value.open = false
  if (languageDropdown.value) languageDropdown.value.open = false
  selectedTemplate.value = currentTemplate.value
  settingsDialog.value.showModal()
}

async function submitLogin() {
  await signIn(email.value.trim(), password.value)
  password.value = ''
}

function returnFocus() {
  dropdown.value?.querySelector('summary')?.focus()
}

function selectLanguage(value) {
  setLocale(value)
  languageDropdown.value.open = false
  languageDropdown.value.querySelector('summary').focus()
}

function closeOnOutsideClick(event) {
  if (dropdown.value && !dropdown.value.contains(event.target)) {
    dropdown.value.open = false
    if (languageDropdown.value) languageDropdown.value.open = false
  }
}

function closeOnEscape() {
  if (!dropdown.value?.open) return
  dropdown.value.open = false
  if (languageDropdown.value) languageDropdown.value.open = false
  dropdown.value.querySelector('summary').focus()
}

function closeLanguageOnEscape(event) {
  if (!languageDropdown.value?.open) return
  event.stopPropagation()
  event.preventDefault()
  languageDropdown.value.open = false
  languageDropdown.value.querySelector('summary').focus()
}

onMounted(() => document.addEventListener('pointerdown', closeOnOutsideClick))
onUnmounted(() => document.removeEventListener('pointerdown', closeOnOutsideClick))
</script>

<template>
  <header class="header" :class="{ 'header-cambodia': variant === 'cambodia' }">
    <div class="header-inner">
      <a v-if="variant === 'cambodia' && shopName" href="#top" class="brand shop-brand">
        <img v-if="logoUrl && !logoFailed" class="shop-logo" :src="logoUrl" alt="" @error="logoFailed = true" />
        <span v-else class="shop-avatar" aria-hidden="true">{{ shopName.trim().charAt(0).toUpperCase() }}</span>
        <span class="shop-name">{{ shopName }}</span>
      </a>
      <a v-else href="#top" class="brand">Sabrey<span> {{ $t('menu') }}</span></a>
      <details ref="dropdown" class="settings" @keydown.esc.stop.prevent="closeOnEscape">
        <summary class="settings-button" :aria-label="$t('settings')">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" stroke="currentColor" stroke-width="1.7"/><path d="M19 13.5v-3l-1.8-.6a6 6 0 0 0-.6-1.4l.8-1.7-2.1-2.1-1.7.8a6 6 0 0 0-1.4-.6L11.5 3h-3l-.6 1.9a6 6 0 0 0-1.4.6l-1.7-.8-2.1 2.1.8 1.7a6 6 0 0 0-.6 1.4L1 10.5v3l1.9.6a6 6 0 0 0 .6 1.4l-.8 1.7 2.1 2.1 1.7-.8a6 6 0 0 0 1.4.6l.6 1.9h3l.6-1.9a6 6 0 0 0 1.4-.6l1.7.8 2.1-2.1-.8-1.7a6 6 0 0 0 .6-1.4l1.9-.6Z" stroke="currentColor" stroke-width="1.7" transform="translate(2 0)"/></svg>
        </summary>
        <div class="settings-panel">
          <span class="setting-label">{{ $t('language') }}</span>
          <details ref="languageDropdown" class="language-select" @keydown.esc="closeLanguageOnEscape">
            <summary :aria-label="`${$t('language')}: ${locale === 'km' ? 'ភាសាខ្មែរ' : 'English'}`">
              <LanguageFlag :locale="locale" />
              <span :lang="locale">{{ locale === 'km' ? 'ភាសាខ្មែរ' : 'English' }}</span>
              <svg class="chevron" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m5 7.5 5 5 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </summary>
            <div class="language-options" role="group" :aria-label="$t('language')">
              <button type="button" :class="{ active: locale === 'en' }" :aria-pressed="locale === 'en'" lang="en" @click="selectLanguage('en')"><LanguageFlag locale="en" /> English</button>
              <button type="button" :class="{ active: locale === 'km' }" :aria-pressed="locale === 'km'" lang="km" @click="selectLanguage('km')"><LanguageFlag locale="km" /> ភាសាខ្មែរ</button>
            </div>
          </details>
          <button class="open-settings" type="button" @click="openSettings">{{ $t('settings') }}</button>
        </div>
      </details>
    </div>
    <dialog ref="settingsDialog" class="settings-dialog" aria-labelledby="settings-title" @close="returnFocus">
      <div class="dialog-heading"><h2 id="settings-title">{{ $t('settings') }}</h2><button type="button" class="close-dialog" :aria-label="$t('close')" @click="settingsDialog.close()">×</button></div>
      <div class="appearance-setting">
        <label for="theme-select">{{ $t('appearance') }}</label>
        <select id="theme-select" :value="theme" @change="setTheme($event.target.value)">
          <option value="system">{{ $t('themeSystem') }}</option>
          <option value="light">{{ $t('themeLight') }}</option>
          <option value="dark">{{ $t('themeDark') }}</option>
        </select>
      </div>
      <div class="font-heading"><label for="font-size">{{ $t('fontSize') }}</label><output for="font-size">{{ fontSize }}%</output></div>
      <input id="font-size" class="font-slider" type="range" min="80" max="150" step="5" :value="fontSize" :aria-valuetext="`${fontSize}%`" @input="setFontSize($event.target.value)" />
      <div class="font-limits" aria-hidden="true"><span>80%</span><span>150%</span></div>
      <div v-if="hasMenu" class="template-settings">
        <h3>{{ $t('templateSettings') }}</h3>
        <p v-if="templateState.error" class="template-error" role="alert">{{ $t(templateState.error) }}</p>
        <p v-if="templateState.status" class="template-success" role="status">{{ $t(templateState.status) }}</p>
        <form v-if="!templateState.token" class="login-form" @submit.prevent="submitLogin">
          <p>{{ $t('templateSignInHelp') }}</p>
          <label for="template-email">{{ $t('email') }}</label>
          <input id="template-email" v-model="email" type="email" autocomplete="username" required />
          <label for="template-password">{{ $t('password') }}</label>
          <input id="template-password" v-model="password" type="password" autocomplete="current-password" required />
          <button class="template-action" type="submit" :disabled="templateState.busy">{{ $t(templateState.busy ? 'pleaseWait' : 'signIn') }}</button>
        </form>
        <div v-else class="template-form">
          <label for="display-template">{{ $t('displayTemplate') }}</label>
          <select id="display-template" v-model="selectedTemplate" :disabled="templateState.busy">
            <option value="default_template">{{ $t('defaultTemplate') }}</option>
            <option value="cosmetic_template">{{ $t('cosmeticTemplate') }}</option>
            <option value="cambodia_template">{{ $t('cambodiaTemplate') }}</option>
          </select>
          <div class="template-actions">
            <button class="template-action" type="button" :disabled="templateState.busy || selectedTemplate === currentTemplate" @click="saveTemplate(selectedTemplate)">{{ $t(templateState.busy ? 'pleaseWait' : 'saveTemplate') }}</button>
            <button class="sign-out" type="button" :disabled="templateState.busy" @click="signOut">{{ $t('signOut') }}</button>
          </div>
          <button class="show-qr" type="button" :disabled="templateState.busy" @click="showQr">{{ $t('showQr') }}</button>
          <div v-if="templateState.qrUrl" class="qr-display">
            <img :src="templateState.qrUrl" :alt="$t('menuQr')" />
            <a :href="templateState.menuUrl" target="_blank" rel="noopener noreferrer">{{ templateState.menuUrl }}</a>
            <a :href="templateState.qrUrl" :download="`menu-${templateState.slug}.svg`">{{ $t('downloadQr') }}</a>
          </div>
        </div>
      </div>
    </dialog>
  </header>
</template>

<style scoped>
.header { position: relative; z-index: 20; background: #fff; border-bottom: 1px solid #e5e7eb; }
.header-inner { max-width: 1080px; margin: 0 auto; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.settings { position: relative; }
.settings-button { display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid #d1d5db; border-radius: 6px; color: #374151; background: #fff; cursor: pointer; list-style: none; }
.settings-button::-webkit-details-marker { display: none; }
.settings-button svg { width: 21px; height: 21px; }
.settings-panel { position: absolute; z-index: 6; top: calc(100% + 8px); right: 0; width: min(260px, calc(100vw - 32px)); padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; box-shadow: 0 6px 20px rgb(0 0 0 / 10%); }
.setting-label { display: block; margin: 0 0 7px; color: #374151; font-size: .875rem; font-weight: 600; }
.settings-button:focus-visible, .font-slider:focus-visible { outline: 3px solid #d59d5e; outline-offset: 3px; }
.open-settings { width: 100%; margin-top: 12px; padding: 10px; border: 0; border-radius: 6px; text-align: left; color: #374151; background: #f3f4f6; font: inherit; font-size: .875rem; cursor: pointer; }
.settings-dialog { position: fixed; inset: 0; margin: auto; width: min(400px, calc(100vw - 32px)); height: fit-content; max-height: calc(100dvh - 32px); overflow-y: auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px; color: #1f2937; background: white; box-shadow: 0 15px 40px rgb(0 0 0 / 18%); }
.settings-dialog::backdrop { background: rgb(0 0 0 / 40%); }
.dialog-heading, .font-heading, .font-limits { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.dialog-heading h2 { margin: 0; font-size: 1.125rem; font-weight: 700; }
.close-dialog { width: 36px; height: 36px; border: 0; border-radius: 6px; color: #374151; background: #f3f4f6; font-size: 1.5rem; cursor: pointer; }
.font-heading { margin-top: 24px; font-size: .9375rem; font-weight: 600; }
.appearance-setting { display: grid; gap: 8px; margin-top: 20px; font-size: .9375rem; font-weight: 600; }
.appearance-setting select { width: 100%; padding: 9px 10px; border: 1px solid #d1d5db; border-radius: 6px; color: #1f2937; background: #fff; font: inherit; font-weight: 400; }
.font-slider { width: 100%; margin: 20px 0 8px; accent-color: #285a42; cursor: pointer; }
.font-limits { color: #6b7280; font-size: .75rem; }
.template-settings { margin-top: 24px; padding-top: 20px; border-top: 1px solid #e5e7eb; }
.template-settings h3 { margin: 0 0 10px; font-size: 1rem; font-weight: 700; }
.template-settings p { margin: 0 0 12px; color: #6b7280; font-size: .875rem; line-height: 1.5; }
.template-settings .template-error { color: #b42318; }.template-settings .template-success { color: #285a42; }
.login-form, .template-form { display: grid; gap: 8px; }
.login-form label, .template-form label { color: #374151; font-size: .875rem; font-weight: 600; }
.login-form input, .template-form select { width: 100%; padding: 9px 10px; border: 1px solid #d1d5db; border-radius: 6px; color: #1f2937; background: #fff; font: inherit; font-size: .875rem; }
.template-actions { display: flex; gap: 10px; margin-top: 4px; }
.template-action, .sign-out { padding: 9px 14px; border: 1px solid #285a42; border-radius: 6px; color: #fff; background: #285a42; font: inherit; font-size: .875rem; font-weight: 600; cursor: pointer; }
.template-action:disabled, .sign-out:disabled { opacity: .55; cursor: not-allowed; }
.sign-out { color: #285a42; background: #fff; }
.show-qr { margin-top: 8px; padding: 9px 14px; border: 1px solid #d1d5db; border-radius: 6px; color: #374151; background: #fff; font: inherit; font-size: .875rem; font-weight: 600; cursor: pointer; }
.show-qr:disabled { opacity: .55; cursor: not-allowed; }
.qr-display { display: grid; justify-items: center; gap: 8px; margin-top: 8px; text-align: center; font-size: .875rem; overflow-wrap: anywhere; }
.qr-display img { display: block; width: min(220px, 100%); padding: 8px; border-radius: 6px; background: #fff; }
.qr-display a { color: #285a42; text-decoration: underline; }
.language-select { position: relative; }
.language-select summary { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border: 1px solid #d1d5db; border-radius: 6px; color: #374151; font-size: .875rem; cursor: pointer; list-style: none; }
.language-select summary .chevron { margin-left: auto; }
.language-select summary::-webkit-details-marker { display: none; }
.language-select summary:focus-visible { outline: 3px solid #d59d5e; outline-offset: 3px; }
.chevron { width: 16px; height: 16px; }
.language-options { position: absolute; z-index: 5; top: calc(100% + 6px); right: 0; min-width: 160px; padding: 4px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; box-shadow: 0 6px 20px rgb(0 0 0 / 10%); }
.language-select button { display: flex; width: 100%; align-items: center; gap: 8px; padding: 9px 10px; border: 1px solid transparent; border-radius: 6px; color: #4b5563; background: transparent; font: inherit; font-size: .875rem; text-align: left; cursor: pointer; }
.language-select button:hover { background: #f3f4f6; }
.language-select button.active { color: #285a42; border-color: #c7d9cb; background: #edf5ee; font-weight: 600; }
@media (max-width: 380px) { .header-inner { padding: 16px; gap: 8px; } }
.brand { color: #18211b; font-size: 1.125rem; font-weight: 700; text-decoration: none; }
.brand span { color: #637069; font-weight: 400; }
.header-cambodia { position: relative; overflow: visible; border-bottom: 1px solid #ecd9b8; background: #fff3d8; }
.header-cambodia .header-inner { position: relative; overflow: visible; min-height: 76px; }
.header-cambodia .shop-brand { position: relative; z-index: 1; display: flex; align-items: center; gap: 10px; min-width: 0; }
.header-cambodia .shop-logo, .header-cambodia .shop-avatar { width: 42px; height: 42px; flex-shrink: 0; border: 2px solid #fff; border-radius: 50%; }
.header-cambodia .shop-logo { object-fit: cover; }
.header-cambodia .shop-avatar { display: grid; place-items: center; color: #fff; background: #a04d31; font-weight: 700; }
.header-cambodia .shop-name { overflow: hidden; color: #70432b; font-size: 1rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.header-cambodia .settings { z-index: 2; flex-shrink: 0; }
.header-cambodia .settings-button { color: #80502e; border-color: #d8b781; background: #fffaf0; }
html[data-theme='dark'] .header, html[data-theme='dark'] .header-cambodia { color: #edf1ed; background: #1c2521; border-color: #37443b; }
html[data-theme='dark'] .brand, html[data-theme='dark'] .header-cambodia .shop-name { color: #f1ede1; }
html[data-theme='dark'] .brand span { color: #b4c1b6; }
html[data-theme='dark'] .settings-button, html[data-theme='dark'] .header-cambodia .settings-button { color: #f1ede1; background: #28332d; border-color: #526354; }
html[data-theme='dark'] .settings-panel, html[data-theme='dark'] .settings-dialog, html[data-theme='dark'] .language-options { color: #edf1ed; background: #202b25; border-color: #435449; }
html[data-theme='dark'] .setting-label, html[data-theme='dark'] .dialog-heading h2, html[data-theme='dark'] .login-form label, html[data-theme='dark'] .template-form label { color: #e2e9e2; }
html[data-theme='dark'] .language-select summary, html[data-theme='dark'] .language-select button { color: #e3ebe3; }
html[data-theme='dark'] .language-select summary, html[data-theme='dark'] .login-form input, html[data-theme='dark'] .template-form select, html[data-theme='dark'] .appearance-setting select { color: #edf1ed; background: #17211b; border-color: #526354; }
html[data-theme='dark'] .language-select button:hover, html[data-theme='dark'] .open-settings, html[data-theme='dark'] .close-dialog { color: #edf1ed; background: #334239; }
html[data-theme='dark'] .language-select button.active { color: #d1efda; background: #354f3c; border-color: #668773; }
html[data-theme='dark'] .font-limits, html[data-theme='dark'] .template-settings p { color: #c0ccc2; }
html[data-theme='dark'] .template-settings { border-color: #435449; }
html[data-theme='dark'] .template-settings .template-error { color: #ffa8a0; }
html[data-theme='dark'] .template-settings .template-success { color: #a7dfb5; }
html[data-theme='dark'] .sign-out { color: #d4ead9; background: #24352a; border-color: #72967b; }
html[data-theme='dark'] .show-qr { color: #e3ebe3; background: #24352a; border-color: #72967b; }
html[data-theme='dark'] .qr-display a { color: #b4e5be; }
html[data-theme='dark'] .font-slider { accent-color: #92c79e; }
</style>
