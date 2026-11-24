import { computed, nextTick, onMounted, onUnmounted, ref, toRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'

export function useMenu(props) {
  const menu = toRef(props, 'menu')
  const { locale } = useI18n({ useScope: 'global' })
  const query = ref('')
  const failedImages = ref(new Set())
  const searchOpen = ref(false)
  const searchInput = ref(null)
  const searchButton = ref(null)
  const shopSlug = ref(new URLSearchParams(window.location.search).get('shop') || '')
  const toolbar = ref(null)
  const categoryNav = ref(null)
  const activeCategoryId = ref(null)
  let scrollFrame = 0

  watch(menu, () => { failedImages.value = new Set() })
  const availableCategories = computed(() => (menu.value?.categories ?? []).filter((category) => category.items.length > 0))
  const categories = computed(() => {
    const term = query.value.trim().toLocaleLowerCase()
    return availableCategories.value.map((category) => ({
      ...category,
      items: category.items.filter((item) => !term || item.name.toLocaleLowerCase().includes(term)),
    })).filter((category) => !term || category.items.length > 0)
  })

  function updateActiveCategory() {
    scrollFrame = 0
    const list = categories.value
    if (!list.length) {
      activeCategoryId.value = null
      return
    }
    const threshold = (toolbar.value?.getBoundingClientRect().bottom ?? 0) + 16
    let active = list[0].id
    for (const category of list) {
      const section = document.getElementById(`category-${category.id}`)
      if (section && section.getBoundingClientRect().top <= threshold) active = category.id
    }
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) active = list[list.length - 1].id
    if (activeCategoryId.value === active) return
    activeCategoryId.value = active
    nextTick(() => {
      const nav = categoryNav.value
      const link = nav?.querySelector('[aria-current="location"]')
      if (!nav || !link) return
      const navRect = nav.getBoundingClientRect()
      const linkRect = link.getBoundingClientRect()
      if (linkRect.left < navRect.left) nav.scrollLeft -= navRect.left - linkRect.left
      else if (linkRect.right > navRect.right) nav.scrollLeft += linkRect.right - navRect.right
    })
  }

  function scheduleScrollSpy() {
    if (!scrollFrame) scrollFrame = window.requestAnimationFrame(updateActiveCategory)
  }
  watch(() => categories.value.map((category) => category.id).join(','), async () => {
    await nextTick()
    scheduleScrollSpy()
  })

  function formatPrice(price) {
    const number = Number(price)
    if (!Number.isFinite(number)) return price
    try {
      return new Intl.NumberFormat(locale.value, { style: 'currency', currency: menu.value.currency_code }).format(number)
    } catch {
      return `${menu.value.currency_code} ${number.toFixed(2)}`
    }
  }

  async function showCategory(id) {
    query.value = ''
    await nextTick()
    document.getElementById(`category-${id}`)?.scrollIntoView({ behavior: 'smooth' })
  }
  async function toggleSearch() {
    searchOpen.value = !searchOpen.value
    await nextTick()
    if (searchOpen.value) searchInput.value?.focus()
    else { query.value = ''; searchButton.value?.focus() }
  }
  function clearSearch() {
    query.value = ''
    searchInput.value?.focus()
  }

  onMounted(() => {
    window.addEventListener('scroll', scheduleScrollSpy, { passive: true })
    window.addEventListener('resize', scheduleScrollSpy)
    nextTick(scheduleScrollSpy)
  })
  onUnmounted(() => {
    window.removeEventListener('scroll', scheduleScrollSpy)
    window.removeEventListener('resize', scheduleScrollSpy)
    if (scrollFrame) window.cancelAnimationFrame(scrollFrame)
  })

  return { query, failedImages, searchOpen, searchInput, searchButton, shopSlug, toolbar, categoryNav, activeCategoryId, availableCategories, categories, formatPrice, showCategory, toggleSearch, clearSearch }
}
