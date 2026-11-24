<script setup>
import { computed, onMounted, onUnmounted, provide, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import DefaultTemplate from '../template/default_template/default_template.vue'
import CosmeticTemplate from '../template/cosmetic_template/cosmetic_template.vue'
import CambodiaTemplate from '../template/cambodia_template/cambodia_template.vue'
import { api, ApiError } from '../../services/api-services'

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
const apiIsSeparate = Boolean(import.meta.env.VITE_API_ORIGIN)
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
    let login
    try {
      login = await api.login(email, password)
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) throw new Error('templateLoginFailed')
      throw cause
    }
    const token = login.access_token
    const tenants = await api.listTenants(token)
    const tenant = tenants.find((item) => item.slug === menu.value?.slug)
    if (!tenant) throw new Error('templateNoAccess')
    Object.assign(templateState, { token, tenantId: tenant.id, slug: tenant.slug, menuUrl: tenant.menu_url || '' })
    return true
  } catch (cause) {
    const known = ['templateRateLimited', 'templateLoginFailed', 'templateNoAccess', 'templateRequestFailed']
    templateState.error = cause instanceof ApiError && cause.status === 429 ? 'templateRateLimited' : (known.includes(cause.message) ? cause.message : 'templateRequestFailed')
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
    const tenant = await api.updateTemplate(templateState.tenantId, value, templateState.token)
    templateState.status = 'templateSaved'
    menu.value = { ...menu.value, display_template: tenant.display_template }
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 401) {
      signOut()
      templateState.error = 'templateSessionExpired'
    } else if (cause instanceof ApiError && cause.status === 403) templateState.error = 'templateForbidden'
    else if (cause instanceof ApiError && cause.status === 429) templateState.error = 'templateRateLimited'
    else templateState.error = 'templateRequestFailed'
  } finally {
    templateState.busy = false
  }
}

async function showQr() {
  if (!templateState.token || templateState.slug !== menu.value?.slug) return
  templateState.busy = true
  templateState.error = ''
  try {
    const image = await api.getQrCode(templateState.tenantId, templateState.token)
    if (templateState.qrUrl) URL.revokeObjectURL(templateState.qrUrl)
    templateState.qrUrl = URL.createObjectURL(image)
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 401) {
      signOut()
      templateState.error = 'templateSessionExpired'
    } else if (cause instanceof ApiError && cause.status === 429) templateState.error = 'templateRateLimited'
    else templateState.error = 'templateRequestFailed'
  } finally {
    templateState.busy = false
  }
}

provide('templateSettings', { state: templateState, currentTemplate, hasMenu, signIn, signOut, saveTemplate, showQr })

watch([menu, locale], () => {
  if (menu.value) document.title = `${menu.value.name} | ${t('menu')}`
})

async function loadMenu() {
  const requestedSlug = new URLSearchParams(window.location.search).get('shop')?.trim()
  const hostnameMatch = window.location.hostname.toLowerCase().match(/^([a-z0-9-]+)\.sabrey\.xyz$/)
  const slug = requestedSlug || (apiIsSeparate ? hostnameMatch?.[1] : '')
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
    menu.value = await api.getMenu(slug)
  } catch (cause) {
    error.value = cause instanceof TypeError ? 'connectionError' : (cause instanceof ApiError && cause.status === 404 ? 'notFound' : 'loadError')
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
