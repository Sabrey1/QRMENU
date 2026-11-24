import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createI18n } from 'vue-i18n'

test('all translated messages compile and the email placeholder displays correctly', async () => {
  for (const locale of ['en', 'km']) {
    const messages = JSON.parse(await readFile(new URL(`../src/locals/${locale}.json`, import.meta.url), 'utf8'))
    const i18n = createI18n({ legacy: false, locale, messages: { [locale]: messages } })
    for (const key of Object.keys(messages)) i18n.global.t(key, { query: 'tea' })
    assert.equal(i18n.global.t('loginEmailPlaceholder'), 'you@example.com')
    if (locale === 'km') assert.match(i18n.global.t('adminPanel'), /[\u1780-\u17ff]/)
  }
})
