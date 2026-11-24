import test from 'node:test'
import assert from 'node:assert/strict'

test('appearance follows system or saved choice and remembers explicit changes', async () => {
  // Load Vue before providing the minimal document stub used by settings.js.
  await import('vue')
  const stored = new Map()
  let onSchemeChange
  const scheme = {
    matches: true,
    addEventListener(event, callback) { if (event === 'change') onSchemeChange = callback },
  }
  globalThis.localStorage = {
    getItem: (key) => stored.get(key) ?? null,
    setItem: (key, value) => stored.set(key, value),
  }
  globalThis.window = { matchMedia: () => scheme }
  globalThis.document = { documentElement: { dataset: {}, style: { setProperty() {} } } }

  const { theme, setTheme } = await import('../src/settings.js')
  assert.equal(theme.value, 'system')
  assert.equal(document.documentElement.dataset.theme, 'dark')

  setTheme('light')
  assert.equal(document.documentElement.dataset.theme, 'light')
  assert.equal(stored.get('sabrey-theme'), 'light')
  scheme.matches = false
  onSchemeChange()
  assert.equal(document.documentElement.dataset.theme, 'light')

  setTheme('dark')
  assert.equal(document.documentElement.dataset.theme, 'dark')
  setTheme('system')
  assert.equal(document.documentElement.dataset.theme, 'light')
  scheme.matches = true
  onSchemeChange()
  assert.equal(document.documentElement.dataset.theme, 'dark')
  setTheme('invalid')
  assert.equal(theme.value, 'system')

  setTheme('light')
  const restored = await import('../src/settings.js?restore')
  assert.equal(restored.theme.value, 'light')
  assert.equal(document.documentElement.dataset.theme, 'light')
})
