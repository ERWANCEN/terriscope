<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { createLoader, ZOOM_MINIMUM } from '../map/loader.js'
import { creerCoucheImplantations } from '../map/implantationsLayer.js'
import { chargerEmpriseVille } from '../api.js'

const conteneur = ref(null)
const props = defineProps({
  filtres: { type: Object, required: true },
  implantations: { type: Array, required: true },
  modeAjout: Boolean,
  destination: Object,
})
const emit = defineEmits(['selection', 'position', 'implantation'])
const message = ref('')
const erreurNavigation = ref('')
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

  watch(() => props.destination, async (cible, _, nettoyer) => {
    erreurNavigation.value = ''
    if (!cible) return
    const requete = new AbortController()
    nettoyer(() => {
      requete.abort()
      carte.stop()
    })
    let centre, zoom
    if (cible.ville) {
      try {
        const [ouest, sud, est, nord] = await chargerEmpriseVille(cible.ville, requete.signal)
        if (requete.signal.aborted) return
        const limites = L.latLngBounds([sud, ouest], [nord, est])
        centre = limites.getCenter()
        zoom = Math.max(ZOOM_MINIMUM, Math.min(15, carte.getBoundsZoom(limites, false, L.point(48, 48))))
      } catch {
        if (!requete.signal.aborted) erreurNavigation.value = `Impossible de centrer la carte sur ${cible.ville}.`
        return
      }
    } else {
      centre = L.GeoJSON.coordsToLatLng(cible.coordonnees)
      zoom = Math.max(16, carte.getZoom())
      if (cible.adresse || cible.equipement) {
        const repere = L.marker(centre, {
          icon: L.divIcon({ className: cible.equipement ? 'repere-equipement' : 'repere-adresse', iconSize: [22, 22] }),
          title: cible.equipement?.nom ?? cible.adresse,
          interactive: false,
          keyboard: false,
          zIndexOffset: 1000,
        }).addTo(carte)
        nettoyer(() => repere.remove())
      }
    }
    const animer = !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    conteneur.value.scrollIntoView({ block: 'nearest', inline: 'nearest' })
    carte.flyTo(centre, zoom, { animate: animer, duration: .8 })
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
    <p v-if="destination?.horsZone" class="indication hors-zone" role="status">
      Cette adresse est hors zone. TerriScope couvre les équipements du Centre-Val de Loire.
    </p>
    <p v-if="modeAjout || erreurNavigation || message" class="indication" role="status">
      {{ modeAjout ? 'Cliquez sur la carte pour placer votre implantation.' : erreurNavigation || message }}
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
.carte :deep(.repere-equipement) {
  pointer-events: none;
  border: 3px solid white;
  border-radius: 50%;
  background: #175749;
  box-shadow: 0 0 0 3px #175749;
}
.carte :deep(.repere-adresse) {
  pointer-events: none;
  border: 3px solid white;
  border-radius: 50%;
  background: #bd4a14;
  box-shadow: 0 0 0 2px #80300e, 0 1px 7px #0005;
}
.carte[data-placement] { cursor: crosshair; }
.carte[data-placement] :deep(.leaflet-interactive) { pointer-events: none; }
.indication { pointer-events: none; }
.hors-zone {
  top: .65rem;
  bottom: auto;
  max-width: calc(100% - 6rem);
  background: #fff4d9;
  border: 1px solid #b48a46;
  color: #573a0c;
}
.carte :deep(.marker-cluster div) { background: #175749; color: white; font-weight: bold; }
</style>
