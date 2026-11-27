import L from 'leaflet'

// Icône SVG violette distincte des points BPE publics (évite les soucis de chemins d'images Leaflet)
const iconeImplantation = L.divIcon({
    className: 'implantation-marker',
    html: `
    <svg width="28" height="36" viewBox="0 0 28 36" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 1C6.8 1 1 6.8 1 14c0 9.5 13 21 13 21s13-11.5 13-21C27 6.8 21.2 1 14 1z"
            fill="#7c3aed" stroke="#ffffff" stroke-width="2"/>
      <circle cx="14" cy="14" r="5" fill="#ffffff"/>
    </svg>
  `,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    tooltipAnchor: [0, -32],
})

export function creerCoucheImplantations(map, { onSelect } = {}) {
    const groupe = L.layerGroup().addTo(map)

    function afficher(features = []) {
        groupe.clearLayers()

        for (const feature of features) {
            const coords = feature?.geometry?.coordinates
            if (!coords || coords.length < 2) continue

            // GeoJSON stocke [lon, lat], tandis que Leaflet attend [lat, lon]
            const [lon, lat] = coords
            const titre = feature.properties?.titre || 'Implantation sans titre'

            const tooltipEl = document.createElement('span')
            tooltipEl.textContent = titre

            const marqueur = L.marker([lat, lon], { icon: iconeImplantation })
            marqueur.bindTooltip(tooltipEl, { direction: 'top' })

            if (typeof onSelect === 'function') {
                marqueur.on('click', () => onSelect(feature))
            }

            marqueur.addTo(groupe)
        }
    }

    function vider() {
        groupe.clearLayers()
    }

    function detruire() {
        groupe.clearLayers()
        map.removeLayer(groupe)
    }

    return { afficher, vider, detruire, layer: groupe }
}