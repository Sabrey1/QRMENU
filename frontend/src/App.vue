<script setup>
import Home from './view/Home/home.vue'
import Login from './view/auth/login.vue'
import ScrollToTop from './layout/scrolltotop.vue'

const isLoginPage = window.location.pathname.replace(/\/+$/, '') === '/login'
</script>

<template><Login v-if="isLoginPage" /><template v-else><Home /><ScrollToTop /></template></template>
