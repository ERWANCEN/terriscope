async function lireJson(url, signal) {
  const reponse = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!reponse.ok) throw new Error(`Chargement des équipements impossible (HTTP ${reponse.status})`)
  return reponse.json()
}

export async function chargerEquipements(bbox, signal) {
  const parametres = new URLSearchParams({ in_bbox: bbox.join(',') })
  const collection = await lireJson(`/api/equipements/?${parametres}`, signal)
  return collection.features
}

export function chargerFicheEquipement(id, signal) {
  return lireJson(`/api/equipements/${encodeURIComponent(id)}/`, signal)
}
