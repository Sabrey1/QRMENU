<script setup>
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import { Autoplay, A11y } from 'swiper/modules'
import { Swiper, SwiperSlide } from 'swiper/vue'
import 'swiper/css'

const props = defineProps({
  slides: { type: Array, required: true },
})

const swiper = shallowRef(null)
const failed = ref(new Set())
const loaded = ref(new Set())
const current = ref(0)
const reducedMotion = ref(window.matchMedia('(prefers-reduced-motion: reduce)').matches)
const visibleSlides = computed(() => props.slides.filter((slide) => !failed.value.has(slide.id)))
const activeImageLoaded = computed(() => loaded.value.has(visibleSlides.value[current.value]?.id))
const sliderKey = computed(() => `${reducedMotion.value}-${visibleSlides.value.map((slide) => slide.id).join('-')}`)
const autoplay = computed(() => visibleSlides.value.length > 1 && !reducedMotion.value
  ? { delay: 5000, disableOnInteraction: false }
  : false)
let motionQuery

function setSwiper(instance) {
  swiper.value = instance
  current.value = instance.realIndex
}

function updateMotion(event) {
  reducedMotion.value = event.matches
}

watch(() => props.slides, () => { failed.value = new Set(); loaded.value = new Set(); current.value = 0 })
onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionQuery.addEventListener('change', updateMotion)
})
onUnmounted(() => motionQuery?.removeEventListener('change', updateMotion))
</script>

<template>
  <section v-if="visibleSlides.length" class="slider" :aria-label="$t('featuredImages')">
    <Swiper
      :key="sliderKey"
      :modules="[Autoplay, A11y]"
      :autoplay="autoplay"
      :rewind="visibleSlides.length > 1"
      :speed="reducedMotion ? 0 : 350"
      @swiper="setSwiper"
      @slide-change="current = $event.realIndex"
    >
      <SwiperSlide v-for="slide in visibleSlides" :key="slide.id">
        <div v-if="!loaded.has(slide.id)" class="image-skeleton" aria-hidden="true"></div>
        <img :class="{ 'image-loading': !loaded.has(slide.id) }" :src="slide.image_url" :alt="slide.alt_text" @load="loaded.add(slide.id)" @error="failed.add(slide.id)" />
      </SwiperSlide>
    </Swiper>
    <template v-if="visibleSlides.length > 1 && activeImageLoaded">
      <button class="slider-button previous" type="button" :aria-label="$t('previousImage')" @click="swiper?.slidePrev()"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m15 5-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg></button>
      <button class="slider-button next" type="button" :aria-label="$t('nextImage')" @click="swiper?.slideNext()"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m9 5 7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg></button>
    </template>
  </section>
</template>

<style scoped>
.slider { position: relative; height: clamp(180px, 30vw, 300px); margin-bottom: 24px; overflow: hidden; border-radius: 10px; background: #eef1ed; }
.slider :deep(.swiper), .slider :deep(.swiper-slide) { width: 100%; height: 100%; }
.slider img { display: block; width: 100%; height: 100%; object-fit: cover; }
.slider img.image-loading { opacity: 0; }
.image-skeleton { position: absolute; inset: 0; background: #e9eeea; animation: skeleton-pulse 1.5s ease-in-out infinite; }
@keyframes skeleton-pulse { 50% { opacity: .5; } }
.slider-button { position: absolute; z-index: 2; top: 50%; transform: translateY(-50%); width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; padding: 0; border: 0; border-radius: 50%; color: #fff; background: rgb(0 0 0 / 55%); cursor: pointer; }
.slider-button svg { display: block; width: 22px; height: 22px; }
.slider-button:hover { background: rgb(0 0 0 / 75%); }
.previous { left: 12px; }.next { right: 12px; }
html[data-theme='dark'] .slider, html[data-theme='dark'] .image-skeleton { background: #344138; }
@media (prefers-reduced-motion: reduce) { .image-skeleton { animation: none; } }
</style>
