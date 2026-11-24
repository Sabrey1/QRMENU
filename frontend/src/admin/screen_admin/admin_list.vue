<script setup>
import { computed, inject, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '../../services/api-services'
import { adminToken, adminUser } from '../../services/admin-session'

const props = defineProps({ kind: { type: String, required: true } })
const { t } = useI18n()
const { tenants, selectedTenantId, loadingTenants, tenantError, loadTenants, signOut } = inject('adminContext')
const definitions = {
  banners: { title: 'adminBanners', description: 'adminBannersHelp', fetch: api.listBanners, columns: [['image_url', 'adminImage', 'image'], ['alt_text', 'adminDescription'], ['sort_order', 'adminOrder'], ['is_active', 'adminStatus', 'status']] },
  categories: { title: 'adminCategories', description: 'adminCategoriesHelp', fetch: api.listCategories, columns: [['name', 'adminName'], ['description', 'adminDescription'], ['sort_order', 'adminOrder'], ['is_active', 'adminStatus', 'status']] },
  items: { title: 'adminItems', description: 'adminItemsHelp', fetch: api.listMenuItems, columns: [['image_url', 'adminImage', 'image'], ['name', 'adminName'], ['category_id', 'adminCategoryId'], ['price', 'adminPrice'], ['is_available', 'adminAvailable', 'status'], ['is_active', 'adminStatus', 'status']] },
  shops: { title: 'adminShops', description: 'adminShopsHelp', columns: [['name', 'adminName'], ['slug', 'adminSlug'], ['currency_code', 'adminCurrency'], ['display_template', 'displayTemplate'], ['is_published', 'adminPublished', 'status']] },
  members: { title: 'adminMembers', description: 'adminMembersHelp', fetch: api.listMembers, columns: [['user_id', 'adminUserId'], ['role', 'adminRole'], ['created_at', 'adminJoined', 'date']] },
  account: { title: 'adminAccount', description: 'adminAccountHelp', columns: [['name', 'adminName'], ['email', 'email'], ['is_active', 'adminStatus', 'status'], ['created_at', 'adminJoined', 'date']] },
}
const definition = computed(() => definitions[props.kind])
const rows = ref([])
const loading = ref(false)
const error = ref('')
const attempt = ref(0)
const displayRows = computed(() => props.kind === 'shops' ? tenants.value : props.kind === 'account' ? (adminUser.value ? [adminUser.value] : []) : rows.value)
const displayLoading = computed(() => props.kind === 'shops' ? loadingTenants.value : loading.value)
const displayError = computed(() => props.kind === 'shops' ? tenantError.value : error.value)
function retry() { if (props.kind === 'shops' || tenantError.value) loadTenants(); else attempt.value++ }
watch([() => props.kind, selectedTenantId, attempt], async ([kind, tenantId], _old, onCleanup) => {
  let active = true
  onCleanup(() => { active = false })
  rows.value = []
  error.value = ''
  const fetchRows = definitions[kind].fetch
  if (!fetchRows || !tenantId) { loading.value = false; return }
  loading.value = true
  try {
    const result = await fetchRows(tenantId, adminToken.value)
    if (active) rows.value = result
  } catch (cause) {
    if (!active) return
    if (cause instanceof ApiError && cause.status === 401) { signOut(); return }
    error.value = cause instanceof ApiError && cause.status === 403 ? 'adminNoPermission' : 'adminLoadError'
  } finally { if (active) loading.value = false }
}, { immediate: true })
function format(value, type) {
  if (type === 'status') return t(value ? 'adminYes' : 'adminNo')
  if (type === 'date' && value) return new Date(value).toLocaleDateString()
  return value === null || value === undefined || value === '' ? '—' : value
}
</script>

<template>
  <section class="list-page">
    <header class="page-heading"><div><p class="eyebrow">{{ $t('adminPanel') }}</p><h1>{{ $t(definition.title) }}</h1><p class="description">{{ $t(definition.description) }}</p></div></header>
    <div class="list-card">
      <div class="list-heading"><h2>{{ $t(definition.title) }}</h2><span v-if="!displayLoading && !displayError" class="count">{{ displayRows.length }}</span></div>
      <div v-if="displayLoading || (definition.fetch && loadingTenants)" class="state" role="status">{{ $t('adminLoading') }}</div>
      <div v-else-if="displayError || (definition.fetch && tenantError)" class="state" role="alert"><p>{{ $t(displayError || tenantError) }}</p><button type="button" @click="retry">{{ $t('tryAgain') }}</button></div>
      <div v-else-if="definition.fetch && !selectedTenantId" class="state">{{ $t('adminNoShops') }}</div>
      <div v-else-if="!displayRows.length" class="state">{{ $t('adminEmpty') }}</div>
      <div v-else class="table-wrap"><table><thead><tr><th v-for="column in definition.columns" :key="column[0]" scope="col">{{ $t(column[1]) }}</th></tr></thead><tbody><tr v-for="row in displayRows" :key="row.id"><td v-for="column in definition.columns" :key="column[0]">
        <img v-if="column[2] === 'image' && row[column[0]]" class="thumbnail" :src="row[column[0]]" :alt="row.alt_text || row.name || ''" loading="lazy" />
        <span v-else-if="column[2] === 'status'" class="badge" :class="{ muted: !row[column[0]] }">{{ format(row[column[0]], column[2]) }}</span>
        <span v-else>{{ format(row[column[0]], column[2]) }}</span>
      </td></tr></tbody></table></div>
    </div>
  </section>
</template>

<style scoped>
.page-heading { margin-bottom: 28px; }.eyebrow { margin: 0 0 6px; color: #688977; font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
h1 { margin: 0; color: #20382a; font-size: clamp(1.65rem, 3vw, 2rem); letter-spacing: -.03em; }.description { margin: 8px 0 0; color: #718178; line-height: 1.5; }
.list-card { overflow: hidden; border: 1px solid #e0e9e1; border-radius: 13px; background: #fff; box-shadow: 0 4px 18px rgb(37 72 47 / 3%); }
.list-heading { display: flex; align-items: center; gap: 10px; padding: 21px 22px; border-bottom: 1px solid #e9efea; }.list-heading h2 { margin: 0; font-size: 1rem; }.count { padding: 3px 8px; border-radius: 999px; color: #54745e; background: #eef5ef; font-size: .75rem; }
.table-wrap { overflow-x: auto; } table { width: 100%; border-collapse: collapse; text-align: left; font-size: .875rem; } th { padding: 13px 22px; color: #718178; background: #fafcf9; font-size: .75rem; font-weight: 650; white-space: nowrap; } td { max-width: 300px; padding: 15px 22px; border-top: 1px solid #edf1ed; color: #374b3e; overflow-wrap: anywhere; } .thumbnail { display: block; width: 64px; height: 48px; object-fit: contain; border-radius: 6px; background: #f2f5f1; }
.badge { display: inline-block; padding: 4px 9px; border-radius: 999px; color: #27623b; background: #eaf5ec; font-size: .75rem; font-weight: 600; }.badge.muted { color: #767d77; background: #f0f2f0; }
.state { padding: 44px 24px; color: #77867b; text-align: center; }.state p { margin: 0 0 12px; }.state button { padding: 8px 14px; border: 1px solid #c5d7c9; border-radius: 6px; color: #285a42; background: #fff; cursor: pointer; }
</style>
