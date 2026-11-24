import { ref } from 'vue'
import { api, ApiError } from './api-services.js'

const storageKey = 'sabrey-admin-token'
let savedToken = ''
try { savedToken = sessionStorage.getItem(storageKey) || '' } catch { /* Use an in-memory session. */ }
export const adminToken = ref(savedToken)
export const adminUser = ref(null)

export function setAdminSession(token) {
  adminToken.value = token
  adminUser.value = null
  try {
    if (token) sessionStorage.setItem(storageKey, token)
    else sessionStorage.removeItem(storageKey)
  } catch { /* Use an in-memory session. */ }
}

export async function validateAdminSession() {
  if (!adminToken.value) return false
  if (adminUser.value) return true
  const token = adminToken.value
  try {
    const user = await api.getCurrentUser(token)
    if (adminToken.value !== token) return false
    adminUser.value = user
    return true
  } catch (error) {
    if (error instanceof ApiError && error.status === 401 && adminToken.value === token) setAdminSession('')
    throw error
  }
}

export function safeAdminRedirect(value) {
  return typeof value === 'string' && /^\/admin(?:\/|\?|$)/.test(value) && !value.startsWith('//') ? value : '/admin/banner'
}

export async function adminGuard(to) {
  if (!to.meta.requiresAuth) return true
  try {
    if (await validateAdminSession()) return true
    return { path: '/login', query: { redirect: to.fullPath } }
  } catch (error) {
    return { path: '/login', query: { redirect: to.fullPath, ...(error instanceof ApiError && error.status === 401 ? {} : { sessionError: '1' }) } }
  }
}
