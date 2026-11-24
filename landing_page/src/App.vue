<script setup>
import { computed, ref } from 'vue'
import MediaFrame from './components/MediaFrame.vue'
import { media, menuAppUrl } from './content'

const menuOpen = ref(false)
const selectedCategory = ref('All')
const categories = ['All', 'Breakfast', 'Coffee', 'Drinks']
const items = [
  { name: 'Morning toast', detail: 'Avocado, egg, sourdough', price: '$5.50', category: 'Breakfast', color: 'sage', media: media.morningToast },
  { name: 'Iced latte', detail: 'Espresso, milk, ice', price: '$3.00', category: 'Coffee', color: 'sand', media: media.icedLatte },
  { name: 'Berry bowl', detail: 'Seasonal fruit, yogurt', price: '$4.50', category: 'Breakfast', color: 'pink', media: media.berryBowl },
  { name: 'Citrus soda', detail: 'Orange, lemon, soda', price: '$3.50', category: 'Drinks', color: 'yellow', media: media.citrusSoda },
]
const visibleItems = computed(() => selectedCategory.value === 'All' ? items : items.filter((item) => item.category === selectedCategory.value))
const features = [
  { icon: 'menu', title: 'A menu that stays fresh', text: 'Keep your categories, items, prices and photos up to date in one place.' },
  { icon: 'qr', title: 'One scan, easy browsing', text: 'Give guests a QR code that opens your menu right on their phones.' },
  { icon: 'spark', title: 'Made to feel like you', text: 'Choose a menu template and bring your brand to the table.' },
  { icon: 'globe', title: 'A little more welcoming', text: 'An interface in English and Khmer helps more guests feel at home.' },
]
const questions = [
  { q: 'What is a QR menu?', a: 'It is a digital version of your menu that guests can open on their phone by scanning a QR code.' },
  { q: 'Can I update my menu later?', a: 'Yes. You can manage your menu items, categories and banners from your shop account.' },
  { q: 'Do my customers need to download an app?', a: 'No. Your menu opens in a web browser on their phone.' },
  { q: 'Can I choose a different look?', a: 'Yes. Sabrey includes different menu templates for your shop.' },
]
</script>

<template>
  <div class="site-shell">
    <svg class="svg-defs" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <symbol id="icon-menu" viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></symbol>
      <symbol id="icon-qr" viewBox="0 0 24 24"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM19 14v2M14 20h2M19 19v1"/></symbol>
      <symbol id="icon-spark" viewBox="0 0 24 24"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3ZM19 15l.7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7L19 15Z"/></symbol>
      <symbol id="icon-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.5 5.5 3.5 9s-1 6.5-3.5 9c-2.5-2.5-3.5-5.5-3.5-9S9.5 5.5 12 3Z"/></symbol>
      <symbol id="icon-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>
    </svg>

    <header class="site-header">
      <div class="header-inner wrap">
        <a class="brand" href="#top" aria-label="Sabrey home"><span class="brand-icon"><i></i><i></i><i></i><i></i></span><span>sabrey<span class="brand-dot">.</span></span></a>
        <nav class="desktop-nav" aria-label="Main navigation"><a href="#features">Features</a><a href="#how-it-works">How it works</a><a href="#preview">Menu preview</a><a href="#faq">FAQs</a></nav>
        <div class="header-actions"><a class="login-link" :href="`${menuAppUrl}/login`">Log in</a><a class="button button-dark header-cta" href="#get-started">Get started</a></div>
        <button class="mobile-toggle" type="button" :aria-expanded="menuOpen" aria-controls="mobile-nav" :aria-label="menuOpen ? 'Close menu' : 'Open menu'" @click="menuOpen = !menuOpen"><span></span><span></span></button>
      </div>
      <nav v-if="menuOpen" id="mobile-nav" class="mobile-nav wrap" aria-label="Mobile navigation"><a href="#features" @click="menuOpen = false">Features</a><a href="#how-it-works" @click="menuOpen = false">How it works</a><a href="#preview" @click="menuOpen = false">Menu preview</a><a href="#faq" @click="menuOpen = false">FAQs</a><a :href="`${menuAppUrl}/login`">Log in</a></nav>
    </header>

    <main id="top">
      <section class="hero wrap">
        <div class="hero-copy">
          <div class="eyebrow hero-eyebrow"><span class="eyebrow-dot"></span> A FRESH TAKE ON YOUR MENU</div>
          <h1>Good food deserves a <span>better menu.</span></h1>
          <p class="hero-description">A beautiful digital menu for the places people love. Keep it fresh, share it with a scan, and make every first impression count.</p>
          <div class="hero-buttons"><a class="button button-dark" href="#get-started">Get started</a><a class="button button-outline" href="#preview"><span class="play-icon">▶</span> Explore the demo</a></div>
          <div class="hero-note"><span class="note-icon"><svg><use href="#icon-check"/></svg></span> Simple to manage <span class="note-divider"></span> Easy for guests</div>
        </div>
        <div class="hero-visual" aria-label="Illustration of a digital menu">
          <div class="visual-grid"></div><div class="visual-orb visual-orb-one"></div><div class="visual-orb visual-orb-two"></div>
          <div class="visual-label"><span class="label-spark">✳</span> MADE FOR GOOD TASTE</div>
          <div class="floating-card floating-qr"><div class="qr-symbol"><svg><use href="#icon-qr"/></svg></div><div><strong>Scan & explore</strong><span>Your menu, right here.</span></div></div>
          <div class="phone hero-phone"><div class="phone-top"><span>9:41</span><span class="phone-speaker"></span><span>●●●</span></div><div class="phone-screen"><div class="phone-brand"><span class="phone-logo">S</span><span>the good table<small>FOOD & COFFEE</small></span><span class="phone-more">•••</span></div><div class="phone-welcome"><span>FRESHLY MADE, ALWAYS</span><strong>A little something<br>for everyone.</strong></div><div class="phone-categories"><span class="active">All</span><span>Breakfast</span><span>Coffee</span></div><div class="phone-section-title">House favorites <span>✳</span></div><div class="phone-items"><div class="phone-item"><div><strong>Morning toast</strong><small>Made fresh daily</small><b>$5.50</b></div><div class="phone-item-image sage"><span>✳</span></div></div><div class="phone-item"><div><strong>Iced latte</strong><small>Your daily favorite</small><b>$3.00</b></div><div class="phone-item-image sand"><span>☼</span></div></div><div class="phone-item"><div><strong>Berry bowl</strong><small>A little bit of happy</small><b>$4.50</b></div><div class="phone-item-image pink"><span>✽</span></div></div></div></div></div>
          <div class="floating-card floating-update"><span class="update-check">✓</span><div><strong>Looking good!</strong><span>Made for your brand</span></div></div>
          <div class="visual-caption">YOUR MENU, IN THEIR HANDS <span>✳</span></div>
        </div>
      </section>

      <div class="trust-strip"><div class="wrap trust-inner"><span class="trust-lead">A better experience for</span><span>Restaurants</span><i></i><span>Cafés</span><i></i><span>Retail shops</span><i></i><span>And more</span><span class="trust-end">GOOD FOR BUSINESS. GREAT FOR GUESTS.</span></div></div>
      <section id="features" class="section wrap feature-section"><div class="section-heading split-heading"><div><span class="eyebrow"><span class="eyebrow-dot"></span> THOUGHTFULLY SIMPLE</span><h2>Everything your menu needs.<br><span>Nothing it doesn’t.</span></h2></div><p>From the first scan to the last look, make it easier for guests to discover what you do best.</p></div><div class="feature-grid"><article v-for="feature in features" :key="feature.title" class="feature"><span class="feature-icon"><svg><use :href="`#icon-${feature.icon}`"/></svg></span><h3>{{ feature.title }}</h3><p>{{ feature.text }}</p></article></div></section>

      <section id="preview" class="preview-section"><div class="wrap preview-layout"><div class="preview-copy"><span class="eyebrow light-eyebrow"><span class="eyebrow-dot"></span> A LITTLE LOOK AROUND</span><h2>Meet your menu’s<br><em>new look.</em></h2><p>Your menu should feel like an extension of your space. Give customers an easy way to browse, discover, and find their next favorite.</p><ul class="check-list"><li><svg><use href="#icon-check"/></svg> Clean, mobile-friendly layouts</li><li><svg><use href="#icon-check"/></svg> Categories that are easy to explore</li><li><svg><use href="#icon-check"/></svg> Your products, prices and personality</li></ul><a href="#how-it-works" class="text-link">See how it works <span>+</span></a></div><div class="preview-stage"><div class="browser-window"><div class="browser-top"><span class="browser-dots"><i></i><i></i><i></i></span><div>yourshop.sabrey.xyz</div><span class="browser-square">□</span></div><div class="demo-menu"><div class="demo-header"><span class="demo-logo">S</span><div><strong>The Good Table</strong><small>GOOD FOOD, GOOD COMPANY</small></div><span class="demo-language">EN⌄</span></div><MediaFrame :media="media.menuBanner" label="A little something for everyone" class="demo-banner" /><div class="demo-content"><div class="demo-category-nav" aria-label="Preview categories"><button v-for="category in categories" :key="category" type="button" :class="{ active: selectedCategory === category }" :aria-pressed="selectedCategory === category" @click="selectedCategory = category">{{ category }}</button></div><div class="demo-title"><div><small>MADE WITH CARE</small><h3>{{ selectedCategory === 'All' ? 'Our favorites' : selectedCategory }}</h3></div><span>✳</span></div><div class="demo-items"><article v-for="item in visibleItems" :key="item.name" class="demo-item"><MediaFrame :class="['demo-item-photo', item.color]" :media="item.media" /><div><strong>{{ item.name }}</strong><small>{{ item.detail }}</small><b>{{ item.price }}</b></div></article></div></div></div></div><div class="preview-badge"><span>✳</span> MADE TO BE SHARED</div></div></div></section>

      <section id="how-it-works" class="section wrap how-section"><div class="section-heading centered"><span class="eyebrow"><span class="eyebrow-dot"></span> NICE AND EASY</span><h2>From your kitchen<br>to their screen.</h2><p>Getting your menu in front of your guests can be refreshingly simple.</p></div><div class="steps-grid"><article class="step"><div class="step-art step-art-one"><div class="mini-window"><span></span><span></span><span></span><div><i></i><i></i><i></i></div></div><div class="mini-plus">+</div></div><div class="step-label">01 / MAKE IT YOURS</div><h3>Build your menu</h3><p>Add your shop details, categories, items, and prices in one place.</p></article><article class="step"><div class="step-art step-art-two"><div class="template-stack"><div></div><div></div><div><span>YOUR<br>MENU.</span><i>✳</i></div></div></div><div class="step-label">02 / FIND YOUR LOOK</div><h3>Choose a style</h3><p>Pick a template that feels right at home with your business.</p></article><article class="step"><div class="step-art step-art-three"><div class="qr-paper"><svg><use href="#icon-qr"/></svg><span>SCAN ME</span></div><div class="scan-ring"></div></div><div class="step-label">03 / SHARE IT</div><h3>Let guests scan</h3><p>Share your menu’s QR code and let your guests explore on their phones.</p></article></div></section>

      <section class="story-section wrap"><div class="story-media"><MediaFrame :media="media.story" label="Made for the places people love" /></div><div class="story-copy"><span class="eyebrow"><span class="eyebrow-dot"></span> MADE FOR YOUR EVERYDAY</span><h2>More time for<br><em>what matters.</em></h2><p>A good menu is just the beginning. Spend less time worrying about the little things and more time making your guests feel welcome.</p><a class="button button-dark" href="#get-started">Get started</a></div></section>
      <section id="faq" class="section wrap faq-section"><div class="faq-intro"><span class="eyebrow"><span class="eyebrow-dot"></span> GOOD TO KNOW</span><h2>A few things<br>you might ask.</h2><p>Everything you need to know to get started.</p></div><div class="faq-list"><details v-for="question in questions" :key="question.q"><summary>{{ question.q }}<span></span></summary><p>{{ question.a }}</p></details></div></section>
      <section id="get-started" class="cta-section wrap"><div class="cta-decoration cta-deco-one">✳</div><div class="cta-decoration cta-deco-two">✳</div><span class="eyebrow light-eyebrow"><span class="eyebrow-dot"></span> LET’S MAKE SOMETHING GOOD</span><h2>Ready when<br><em>you are.</em></h2><p>Give your menu a little more room to shine.</p><a class="button button-lime" :href="`${menuAppUrl}/login`">Go to Sabrey</a><small>Already have an account? Sign in to manage your menu.</small></section>
    </main>

    <footer class="footer wrap"><div class="footer-top"><div><a class="brand" href="#top"><span class="brand-icon"><i></i><i></i><i></i><i></i></span><span>sabrey<span class="brand-dot">.</span></span></a><p>Good things start at the table.</p></div><div class="footer-links"><div><strong>EXPLORE</strong><a href="#features">Features</a><a href="#how-it-works">How it works</a><a href="#preview">Menu preview</a></div><div><strong>GET STARTED</strong><a :href="`${menuAppUrl}/login`">Log in</a><a href="#faq">FAQs</a></div></div></div><div class="footer-bottom"><span>© {{ new Date().getFullYear() }} Sabrey. All rights reserved.</span><span>MADE FOR GOOD TASTE <b>✳</b></span></div></footer>
  </div>
</template>
