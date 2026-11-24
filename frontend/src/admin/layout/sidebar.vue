<script setup>
import { computed, onMounted, provide, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, ApiError } from '../../services/api-services'
import { adminToken, adminUser, setAdminSession } from '../../services/admin-session'
import '../../settings'

const router = useRouter()
const tenants = ref([])
const selectedTenantId = ref('')
const loadingTenants = ref(true)
const tenantError = ref('')
const selectedTenant = computed(() => tenants.value.find((tenant) => String(tenant.id) === String(selectedTenantId.value)))
const links = [
  { to: '/admin/banner', label: 'adminBanners', icon: 'M4 5h16v14H4z M4 16l5-5 4 4 2-2 5 5 M15 9h.01' },
  { to: '/admin/category', label: 'adminCategories', icon: 'M4 4h6v6H4z M14 4h6v6h-6z M4 14h6v6H4z M14 14h6v6h-6z' },
  { to: '/admin/menu-items', label: 'adminItems', icon: 'M5 6h14 M5 12h14 M5 18h14' },
  { to: '/admin/tenant', label: 'adminShops', icon: 'M3 10l2-6h14l2 6 M4 10v10h16V10 M9 20v-6h6v6' },
  { to: '/admin/tenant-member', label: 'adminMembers', icon: 'M16 20v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M10 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6 M17 8a3 3 0 0 1 0 6 M20 20v-2a4 4 0 0 0-2-3.5' },
  { to: '/admin/user', label: 'adminAccount', icon: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M4 20a8 8 0 0 1 16 0' },
]
function signOut() {
  setAdminSession('')
  router.replace('/login')
}
async function loadTenants() {
  loadingTenants.value = true
  tenantError.value = ''
  try {
    tenants.value = await api.listTenants(adminToken.value)
    if (!tenants.value.some((tenant) => String(tenant.id) === String(selectedTenantId.value))) {
      selectedTenantId.value = tenants.value[0] ? String(tenants.value[0].id) : ''
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) { signOut(); return }
    tenantError.value = 'adminLoadError'
  } finally { loadingTenants.value = false }
}
provide('adminContext', { tenants, selectedTenantId, selectedTenant, loadingTenants, tenantError, loadTenants, signOut })
onMounted(loadTenants)
</script>

<template>
  <div class="admin-shell">
    <aside class="sidebar" :aria-label="$t('adminNavigation')">
      <RouterLink to="/admin/banner" class="brand"><span class="brand-mark">S</span><span>Sabrey <small>{{ $t('adminPanel') }}</small></span></RouterLink>
      <p class="nav-heading">{{ $t('adminNavigation') }}</p>
      <nav class="navigation">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link"><svg class="nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path :d="link.icon" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" /></svg>{{ $t(link.label) }}</RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <a class="view-menu" href="/">{{ $t('backToMenu') }}</a>
        <button class="sign-out" type="button" @click="signOut">{{ $t('signOut') }}</button>
      </div>
    </aside>
    <div class="admin-main">
      <header class="topbar">
        <div class="shop-picker">
          <label for="admin-shop">{{ $t('adminCurrentShop') }}</label>
          <select id="admin-shop" v-model="selectedTenantId" :disabled="loadingTenants || !tenants.length">
            <option value="">{{ $t(loadingTenants ? 'adminLoading' : 'adminNoShops') }}</option>
            <option v-for="tenant in tenants" :key="tenant.id" :value="String(tenant.id)">{{ tenant.name }}</option>
          </select>
        </div>
        <div class="account"><span class="account-avatar">{{ (adminUser?.name || '?').charAt(0).toUpperCase() }}</span><span class="account-name">{{ adminUser?.name }}</span></div>
      </header>
      <main class="content"><RouterView /></main>
    </div>
  </div>
</template>

<style scoped>
.admin-shell { min-height: 100dvh; display: flex; background: #f5f7f4; color: #22312a; }
.sidebar { position: sticky; top: 0; width: 246px; height: 100dvh; flex-shrink: 0; display: flex; flex-direction: column; padding: 28px 16px 20px; background: #193b2b; color: #e8f2ea; }
.brand { display: flex; align-items: center; gap: 11px; padding: 0 8px; color: white; font-size: 1.12rem; font-weight: 750; text-decoration: none; }
.brand small { display: block; color: #a7c2af; font-size: .7rem; font-weight: 500; }
.brand-mark { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; background: #c9e6cd; color: #22513a; font-size: 1.15rem; }
.nav-heading { margin: 42px 10px 12px; color: #9bb9a4; font-size: .7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.navigation { display: grid; gap: 4px; }
.nav-link { display: flex; align-items: center; gap: 12px; padding: 11px 12px; border-radius: 8px; color: #c7d9cc; font-size: .9rem; text-decoration: none; white-space: nowrap; }
.nav-link:hover, .nav-link.router-link-active { color: #fff; background: #315944; }
.nav-icon { width: 20px; height: 20px; flex-shrink: 0; }
.sidebar-bottom { display: grid; gap: 7px; margin-top: auto; }
.view-menu, .sign-out { padding: 10px 12px; border: 0; border-radius: 7px; color: #d3e4d7; background: transparent; font: inherit; font-size: .875rem; text-align: left; text-decoration: none; cursor: pointer; }
.view-menu:hover, .sign-out:hover { background: #315944; }
.admin-main { flex: 1; min-width: 0; }
.topbar { min-height: 76px; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 32px; border-bottom: 1px solid #e1e9e2; background: #fff; }
.shop-picker { display: flex; align-items: center; gap: 12px; min-width: 0; }
.shop-picker label { color: #697970; font-size: .8rem; white-space: nowrap; }
.shop-picker select { max-width: min(280px, 45vw); padding: 8px 30px 8px 10px; border: 1px solid #dbe4dc; border-radius: 8px; color: #263b2e; background: #fff; font: inherit; font-size: .875rem; }
.account { display: flex; align-items: center; gap: 9px; font-size: .875rem; font-weight: 600; }
.account-avatar { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 50%; color: #315d40; background: #e5f2e7; }
.content { max-width: 1500px; margin: 0 auto; padding: 36px 32px 64px; }
@media (max-width: 760px) { .admin-shell { display: block; } .sidebar { position: static; width: 100%; height: auto; padding: 16px; } .nav-heading { margin: 20px 4px 8px; } .navigation { display: flex; overflow-x: auto; } .nav-link { flex-shrink: 0; } .sidebar-bottom { display: flex; margin-top: 10px; } .topbar { padding: 12px 16px; } .content { padding: 26px 16px 48px; } .account-name { display: none; } }
</style>
