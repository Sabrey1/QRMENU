<script setup>
import MenuHeader from '../../../layout/header.vue'
import MenuFooter from '../../../layout/footer.vue'
import MenuSlider from '../default_template/menu_slider.vue'
import { useMenu } from '../use_menu'

const props = defineProps({
  menu: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  needsShop: { type: Boolean, default: false },
  isLocal: { type: Boolean, default: false },
  variant: { type: String, default: 'default' },
})
const emit = defineEmits(['retry', 'choose-shop', 'open-shop'])
const { query, failedImages, searchOpen, searchInput, searchButton, shopSlug, toolbar, categoryNav, activeCategoryId, categories, formatPrice, showCategory, toggleSearch, clearSearch } = useMenu(props)
</script>

<template>
  <div class="page" :class="{ 'cosmetic-theme': variant === 'cosmetic' }" id="top">
    <MenuHeader :variant="variant" :shop-name="menu?.name || ''" :logo-url="menu?.logo_url || ''" />

    <main class="container">
      <div v-if="loading" class="menu-skeleton" role="status" aria-live="polite">
        <span class="sr-only">{{ $t('loading') }}</span>
        <div class="skeleton skeleton-banner" aria-hidden="true"></div>
        <div class="skeleton-toolbar" aria-hidden="true">
          <div class="skeleton skeleton-search"></div>
          <div v-for="n in 3" :key="n" class="skeleton skeleton-category-tab"></div>
        </div>
        <div v-for="section in 2" :key="section" class="skeleton-section" aria-hidden="true">
          <div class="skeleton skeleton-heading"></div>
          <div class="skeleton-items">
            <div v-for="item in 2" :key="item" class="skeleton-card">
              <div class="skeleton-details"><div class="skeleton skeleton-name"></div><div class="skeleton skeleton-price"></div></div>
              <div class="skeleton skeleton-image"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="needsShop" class="state">
        <h1>{{ $t('findShop') }}</h1>
        <p>{{ $t('shopHelp') }}</p>
        <form class="shop-form" @submit.prevent="emit('open-shop', shopSlug)">
          <label for="shop-slug">{{ $t('shopSlug') }}</label>
          <input id="shop-slug" v-model="shopSlug" :placeholder="$t('shopPlaceholder')" required />
          <button type="submit">{{ $t('showMenu') }}</button>
        </form>
      </div>

      <div v-else-if="error" class="state" role="alert">
        <h1>{{ $t('menuUnavailable') }}</h1>
        <p>{{ $t(error) }}</p>
        <div class="state-actions">
          <button type="button" @click="emit('retry')">{{ $t('tryAgain') }}</button>
          <button v-if="isLocal" class="secondary-button" type="button" @click="emit('choose-shop')">{{ $t('chooseAnother') }}</button>
        </div>
      </div>

      <template v-else-if="menu">
        <MenuSlider :slides="menu.banners || []" />
        <div ref="toolbar" class="menu-toolbar">
        <div class="search-slot">
        <div class="menu-controls" :class="{ 'is-open': searchOpen }">
          <button ref="searchButton" class="search-toggle" type="button" :aria-expanded="searchOpen" aria-controls="menu-search" :aria-label="$t(searchOpen ? 'closeSearch' : 'searchMenu')" @click="toggleSearch">
            <svg v-if="!searchOpen" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/><path d="m16 16 4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            <svg v-else viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          </button>
          <input v-show="searchOpen" id="menu-search" ref="searchInput" v-model="query" type="search" :aria-label="$t('searchMenu')" :placeholder="$t('searchPlaceholder')" @keydown.esc="toggleSearch" />
          <button v-if="searchOpen && query" class="clear-search" type="button" :aria-label="$t('clearSearch')" @click="clearSearch">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          </button>
        </div>
        </div>

        <nav v-if="menu.categories.length" ref="categoryNav" class="category-nav" :inert="searchOpen" :aria-label="$t('categories')">
          <a v-for="category in menu.categories" :key="category.id" :href="`#category-${category.id}`" :class="{ active: activeCategoryId === category.id }" :aria-current="activeCategoryId === category.id ? 'location' : undefined" @click.prevent="showCategory(category.id)">{{ category.name }}</a>
        </nav>
        </div>

        <p v-if="!menu.categories.length" class="empty">{{ $t('emptyMenu') }}</p>
        <p v-else-if="!categories.length" class="empty">{{ $t('noResults', { query }) }}</p>

        <section v-for="category in categories" :id="`category-${category.id}`" :key="category.id" class="category">
          <div class="category-heading"><h2>{{ category.name }}</h2></div>
          <div v-if="category.items.length" class="item-list">
            <article v-for="item in category.items" :key="item.id" class="item">
              <div class="item-details"><h3>{{ item.name }}</h3><strong>{{ formatPrice(item.price) }}</strong></div>
              <img v-if="item.image_url && !failedImages.has(item.id)" class="item-image" :src="item.image_url" :alt="item.name" loading="lazy" @error="failedImages.add(item.id)" />
              <div v-else class="item-avatar" aria-hidden="true">{{ item.name.trim().charAt(0).toUpperCase() }}</div>
            </article>
          </div>
          <p v-else class="empty">{{ $t('emptyCategory') }}</p>
        </section>
      </template>
    </main>

    <MenuFooter />
  </div>
</template>

<style scoped>
.page { min-height: 100vh; display: flex; flex-direction: column; background: #fff; color: #1f2937; }
.container { width: 100%; max-width: 1080px; margin: 0 auto; padding: 40px 24px 80px; flex: 1; font-size: calc(1rem * var(--menu-font-scale, 1)); }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
.skeleton { border-radius: 6px; background: #e9eeea; animation: skeleton-pulse 1.5s ease-in-out infinite; }
.skeleton-banner { width: 100%; height: clamp(180px, 30vw, 300px); margin-bottom: 24px; border-radius: 10px; }
.skeleton-toolbar { display: flex; gap: 12px; align-items: center; padding-bottom: 16px; border-bottom: 1px solid #e5e7eb; overflow: hidden; }
.skeleton-search { width: 44px; height: 44px; flex-shrink: 0; }
.skeleton-category-tab { width: 100px; height: 38px; flex-shrink: 0; }
.skeleton-section { margin-top: 40px; }
.skeleton-heading { width: 150px; height: 27px; margin: 0 auto 38px; }
.skeleton-items { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.skeleton-card { min-height: 116px; display: flex; justify-content: space-between; gap: 16px; padding: 18px; border: 1px solid #e5e7eb; border-radius: 8px; }
.skeleton-details { flex: 1; }
.skeleton-name { width: 65%; max-width: 180px; height: 18px; }
.skeleton-price { width: 65px; height: 16px; margin-top: 16px; }
.skeleton-image { width: 92px; height: 92px; flex-shrink: 0; }
@keyframes skeleton-pulse { 50% { opacity: .5; } }
@media (prefers-reduced-motion: reduce) { .skeleton { animation: none; } }
h1, h2, h3, p { margin: 0; }
h1 { font-size: clamp(1.75em, 4vw, 2.25em); font-weight: 700; line-height: 1.2; overflow-wrap: anywhere; }
.menu-toolbar { position: sticky; top: 0; z-index: 4; display: flex; align-items: center; gap: 12px; min-width: 0; padding: 12px 0 16px; border-bottom: 1px solid #e5e7eb; background: #fff; }
.search-slot { width: 44px; height: 44px; flex-shrink: 0; }
.menu-controls { display: flex; align-items: center; gap: 10px; min-width: 0; }
.menu-controls.is-open { position: absolute; z-index: 1; top: 12px; left: 0; right: 0; background: #fff; border-radius: 8px; box-shadow: 0 3px 12px rgb(0 0 0 / 10%); }
.menu-controls input { flex: 1; min-width: 0; }
.menu-controls input::-webkit-search-cancel-button { -webkit-appearance: none; }
.clear-search { position: absolute; right: 6px; width: 36px; height: 36px; display: grid; place-items: center; padding: 8px; border: 0; background: #fff; color: #6b7280; }
.clear-search svg { width: 20px; height: 20px; }
.menu-controls.is-open input { padding-right: 44px; }
.search-toggle { flex-shrink: 0; width: 44px; height: 44px; padding: 10px; display: grid; place-items: center; color: #374151; background: #fff; border-color: #d1d5db; }
.search-toggle svg { width: 22px; height: 22px; }
.shop-form label { display: block; margin-bottom: 8px; color: #374151; font-size: .875em; font-weight: 600; }
input { width: 100%; padding: 12px 14px; color: #1f2937; background: #fff; border: 1px solid #d1d5db; border-radius: 8px; font-size: 1em; }
input::placeholder { color: #9ca3af; }
.category-nav { display: flex; flex: 1; min-width: 0; gap: 8px; overflow-x: auto; padding: 2px 0; }
.category-nav a { flex-shrink: 0; padding: 9px 15px; border: 1px solid #e5e7eb; border-radius: 6px; color: #374151; text-decoration: none; font-size: .875em; font-weight: 600; }
.category-nav a:hover { border-color: #285a42; color: #285a42; }
.category-nav a.active { border-color: #285a42; color: #fff; background: #285a42; }
.category { margin-top: 40px; scroll-margin-top: 88px; }
.category-heading { margin-bottom: 18px; padding-bottom: 12px; text-align: center; }
.category-heading h2 { display: inline-block; }
.category-heading h2::after { content: ''; display: block; height: 4px; margin-top: 8px; border-radius: 999px; background: #285a42; }
h2 { font-size: 1.375em; font-weight: 700; }
.item-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.item { min-width: 0; min-height: 116px; display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 18px; border: 1px solid #e5e7eb; border-radius: 8px; }
.item-details { min-width: 0; }
.item h3 { font-size: 1em; font-weight: 600; overflow-wrap: anywhere; }
.item strong { display: block; margin-top: 12px; font-size: .9375em; color: #285a42; }
.item-image { width: 92px; height: 92px; flex-shrink: 0; object-fit: cover; border-radius: 6px; background: #f3f4f6; }
.item-avatar { width: 92px; height: 92px; flex-shrink: 0; display: grid; place-items: center; border-radius: 6px; background: #edf3ee; color: #285a42; font-size: 1.75em; font-weight: 600; }
.empty { color: #6b7280; margin-top: 24px; }
.state { max-width: 460px; margin: 40px auto; }
.state p { color: #6b7280; margin-top: 12px; line-height: 1.6; }
.shop-form { margin-top: 24px; }
button { padding: 11px 16px; border: 1px solid #285a42; border-radius: 6px; background: #285a42; color: #fff; font-weight: 600; cursor: pointer; }
.shop-form button { margin-top: 16px; }
.state-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.secondary-button { background: #fff; color: #285a42; }
@media (max-width: 640px) { .container { padding: 32px 20px 60px; } .item-list, .skeleton-items { grid-template-columns: 1fr; } .item-image, .item-avatar, .skeleton-image { width: 76px; height: 76px; } }
.cosmetic-theme .container { max-width: 1200px; }
.cosmetic-theme .item-list { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.cosmetic-theme .item { flex-direction: column-reverse; align-items: stretch; justify-content: flex-end; gap: 0; min-height: 0; padding: 0; overflow: hidden; background: #fff; }
.cosmetic-theme .item-image, .cosmetic-theme .item-avatar { width: 100%; height: auto; aspect-ratio: 4 / 3; border-radius: 0; background: #f3f4f6; }
.cosmetic-theme .item-avatar { color: #6b7280; font-size: 2.5em; }
.cosmetic-theme .item-details { padding: 16px; }
.cosmetic-theme .item h3 { line-height: 1.4; }
@media (max-width: 640px) {
  .cosmetic-theme .item-list { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  .cosmetic-theme .item-details { padding: 12px; }
}
html[data-theme='dark'] .page { color: #e9eee9; background: #000; }
html[data-theme='dark'] .menu-toolbar { background: #000; border-color: #36463b; }
html[data-theme='dark'] .menu-controls.is-open { background: #1b2820; }
html[data-theme='dark'] .search-toggle, html[data-theme='dark'] .clear-search { color: #e9eee9; background: #243229; border-color: #526354; }
html[data-theme='dark'] input { color: #edf1ed; background: #19241d; border-color: #526354; }
html[data-theme='dark'] input::placeholder { color: #a7b8a9; }
html[data-theme='dark'] .category-nav a { color: #dbe8dd; background: #243229; border-color: #526354; }
html[data-theme='dark'] .category-nav a:hover { color: #fff; border-color: #91b59b; }
html[data-theme='dark'] .category-nav a.active { color: #fff; background: #376d4b; border-color: #78a688; }
html[data-theme='dark'] .category-heading h2::after { background: #8dbb96; }
html[data-theme='dark'] .item, html[data-theme='dark'] .cosmetic-theme .item { color: #eef3ee; background: #202b25; border-color: #3e5043; }
html[data-theme='dark'] .item strong { color: #b1dfba; }
html[data-theme='dark'] .item-avatar, html[data-theme='dark'] .cosmetic-theme .item-avatar { color: #c0d4c3; background: #34473a; }
html[data-theme='dark'] .item-image, html[data-theme='dark'] .cosmetic-theme .item-image { background: #29372e; }
html[data-theme='dark'] .empty, html[data-theme='dark'] .state p { color: #becbc0; }
html[data-theme='dark'] .shop-form label { color: #e2e9e2; }
html[data-theme='dark'] .secondary-button { color: #d3ebd8; background: #24352a; border-color: #72967b; }
html[data-theme='dark'] .skeleton { background: #35463a; }
html[data-theme='dark'] .skeleton-toolbar, html[data-theme='dark'] .skeleton-card { border-color: #3e5043; }
</style>
