<template>
  <section class="not-found">
    <h1>{{ $t('adminPageNotFound') }}</h1>
    <RouterLink to="/admin/banner">{{ $t('adminBackToBanners') }}</RouterLink>
  </section>
</template>

<style scoped>
.not-found { padding: 24px; border: 1px solid #e0e9e1; border-radius: 12px; background: #fff; }
.not-found h1 { margin: 0 0 12px; font-size: 1.4rem; }
.not-found a { color: #285a42; }
</style>
