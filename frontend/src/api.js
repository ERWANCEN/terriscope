async function lireJson(url, signal) {
  const reponse = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!reponse.ok) throw new Error(`Échec de la requête (HTTP ${reponse.status})`)
  return reponse.json()
}

export async function chargerEquipements(bbox, signal, filtres) {
  const parametres = new URLSearchParams({ in_bbox: bbox.join(',') })
  if (filtres.villes.length) parametres.set('ville', filtres.villes.join(','))
  // Django croise les niveaux de domaine. Une requête par niveau sélectionné
  // permet de réunir, par exemple, un domaine entier et un type d'un autre domaine.
  const recherches = Object.entries(filtres.domaines).map(([niveau, codes]) => {
    const recherche = new URLSearchParams(parametres)
    recherche.set(niveau, codes.join(','))
    return recherche
  })
  if (!recherches.length) recherches.push(parametres)
  const collections = await Promise.all(recherches.map(recherche =>
    lireJson(`/api/equipements/?${recherche}`, signal)
  ))
  return collections.flatMap(collection => collection.features)
}

export function chargerDomaines(signal) {
  return lireJson('/api/domaines/', signal)
}

export function chercherVilles(texte, signal) {
  return lireJson(`/api/villes/?${new URLSearchParams({ search: texte })}`, signal)
}

export function chargerFicheEquipement(id, signal) {
  return lireJson(`/api/equipements/${encodeURIComponent(id)}/`, signal)
}
