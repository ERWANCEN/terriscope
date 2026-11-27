<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { createLoader } from '../map/loader.js'
import { creerCoucheImplantations } from '../map/implantationsLayer.js'

const conteneur = ref(null)
const props = defineProps({
  filtres: { type: Object, required: true },
  implantations: { type: Array, required: true },
  modeAjout: Boolean,
})
const emit = defineEmits(['selection', 'position', 'implantation'])
const message = ref('')
let carte
let arreterChargement
let couchePrivee

onMounted(() => {
  carte = L.map(conteneur.value, { maxZoom: 19, zoomControl: false })
    .setView([47.3941, 0.6848], 13)
  L.control.zoom({ zoomInTitle: 'Zoomer', zoomOutTitle: 'Dézoomer' }).addTo(carte)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(carte)

  couchePrivee = creerCoucheImplantations(carte, {
    onSelect: feature => emit('implantation', feature),
  })
  watch(() => props.implantations, features => couchePrivee.afficher(features), { immediate: true })
  watch(() => props.modeAjout, actif => { if (actif) carte.closePopup() })
  carte.on('click', ({ latlng }) => {
    if (props.modeAjout) emit('position', { lon: latlng.lng, lat: latlng.lat })
  })

  const clusters = L.markerClusterGroup({
    animate: false, maxClusterRadius: 46, showCoverageOnHover: false,
  })
  watch(() => props.filtres, filtres => {
    arreterChargement?.()
    clusters.clearLayers()
    arreterChargement = createLoader(carte, clusters,
      texte => { message.value = texte },
      id => emit('selection', id),
      filtres,
    )
  }, { immediate: true })
})

onUnmounted(() => {
  arreterChargement?.()
  couchePrivee?.detruire()
  carte?.remove()
})
</script>

<template>
  <section class="cadre" aria-label="Carte interactive des équipements">
    <div ref="conteneur" class="carte" :data-placement="modeAjout || null"></div>
    <p v-if="modeAjout || message" class="indication" role="status">
      {{ modeAjout ? 'Cliquez sur la carte pour placer votre implantation.' : message }}
    </p>
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
.carte[data-placement] { cursor: crosshair; }
.carte[data-placement] :deep(.leaflet-interactive) { pointer-events: none; }
.indication { pointer-events: none; }
.carte :deep(.marker-cluster div) { background: #175749; color: white; font-weight: bold; }
</style>
