import L from 'leaflet'
import { chargerEquipements } from '../api.js'

export const ZOOM_MINIMUM = 11
const ZOOM_GRILLE = 12

export function createLoader(map, cluster, afficherMessage, selectionnerEquipement) {
  const tuiles = new Map()
  const idsAffiches = new Set()
  const controleur = new AbortController()
  let vue = 0

  function tuileDe(position) {
    return map.project(position, ZOOM_GRILLE).divideBy(256).floor()
  }

  async function chargerTuile(x, y) {
    const nordOuest = map.unproject(L.point(x, y).multiplyBy(256), ZOOM_GRILLE)
    const sudEst = map.unproject(L.point(x + 1, y + 1).multiplyBy(256), ZOOM_GRILLE)
    const bbox = [nordOuest.lng, sudEst.lat, sudEst.lng, nordOuest.lat]
    const points = await chargerEquipements(bbox, controleur.signal)
    if (controleur.signal.aborted) return 0

    const marqueurs = []
    for (const point of points) {
      if (idsAffiches.has(point.id)) continue
      const position = L.GeoJSON.coordsToLatLng(point.geometry.coordinates)
      const nom = document.createElement('span')
      nom.textContent = point.properties.nom
      marqueurs.push(L.circleMarker(position, {
        radius: 7, color: '#fff', weight: 2, fillColor: '#166756', fillOpacity: 1,
      }).bindPopup(nom).on('click', () => selectionnerEquipement(point.id)))
      idsAffiches.add(point.id)
    }
    if (marqueurs.length) cluster.addLayers(marqueurs)
    return points.length
  }

  async function charger() {
    const vueDemandee = ++vue
    if (map.getZoom() < ZOOM_MINIMUM) {
      map.removeLayer(cluster)
      afficherMessage('Zoomez pour voir les équipements')
      return
    }
    cluster.addTo(map)
    afficherMessage('')
    const limites = map.getBounds()
    const debut = tuileDe(limites.getNorthWest())
    const fin = tuileDe(limites.getSouthEast())
    const requetes = []
    for (let x = debut.x; x <= fin.x; x++) {
      for (let y = debut.y; y <= fin.y; y++) {
        const cle = `${x}/${y}`
        // Le cache partage aussi les requêtes en cours entre deux déplacements.
        if (!tuiles.has(cle)) {
          tuiles.set(cle, chargerTuile(x, y).catch(erreur => {
            tuiles.delete(cle)
            throw erreur
          }))
        }
        requetes.push(tuiles.get(cle))
      }
    }

    const resultats = await Promise.allSettled(requetes)
    if (vueDemandee !== vue || controleur.signal.aborted) return
    if (resultats.some(resultat => resultat.status === 'rejected')) {
      afficherMessage('Chargement incomplet. Déplacez la carte pour réessayer.')
    } else if (resultats.every(resultat => resultat.value === 0)) {
      afficherMessage('Aucun équipement dans cette zone.')
    }
  }

  map.on('moveend', charger)
  charger()
  return () => {
    map.off('moveend', charger)
    controleur.abort()
  }
}
