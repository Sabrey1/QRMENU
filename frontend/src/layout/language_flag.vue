<script setup>
defineProps({ locale: { type: String, required: true } })
</script>

<template>
  <svg v-if="locale === 'en'" class="flag" viewBox="0 0 60 36" aria-hidden="true">
    <path fill="#234078" d="M0 0h60v36H0z"/><path stroke="#fff" stroke-width="8" d="M0 0l60 36M60 0L0 36"/><path stroke="#c9233e" stroke-width="3" d="M0 0l60 36M60 0L0 36"/><path stroke="#fff" stroke-width="12" d="M30 0v36M0 18h60"/><path stroke="#c9233e" stroke-width="7" d="M30 0v36M0 18h60"/>
  </svg>
  <svg v-else class="flag" viewBox="0 0 60 36" aria-hidden="true">
    <path fill="#17458c" d="M0 0h60v36H0z"/><path fill="#d72435" d="M0 9h60v18H0z"/><path fill="#fff" d="M17 24h26v2H17zm3-1v-5l2-2 2 2v5zm7 0v-7l3-4 3 4v7zm9 0v-5l2-2 2 2v5z"/>
  </svg>
</template>

<style scoped>
.flag { display: block; width: 24px; height: 15px; flex-shrink: 0; border-radius: 2px; overflow: hidden; }
</style>
