<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const visible = ref(false)

function updateVisibility() {
  visible.value = window.scrollY > 300
}

function scrollToTop() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduceMotion ? 'instant' : 'smooth' })
}

onMounted(() => {
  updateVisibility()
  window.addEventListener('scroll', updateVisibility, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', updateVisibility))
</script>

<template>
  <Transition name="scroll-top">
    <button v-if="visible" class="scroll-to-top" type="button" :aria-label="$t('scrollToTop')" :title="$t('scrollToTop')" @click="scrollToTop">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
    </button>
  </Transition>
</template>

<style scoped>
.scroll-to-top { position: fixed; z-index: 10; right: max(24px, env(safe-area-inset-right)); bottom: max(24px, env(safe-area-inset-bottom)); display: grid; place-items: center; width: 48px; height: 48px; padding: 0; border: 1px solid rgb(255 255 255 / 25%); border-radius: 50%; color: #fff; background: #285a42; box-shadow: 0 6px 18px rgb(25 58 40 / 25%); cursor: pointer; transition: background .2s, transform .2s; }
.scroll-to-top:hover { background: #1e4633; transform: translateY(-3px); }
.scroll-to-top svg { width: 22px; height: 22px; }
.scroll-top-enter-active, .scroll-top-leave-active { transition: opacity .2s, transform .2s; }
.scroll-top-enter-from, .scroll-top-leave-to { opacity: 0; transform: translateY(8px); }
@media (prefers-reduced-motion: reduce) { .scroll-to-top, .scroll-top-enter-active, .scroll-top-leave-active { transition: none; } }
</style>
