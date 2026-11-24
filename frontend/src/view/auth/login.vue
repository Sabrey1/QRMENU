<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, ApiError } from '../../services/api-services'
import { setLocale } from '../../i18n'
import '../../settings'

const { locale } = useI18n({ useScope: 'global' })
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const busy = ref(false)
const error = ref('')
const token = ref('')

async function signIn() {
  if (busy.value) return
  error.value = ''
  const isLocal = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
  if (!window.isSecureContext && !isLocal) {
    error.value = 'templateHttpsRequired'
    return
  }

  busy.value = true
  try {
    const result = await api.login(email.value.trim(), password.value)
    token.value = result.access_token
    password.value = ''
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 401) error.value = 'templateLoginFailed'
    else if (cause instanceof ApiError && cause.status === 429) error.value = 'templateRateLimited'
    else error.value = 'templateRequestFailed'
  } finally {
    busy.value = false
  }
}

function signOut() {
  token.value = ''
  password.value = ''
  error.value = ''
}
</script>

<template>
  <main class="login-page">
    <header class="login-header">
      <a class="brand" href="/" aria-label="Sabrey Menu">Sabrey<span> Menu</span></a>
      <label class="language">
        <span class="sr-only">{{ $t('language') }}</span>
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.5 5.5 3.5 9s-1 6.5-3.5 9c-2.5-2.5-3.5-5.5-3.5-9S9.5 5.5 12 3Z"/></svg>
        <select :value="locale" @change="setLocale($event.target.value)">
          <option value="en">English</option>
          <option value="km">ភាសាខ្មែរ</option>
        </select>
      </label>
    </header>

    <section class="login-content" aria-labelledby="login-title">
      <div class="login-card">
        <div class="card-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 4v2"/></svg>
        </div>
        <h1 id="login-title">{{ $t('loginWelcome') }}</h1>
        <p class="intro">{{ $t('loginIntro') }}</p>

        <div v-if="token" class="success" role="status">
          <strong>{{ $t('loginSuccess') }}</strong>
          <p>{{ $t('loginSessionNote') }}</p>
          <button class="submit-button" type="button" @click="signOut">{{ $t('signOut') }}</button>
        </div>
        <form v-else class="login-form" @submit.prevent="signIn">
          <p v-if="error" class="error" role="alert">{{ $t(error) }}</p>
          <div class="field">
            <label for="login-email">{{ $t('email') }}</label>
            <input id="login-email" v-model="email" type="email" autocomplete="username" :placeholder="$t('loginEmailPlaceholder')" required :disabled="busy" />
          </div>
          <div class="field">
            <label for="login-password">{{ $t('password') }}</label>
            <div class="password-input">
              <input id="login-password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" :placeholder="$t('loginPasswordPlaceholder')" required :disabled="busy" />
              <button type="button" class="password-toggle" :aria-label="$t(showPassword ? 'hidePassword' : 'showPassword')" :aria-pressed="showPassword" @click="showPassword = !showPassword">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/><path v-if="showPassword" d="M4 4l16 16"/></svg>
              </button>
            </div>
          </div>
          <button class="submit-button" type="submit" :disabled="busy">{{ $t(busy ? 'pleaseWait' : 'signIn') }}</button>
        </form>
        <a class="back-link" href="/">{{ $t('backToMenu') }}</a>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page { min-height: 100vh; min-height: 100dvh; background: #f7f8f6; color: #1f2923; }
.login-header { height: 76px; max-width: 1200px; margin: auto; padding: 0 28px; display: flex; align-items: center; justify-content: space-between; }
.brand { color: #234b36; font-weight: 800; font-size: 1.2rem; letter-spacing: -.04em; text-decoration: none; }
.brand span { color: #6b776f; font-weight: 500; }
.language { display: flex; align-items: center; gap: 6px; color: #5d6b61; }
.language svg { width: 19px; height: 19px; stroke: currentColor; stroke-width: 1.6; }
.language select { max-width: 150px; border: 0; padding: 8px 4px; color: inherit; background: transparent; cursor: pointer; }
.login-content { min-height: calc(100dvh - 76px); display: grid; place-items: center; padding: 24px 20px 100px; }
.login-card { width: min(100%, 430px); padding: 40px; background: #fff; border: 1px solid #e6ebe6; border-radius: 18px; box-shadow: 0 16px 45px rgba(33, 59, 43, .06); }
.card-icon { width: 48px; height: 48px; display: grid; place-items: center; color: #386849; background: #edf5ee; border-radius: 14px; }
.card-icon svg { width: 24px; height: 24px; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
h1 { margin: 24px 0 8px; font-size: 1.75rem; line-height: 1.25; letter-spacing: -.04em; }
.intro { margin: 0 0 30px; color: #728077; line-height: 1.55; }
.login-form { display: grid; gap: 20px; }
.field { display: grid; gap: 8px; }
.field label { color: #36483c; font-size: .875rem; font-weight: 650; }
.field input { display: block; width: 100%; min-width: 0; height: 48px; padding: 0 14px; border: 1px solid #d9e1da; border-radius: 9px; background: #fff; color: #1f2923; }
.field input::placeholder { color: #9ba79d; }
.field input:focus { border-color: #598466; }
.password-input { position: relative; }
.password-input input { padding-right: 50px; }
.password-toggle { position: absolute; inset: 0 4px 0 auto; display: grid; place-items: center; width: 42px; border: 0; border-radius: 8px; background: transparent; color: #77877a; cursor: pointer; }
.password-toggle svg { width: 20px; height: 20px; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.submit-button { width: 100%; min-height: 48px; margin-top: 4px; border: 0; border-radius: 9px; background: #285e3f; color: #fff; font-weight: 700; cursor: pointer; }
.submit-button:hover:not(:disabled) { background: #204d33; }
.submit-button:disabled { cursor: wait; opacity: .65; }
.error { margin: 0; padding: 12px; border-radius: 8px; background: #fff1f0; color: #a72f2f; font-size: .875rem; }
.success { color: #285e3f; }
.success p { color: #728077; line-height: 1.5; }
.back-link { display: block; margin-top: 24px; text-align: center; color: #56705d; font-size: .875rem; text-decoration: none; }
.back-link:hover { text-decoration: underline; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
:global(html[data-theme='dark']) .login-page { background: #000; color: #edf3ee; }
:global(html[data-theme='dark']) .brand { color: #a8d6b4; }
:global(html[data-theme='dark']) .brand span, :global(html[data-theme='dark']) .language, :global(html[data-theme='dark']) .intro, :global(html[data-theme='dark']) .success p { color: #a8b8ac; }
:global(html[data-theme='dark']) .login-card { background: #121b15; border-color: #2b3c30; }
:global(html[data-theme='dark']) .card-icon { color: #b0d7b7; background: #21392a; }
:global(html[data-theme='dark']) .field label { color: #dce9df; }
:global(html[data-theme='dark']) .field input { background: #19261d; color: #edf3ee; border-color: #405648; }
:global(html[data-theme='dark']) .back-link, :global(html[data-theme='dark']) .success { color: #b0d7b7; }
:global(html[data-theme='dark']) .error { color: #ffb9b3; background: #422723; }
@media (max-width: 480px) {
  .login-header { height: 68px; padding: 0 20px; }
  .login-content { min-height: calc(100dvh - 68px); padding: 16px 16px 70px; }
  .login-card { padding: 28px 24px; }
}
</style>
