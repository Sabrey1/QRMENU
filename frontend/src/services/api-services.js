const API_ORIGIN = (import.meta.env?.VITE_API_ORIGIN || '').replace(/\/$/, '')
const API_BASE = `${API_ORIGIN}/v1/api`

export class ApiError extends Error {
  constructor(status, retryAfter = null) {
    super(`API request failed (${status})`)
    this.name = 'ApiError'
    this.status = status
    this.retryAfter = retryAfter
  }
}

// An optional API origin supports a frontend hosted separately from FastAPI.
export async function apiRequest(path, { method = 'GET', token, body, responseType = 'json', signal } = {}) {
  if (!path.startsWith('/') || path.startsWith('//')) throw new TypeError('API path must start with a single slash')
  const headers = { Accept: responseType === 'blob' ? 'image/svg+xml' : 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    ...(signal ? { signal } : {}),
  })
  if (!response.ok) throw new ApiError(response.status, response.headers.get('Retry-After'))
  if (response.status === 204) return null
  return responseType === 'blob' ? response.blob() : response.json()
}

export const api = {
  getMenu(slug) {
    return apiRequest(slug ? `/public/menus/${encodeURIComponent(slug)}` : '/public/menu')
  },
  register(data) {
    return apiRequest('/auth/register', { method: 'POST', body: data })
  },
  login(email, password) {
    return apiRequest('/auth/login', { method: 'POST', body: { email, password } })
  },
  listTenants(token) {
    return apiRequest('/tenants', { token })
  },
  updateTemplate(tenantId, displayTemplate, token) {
    return apiRequest(`/tenants/${encodeURIComponent(tenantId)}`, {
      method: 'PATCH', token, body: { display_template: displayTemplate },
    })
  },
  getQrCode(tenantId, token) {
    return apiRequest(`/tenants/${encodeURIComponent(tenantId)}/qr-code`, { token, responseType: 'blob' })
  },
}
