import L from 'leaflet'
import equipements from './equipements.json'

export const ZOOM_MINIMUM = 11
const ZOOM_GRILLE = 12

export function createLoader(map, cluster) {
  const tuilesChargees = new Set()
  const idsAffiches = new Set()

  function tuileDe(position) {
    return map.project(position, ZOOM_GRILLE).divideBy(256).floor()
  }

  function charger() {
    if (map.getZoom() < ZOOM_MINIMUM) {
      map.removeLayer(cluster)
      return
    }

    const limites = map.getBounds()
    const debut = tuileDe(limites.getNorthWest())
    const fin = tuileDe(limites.getSouthEast())
    const marqueurs = []
    for (let x = debut.x; x <= fin.x; x++) {
      for (let y = debut.y; y <= fin.y; y++) {
        const cle = `${x}/${y}`
        if (tuilesChargees.has(cle)) continue
        tuilesChargees.add(cle)
        for (const point of equipements.features) {
          const position = L.GeoJSON.coordsToLatLng(point.geometry.coordinates)
          const tuile = tuileDe(position)
          if (tuile.x !== x || tuile.y !== y || idsAffiches.has(point.id)) continue

          idsAffiches.add(point.id)
          marqueurs.push(L.circleMarker(position, {
            radius: 7, color: '#fff', weight: 2, fillColor: '#166756', fillOpacity: 1,
          }).bindPopup(point.properties.nom))
        }
      }
    }

    if (marqueurs.length) cluster.addLayers(marqueurs)
    cluster.addTo(map)
  }

  map.on('moveend', charger)
  charger()
  return () => map.off('moveend', charger)
}
