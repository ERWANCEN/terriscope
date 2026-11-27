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

export async function chercherAdresses(texte, signal) {
  const parametres = new URLSearchParams({ q: texte, index: 'address', limit: '5' })
  const collection = await lireJson(`/api/adresses/?${parametres}`, signal)
  return collection.features
    .filter(({ properties, geometry }) => properties?.label && geometry?.type === 'Point'
      && Number.isFinite(geometry.coordinates?.[0]) && Number.isFinite(geometry.coordinates?.[1]))
    .map(({ properties, geometry }) => ({ adresse: properties.label, coordonnees: geometry.coordinates }))
}

export function chargerEmpriseVille(ville, signal) {
  return lireJson(`/api/equipements/emprise-ville/?${new URLSearchParams({ ville })}`, signal)
}

export function chargerFicheEquipement(id, signal) {
  return lireJson(`/api/equipements/${encodeURIComponent(id)}/`, signal)
}


// --- Authentification & Implantations privées (Rôle C) ---

const CLE_TOKEN = 'terriscope_token'

export function lireToken() {
  return localStorage.getItem(CLE_TOKEN)
}

export function enregistrerToken(token) {
  localStorage.setItem(CLE_TOKEN, token)
}

export function supprimerToken() {
  localStorage.removeItem(CLE_TOKEN)
}

async function requeteApi(url, options = {}) {
  const token = lireToken()
  const headers = {
    Accept: 'application/json',
    ...options.headers,
  }
  if (options.body) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Token ${token}`

  const reponse = await fetch(url, { ...options, headers })

  if (reponse.status === 204) return null

  const donnees = await reponse.json().catch(() => null)
  if (!reponse.ok) {
    const message = extraireMessageErreur(donnees) || `Erreur HTTP ${reponse.status}`
    throw new Error(message)
  }
  return donnees
}

function extraireMessageErreur(donnees) {
  if (!donnees || typeof donnees !== 'object') return null
  if (donnees.detail) return donnees.detail
  if (donnees.non_field_errors) return donnees.non_field_errors.join(' ')
  return Object.values(donnees).flat().join(' ')
}

export async function connecter(username, password) {
  const donnees = await requeteApi('/api/auth/token/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  enregistrerToken(donnees.token)
  return donnees.token
}

export async function inscrire(username, password) {
  const donnees = await requeteApi('/api/auth/register/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  enregistrerToken(donnees.token)
  return donnees.token
}

export function deconnecter() {
  supprimerToken()
}

export function chargerUtilisateur() {
  return requeteApi('/api/auth/me/')
}

export async function chargerImplantations() {
  const collection = await requeteApi('/api/implantations/')
  return collection.features || []
}

export function creerImplantation({ titre, domaine3, commentaire, lon, lat }) {
  return requeteApi('/api/implantations/', {
    method: 'POST',
    body: JSON.stringify({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [lon, lat] },
      properties: {
        titre,
        domaine3: domaine3 || null,
        commentaire: commentaire || '',
      },
    }),
  })
}

export function modifierImplantation(id, { titre, domaine3, commentaire, lon, lat }) {
  const payload = {
    type: 'Feature',
    properties: {
      titre,
      domaine3: domaine3 || null,
      commentaire: commentaire || '',
    },
  }
  if (lon != null && lat != null) {
    payload.geometry = { type: 'Point', coordinates: [lon, lat] }
  }
  return requeteApi(`/api/implantations/${encodeURIComponent(id)}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function supprimerImplantation(id) {
  return requeteApi(`/api/implantations/${encodeURIComponent(id)}/`, {
    method: 'DELETE',
  })
}
