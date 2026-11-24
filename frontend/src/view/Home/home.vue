<script setup>
import { computed, onMounted, onUnmounted, provide, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import DefaultTemplate from '../template/default_template/default_template.vue'
import CosmeticTemplate from '../template/cosmetic_template/cosmetic_template.vue'
import CambodiaTemplate from '../template/cambodia_template/cambodia_template.vue'

// Register additional templates here; never import a path supplied by the API.
const templates = new Map([
  ['default_template', DefaultTemplate],
  ['cosmetic_template', CosmeticTemplate],
  ['cambodia_template', CambodiaTemplate],
])

const menu = ref(null)
const loading = ref(true)
const error = ref('')
const needsShop = ref(false)
const isLocal = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
const { t, locale } = useI18n({ useScope: 'global' })
const displayTemplate = computed(() => templates.get(menu.value?.display_template) ?? DefaultTemplate)
const templateState = reactive({ token: '', tenantId: null, slug: '', menuUrl: '', qrUrl: '', busy: false, error: '', status: '' })
const currentTemplate = computed(() => menu.value?.display_template ?? 'default_template')
const hasMenu = computed(() => Boolean(menu.value))

function signOut() {
  if (templateState.qrUrl) URL.revokeObjectURL(templateState.qrUrl)
  Object.assign(templateState, { token: '', tenantId: null, slug: '', menuUrl: '', qrUrl: '', busy: false, error: '', status: '' })
}

async function signIn(email, password) {
  templateState.error = ''
  templateState.status = ''
  if (!window.isSecureContext && !isLocal) {
    templateState.error = 'templateHttpsRequired'
    return false
  }
  templateState.busy = true
  try {
    const login = await fetch('/v1/api/auth/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (login.status === 429) throw new Error('templateRateLimited')
    if (login.status === 401) throw new Error('templateLoginFailed')
    if (!login.ok) throw new Error('templateRequestFailed')
    const { access_token: token } = await login.json()
    const response = await fetch('/v1/api/tenants', { headers: { Authorization: `Bearer ${token}` } })
    if (response.status === 429) throw new Error('templateRateLimited')
    if (!response.ok) throw new Error('templateRequestFailed')
    const tenants = await response.json()
    const tenant = tenants.find((item) => item.slug === menu.value?.slug)
    if (!tenant) throw new Error('templateNoAccess')
    Object.assign(templateState, { token, tenantId: tenant.id, slug: tenant.slug, menuUrl: tenant.menu_url || '' })
    return true
  } catch (cause) {
    const known = ['templateRateLimited', 'templateLoginFailed', 'templateNoAccess', 'templateRequestFailed']
    templateState.error = known.includes(cause.message) ? cause.message : 'templateRequestFailed'
    return false
  } finally {
    templateState.busy = false
  }
}

async function saveTemplate(value) {
  if (!templates.has(value) || !templateState.token || templateState.slug !== menu.value?.slug) return
  templateState.error = ''
  templateState.status = ''
  templateState.busy = true
  try {
    const response = await fetch(`/v1/api/tenants/${templateState.tenantId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${templateState.token}` },
      body: JSON.stringify({ display_template: value }),
    })
    if (response.status === 401) {
      signOut()
      throw new Error('templateSessionExpired')
    }
    if (response.status === 403) throw new Error('templateForbidden')
    if (response.status === 429) throw new Error('templateRateLimited')
    if (!response.ok) throw new Error('templateRequestFailed')
    const tenant = await response.json()
    templateState.status = 'templateSaved'
    menu.value = { ...menu.value, display_template: tenant.display_template }
  } catch (cause) {
    const known = ['templateSessionExpired', 'templateForbidden', 'templateRateLimited', 'templateRequestFailed']
    templateState.error = known.includes(cause.message) ? cause.message : 'templateRequestFailed'
  } finally {
    templateState.busy = false
  }
}

async function showQr() {
  if (!templateState.token || templateState.slug !== menu.value?.slug) return
  templateState.busy = true
  templateState.error = ''
  try {
    const response = await fetch(`/v1/api/tenants/${templateState.tenantId}/qr-code`, {
      headers: { Authorization: `Bearer ${templateState.token}` },
    })
    if (response.status === 401) {
      signOut()
      throw new Error('templateSessionExpired')
    }
    if (response.status === 429) throw new Error('templateRateLimited')
    if (!response.ok) throw new Error('templateRequestFailed')
    const image = await response.blob()
    if (templateState.qrUrl) URL.revokeObjectURL(templateState.qrUrl)
    templateState.qrUrl = URL.createObjectURL(image)
  } catch (cause) {
    const known = ['templateSessionExpired', 'templateRateLimited', 'templateRequestFailed']
    templateState.error = known.includes(cause.message) ? cause.message : 'templateRequestFailed'
  } finally {
    templateState.busy = false
  }
}

provide('templateSettings', { state: templateState, currentTemplate, hasMenu, signIn, signOut, saveTemplate, showQr })

watch([menu, locale], () => {
  if (menu.value) document.title = `${menu.value.name} | ${t('menu')}`
})

async function loadMenu() {
  const slug = new URLSearchParams(window.location.search).get('shop')?.trim()
  if (isLocal && !slug) {
    needsShop.value = true
    loading.value = false
    error.value = ''
    return
  }
  needsShop.value = false
  loading.value = true
  error.value = ''
  try {
    const endpoint = slug ? `/v1/api/public/menus/${encodeURIComponent(slug)}` : '/v1/api/public/menu'
    const response = await fetch(endpoint, { headers: { Accept: 'application/json' } })
    if (response.status === 404) throw new Error('notFound')
    if (!response.ok) throw new Error('loadError')
    menu.value = await response.json()
  } catch (cause) {
    error.value = cause instanceof TypeError ? 'connectionError' : (cause.message === 'notFound' ? 'notFound' : 'loadError')
  } finally {
    loading.value = false
  }
}

function openShop(value) {
  const slug = value.trim()
  if (!slug) return
  if (slug !== menu.value?.slug) signOut()
  const url = new URL(window.location.href)
  url.searchParams.set('shop', slug)
  window.history.replaceState(null, '', url)
  loadMenu()
}

onMounted(loadMenu)
onUnmounted(() => { if (templateState.qrUrl) URL.revokeObjectURL(templateState.qrUrl) })
</script>

<template>
  <component
    :is="displayTemplate"
    :menu="menu"
    :loading="loading"
    :error="error"
    :needs-shop="needsShop"
    :is-local="isLocal"
    @retry="loadMenu"
    @choose-shop="needsShop = true"
    @open-shop="openShop"
  />
</template>
