import { createRouter, createWebHistory } from 'vue-router'
import Home from '../view/Home/home.vue'
import Login from '../view/auth/login.vue'
import AdminLayout from '../admin/layout/sidebar.vue'
import BannerList from '../admin/screen_admin/banner/banner_list.vue'
import CategoryList from '../admin/screen_admin/category/category_list.vue'
import MenuItemsList from '../admin/screen_admin/menu_items/menu_items_list.vue'
import TenantList from '../admin/screen_admin/tenant/tenant_list.vue'
import TenantMemberList from '../admin/screen_admin/tenant_member/tenant_member_list.vue'
import UserList from '../admin/screen_admin/user/user_list.vue'
import AdminNotFound from '../admin/screen_admin/not_found.vue'
import { adminGuard } from '../services/admin-session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/admin', component: AdminLayout, meta: { requiresAuth: true }, children: [
      { path: '', redirect: '/admin/banner' },
      { path: 'banner', component: BannerList },
      { path: 'category', component: CategoryList },
      { path: 'menu-items', alias: 'menu_items', component: MenuItemsList },
      { path: 'tenant', component: TenantList },
      { path: 'tenant-member', alias: 'tenant_member', component: TenantMemberList },
      { path: 'user', component: UserList },
      { path: ':pathMatch(.*)*', component: AdminNotFound },
    ] },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(adminGuard)

export default router
