import test from 'node:test'
import assert from 'node:assert/strict'
import { api, apiRequest, ApiError } from '../src/services/api-services.js'

test('menu requests use same-origin URLs and encode shop slugs', async (t) => {
  const previousFetch = globalThis.fetch
  t.after(() => { globalThis.fetch = previousFetch })
  const calls = []
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })
    return new Response(JSON.stringify({ name: 'Shop' }), { status: 200, headers: { 'Content-Type': 'application/json' } })
  }
  assert.deepEqual(await api.getMenu(), { name: 'Shop' })
  await api.getMenu('shop/name')
  assert.equal(calls[0].url, '/v1/api/public/menu')
  assert.equal(calls[1].url, '/v1/api/public/menus/shop%2Fname')
  assert.equal(calls[0].options.headers.Accept, 'application/json')
})

test('authenticated requests send the right body and bearer token', async (t) => {
  const previousFetch = globalThis.fetch
  t.after(() => { globalThis.fetch = previousFetch })
  let call
  globalThis.fetch = async (url, options) => {
    call = { url, options }
    return new Response(JSON.stringify({ display_template: 'cambodia_template' }), { status: 200 })
  }
  await api.updateTemplate(12, 'cambodia_template', 'test-token')
  assert.equal(call.url, '/v1/api/tenants/12')
  assert.equal(call.options.method, 'PATCH')
  assert.equal(call.options.headers.Authorization, 'Bearer test-token')
  assert.deepEqual(JSON.parse(call.options.body), { display_template: 'cambodia_template' })
  await api.register({ name: 'New owner' }, 'test-token')
  assert.equal(call.url, '/v1/api/auth/register')
  assert.equal(call.options.headers.Authorization, 'Bearer test-token')
})

test('admin list requests use the selected shop and bearer token', async (t) => {
  const previousFetch = globalThis.fetch
  t.after(() => { globalThis.fetch = previousFetch })
  const calls = []
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })
    return new Response('[]', { status: 200 })
  }
  await api.listBanners(42, 'token')
  await api.listCategories(42, 'token')
  await api.listMenuItems(42, 'token')
  await api.listMembers(42, 'token')
  assert.deepEqual(calls.map(({ url }) => url), [
    '/v1/api/tenants/42/banners', '/v1/api/tenants/42/categories',
    '/v1/api/tenants/42/menu-items', '/v1/api/tenants/42/members',
  ])
  for (const call of calls) assert.equal(call.options.headers.Authorization, 'Bearer token')
})

test('errors, QR responses and empty responses are handled', async (t) => {
  const previousFetch = globalThis.fetch
  t.after(() => { globalThis.fetch = previousFetch })
  globalThis.fetch = async () => new Response('', { status: 429, headers: { 'Retry-After': '30' } })
  await assert.rejects(api.login('user@example.com', 'password'), (error) =>
    error instanceof ApiError && error.status === 429 && error.retryAfter === '30')
  globalThis.fetch = async () => new Response('<svg/>', { status: 200, headers: { 'Content-Type': 'image/svg+xml' } })
  assert.equal(await (await api.getQrCode(1, 'test-token')).text(), '<svg/>')
  globalThis.fetch = async () => new Response(null, { status: 204 })
  assert.equal(await apiRequest('/tenants/1', { method: 'DELETE', token: 'test-token' }), null)
  await assert.rejects(apiRequest('//external.example'), TypeError)
})
