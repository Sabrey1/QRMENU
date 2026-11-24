import test from 'node:test'
import assert from 'node:assert/strict'

test('admin routes require a validated session and return to the requested page', async (t) => {
  const storage = new Map()
  globalThis.sessionStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  }
  const originalFetch = globalThis.fetch
  t.after(() => { globalThis.fetch = originalFetch; delete globalThis.sessionStorage })
  const { adminGuard, setAdminSession, adminUser, adminToken, safeAdminRedirect } = await import('../src/services/admin-session.js')
  const route = { meta: { requiresAuth: true }, fullPath: '/admin/banner?test=1' }
  assert.deepEqual(await adminGuard(route), { path: '/login', query: { redirect: route.fullPath } })
  assert.equal(await adminGuard({ meta: {} }), true)
  assert.equal(safeAdminRedirect(route.fullPath), route.fullPath)
  assert.equal(safeAdminRedirect('//example.com'), '/admin/banner')
  assert.equal(safeAdminRedirect('https://example.com'), '/admin/banner')

  setAdminSession('valid-token')
  globalThis.fetch = async (_url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer valid-token')
    return new Response(JSON.stringify({ id: 5, name: 'Owner' }), { status: 200 })
  }
  assert.equal(await adminGuard(route), true)
  assert.equal(adminUser.value.name, 'Owner')
  assert.equal(storage.get('sabrey-admin-token'), 'valid-token')

  setAdminSession('expired-token')
  globalThis.fetch = async () => new Response('', { status: 401 })
  assert.deepEqual(await adminGuard(route), { path: '/login', query: { redirect: route.fullPath } })
  assert.equal(adminToken.value, '')
  assert.equal(storage.has('sabrey-admin-token'), false)

  setAdminSession('valid-token')
  globalThis.fetch = async () => { throw new TypeError('network unavailable') }
  assert.deepEqual(await adminGuard(route), { path: '/login', query: { redirect: route.fullPath, sessionError: '1' } })
})
