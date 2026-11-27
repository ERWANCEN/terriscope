<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { createLoader } from '../map/loader.js'

const conteneur = ref(null)
const emit = defineEmits(['selection'])
const message = ref('')
let carte
let arreterChargement

onMounted(() => {
  carte = L.map(conteneur.value, { maxZoom: 19, zoomControl: false })
    .setView([47.3941, 0.6848], 13)
  L.control.zoom({ zoomInTitle: 'Zoomer', zoomOutTitle: 'Dézoomer' }).addTo(carte)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(carte)

  const clusters = L.markerClusterGroup({
    animate: false, maxClusterRadius: 46, showCoverageOnHover: false,
  })
  arreterChargement = createLoader(carte, clusters,
    texte => { message.value = texte },
    id => emit('selection', id),
  )
})

onUnmounted(() => {
  arreterChargement?.()
  carte?.remove()
})
</script>

<template>
  <section class="cadre" aria-label="Carte interactive des équipements">
    <div ref="conteneur" class="carte"></div>
    <p v-if="message" class="indication" role="status">{{ message }}</p>
  </section>
</template>

<style scoped>
.cadre { position: relative; }
.carte {
  height: max(58vh, calc(100dvh - 13rem));
  border: 1px solid #ccd4c9;
  border-radius: .65rem;
  background: #e3e9e3;
}
.indication {
  position: absolute;
  z-index: 500;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: max-content;
  max-width: 90%;
  margin: 0;
  padding: .65rem 1rem;
  border-radius: .4rem;
  background: #183c35;
  color: white;
  font-size: .9rem;
}
.carte :deep(.marker-cluster) { background: #17665640; }
.carte :deep(.marker-cluster div) { background: #175749; color: white; font-weight: bold; }
</style>
