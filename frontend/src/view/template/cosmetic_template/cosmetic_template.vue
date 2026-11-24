<script setup>
import DefaultTemplate from '../default_template/default_template.vue'

defineProps({
  menu: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  needsShop: { type: Boolean, default: false },
  isLocal: { type: Boolean, default: false },
})
defineEmits(['retry', 'choose-shop', 'open-shop'])
</script>

<template>
  <DefaultTemplate
    variant="cosmetic"
    :menu="menu"
    :loading="loading"
    :error="error"
    :needs-shop="needsShop"
    :is-local="isLocal"
    @retry="$emit('retry')"
    @choose-shop="$emit('choose-shop')"
    @open-shop="$emit('open-shop', $event)"
  />
</template>
