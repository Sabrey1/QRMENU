<script setup>
defineProps({
  media: { type: Object, required: true },
  label: { type: String, default: '' },
})
</script>

<template>
  <div class="media-frame">
    <img v-if="media.type === 'image' && media.src" :src="media.src" :alt="media.alt || ''" loading="lazy" />
    <video v-else-if="media.type === 'video' && media.src" :src="media.src" :aria-label="media.alt || label" controls muted loop playsinline></video>
    <div v-else class="media-placeholder"><div class="placeholder-art" aria-hidden="true"><span>✳</span><i></i><i></i></div><span class="placeholder-label">{{ label }}</span></div>
  </div>
</template>

<style scoped>
.media-frame { overflow: hidden; }
img, video { display: block; width: 100%; height: 100%; object-fit: cover; }
.media-placeholder { position: relative; width: 100%; height: 100%; min-height: 140px; overflow: hidden; background: #dce8d5; }
.placeholder-art { position: absolute; inset: 0; display: grid; place-items: center; overflow: hidden; color: #719277; }
.placeholder-art span { position: relative; z-index: 1; font-size: clamp(4rem, 9vw, 8rem); line-height: 1; }
.placeholder-art i { position: absolute; width: 48%; aspect-ratio: 1; border: 1px solid rgb(79 124 88 / 20%); border-radius: 50%; }
.placeholder-art i:last-child { width: 70%; }
.placeholder-label { position: absolute; bottom: 18px; left: 20px; right: 20px; color: #385f42; font-size: .72rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
</style>
