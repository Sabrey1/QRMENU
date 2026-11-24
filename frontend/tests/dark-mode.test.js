import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { compileStyle, parse } from '@vue/compiler-sfc'

const components = [
  ['src/layout/header.vue', '.settings-dialog'],
  ['src/layout/footer.vue', '.footer'],
  ['src/view/template/default_template/default_template.vue', '.page'],
  ['src/view/template/default_template/menu_slider.vue', '.image-skeleton'],
  ['src/view/template/cambodia_template/cambodia_template.vue', '.cambodia-theme'],
]

test('dark styles target component elements after Vue scopes the CSS', () => {
  for (const [path, target] of components) {
    const { descriptor, errors } = parse(readFileSync(new URL(`../${path}`, import.meta.url), 'utf8'))
    assert.deepEqual(errors, [], path)
    const css = descriptor.styles.map((style) => {
      const result = compileStyle({ source: style.content, id: 'data-v-test', scoped: style.scoped })
      assert.deepEqual(result.errors, [], path)
      return result.code
    }).join('\n')
    assert.ok(css.includes(`html[data-theme='dark'] ${target}`), `${path} must target ${target} in dark mode`)
    assert.ok(!css.includes(":global([data-theme='dark'])"), `${path} must use a scoped dark selector`)
  }
})
