export async function chargerEquipements(bbox, signal) {
  const parametres = new URLSearchParams({ in_bbox: bbox.join(',') })
  const reponse = await fetch(`/api/equipements/?${parametres}`, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!reponse.ok) throw new Error(`Chargement des équipements impossible (HTTP ${reponse.status})`)
  const collection = await reponse.json()
  return collection.features
}
