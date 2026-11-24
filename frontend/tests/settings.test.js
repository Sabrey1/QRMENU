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
  const properties = new Map()
  globalThis.document = { documentElement: { dataset: {}, style: { setProperty: (key, value) => properties.set(key, value), removeProperty: (key) => properties.delete(key) } } }

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

  restored.setMenuLayout('columns', '3')
  restored.setMenuLayout('cardWidth', '350')
  restored.setMenuLayout('cardHeight', '240')
  restored.setMenuLayout('imageWidth', '160')
  restored.setMenuLayout('imageHeight', '120')
  assert.equal(properties.get('--menu-columns'), '3')
  assert.equal(properties.get('--menu-card-width'), '350px')
  assert.equal(properties.get('--menu-image-height'), '120px')
  restored.setMenuLayout('columns', '5')
  restored.setMenuLayout('cardWidth', '-1')
  assert.equal(restored.menuLayout.value.columns, 3)
  assert.equal(restored.menuLayout.value.cardWidth, 350)

  const layoutRestored = await import('../src/settings.js?layout-restore')
  assert.deepEqual({ ...layoutRestored.menuLayout.value }, { columns: 3, cardWidth: 350, cardHeight: 240, imageWidth: 160, imageHeight: 120 })
  layoutRestored.setMenuLayout('imageHeight', '')
  assert.equal(properties.has('--menu-image-height'), false)
  assert.equal(JSON.parse(stored.get('sabrey-menu-layout')).imageHeight, '')
})
