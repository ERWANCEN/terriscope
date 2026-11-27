<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { chargerDomaines, chercherVilles } from '../api.js'

const emit = defineEmits(['filtrer'])
const domaines = ref([])
const selection = ref(new Set())
const ouverts = ref(new Set())
const villes = ref([])
const recherche = ref('')
const suggestions = ref([])
const erreurDomaines = ref(false)
const erreurVilles = ref(false)
const controleur = new AbortController()

function preparerDomaine(domaine, niveau) {
  const enfants = (domaine.enfants || []).map(enfant => preparerDomaine(enfant, niveau + 1))
  const feuilles = enfants.length ? enfants.flatMap(enfant => enfant.feuilles) : [domaine.code]
  return { ...domaine, niveau, enfants, feuilles }
}

async function lireDomaines() {
  erreurDomaines.value = false
  try {
    const arbre = await chargerDomaines(controleur.signal)
    domaines.value = arbre.map(domaine => preparerDomaine(domaine, 1))
  } catch {
    if (!controleur.signal.aborted) erreurDomaines.value = true
  }
}
onMounted(lireDomaines)
onUnmounted(() => controleur.abort())

const lignes = computed(() => {
  const visibles = []
  function ajouter(domaine) {
    const coches = domaine.feuilles.filter(code => selection.value.has(code)).length
    visibles.push({ domaine, coche: coches === domaine.feuilles.length, partiel: coches > 0 && coches < domaine.feuilles.length })
    if (ouverts.value.has(domaine.code)) domaine.enfants.forEach(ajouter)
  }
  domaines.value.forEach(ajouter)
  return visibles
})

function appliquer() {
  const codes = {}
  function retenir(domaine) {
    if (domaine.feuilles.every(code => selection.value.has(code))) {
      const niveau = `domaine${domaine.niveau}`
      codes[niveau] ??= []
      codes[niveau].push(domaine.code)
    } else {
      domaine.enfants.forEach(retenir)
    }
  }
  domaines.value.forEach(retenir)
  emit('filtrer', { domaines: codes, villes: [...villes.value] })
}

function cocher(domaine, coche) {
  for (const code of domaine.feuilles) {
    if (coche) selection.value.add(code)
    else selection.value.delete(code)
  }
  appliquer()
}

function deplier(code) {
  if (ouverts.value.has(code)) ouverts.value.delete(code)
  else ouverts.value.add(code)
}

watch(recherche, (valeur, _, nettoyer) => {
  const texte = valeur.trim()
  erreurVilles.value = false
  if (!texte) {
    suggestions.value = []
    return
  }
  const requete = new AbortController()
  const delai = setTimeout(async () => {
    try {
      const noms = await chercherVilles(texte, requete.signal)
      if (!requete.signal.aborted) suggestions.value = noms
    } catch {
      if (!requete.signal.aborted) {
        suggestions.value = []
        erreurVilles.value = true
      }
    }
  }, 180)
  nettoyer(() => {
    clearTimeout(delai)
    requete.abort()
  })
})

const villesDisponibles = computed(() => suggestions.value.filter(nom => !villes.value.includes(nom)))
const villeChoisie = computed(() => villesDisponibles.value.find(nom =>
  nom.toLocaleLowerCase('fr') === recherche.value.trim().toLocaleLowerCase('fr')
))

function ajouterVille() {
  if (!villeChoisie.value) return
  villes.value.push(villeChoisie.value)
  recherche.value = ''
  appliquer()
}

function retirerVille(ville) {
  villes.value = villes.value.filter(nom => nom !== ville)
  appliquer()
}

function effacer() {
  villes.value = []
  selection.value.clear()
  recherche.value = ''
  appliquer()
}
</script>

<template>
  <aside class="filtres" aria-label="Filtres de la carte">
    <header>
      <h2>Filtres</h2>
      <button v-if="selection.size || villes.length" type="button" @click="effacer">Tout effacer</button>
    </header>
    <form @submit.prevent="ajouterVille">
      <label for="ville">Villes</label>
      <div class="saisie">
        <input id="ville" v-model="recherche" list="suggestions-villes" placeholder="Rechercher une ville" autocomplete="off">
        <datalist id="suggestions-villes">
          <option v-for="nom in villesDisponibles" :key="nom" :value="nom" />
        </datalist>
        <button type="submit" :disabled="!villeChoisie">Ajouter</button>
      </div>
      <p v-if="erreurVilles" role="status">Recherche indisponible. Relancez la saisie.</p>
      <ul v-if="villes.length" class="villes">
        <li v-for="ville in villes" :key="ville">
          <button type="button" :aria-label="`Retirer ${ville}`" @click="retirerVille(ville)">{{ ville }} ×</button>
        </li>
      </ul>
    </form>
    <fieldset>
      <legend>Domaines</legend>
      <p v-if="erreurDomaines" role="status">
        Domaines indisponibles. <button type="button" @click="lireDomaines">Réessayer</button>
      </p>
      <div class="arbre">
        <div v-for="{ domaine, coche, partiel } in lignes" :key="domaine.code"
          class="ligne" :style="{ paddingInlineStart: (domaine.niveau - 1) * .85 + 'rem' }">
          <button v-if="domaine.enfants.length" type="button" class="deplier"
            :aria-label="domaine.libelle" :aria-expanded="ouverts.has(domaine.code)" @click="deplier(domaine.code)">
            {{ ouverts.has(domaine.code) ? '▾' : '▸' }}
          </button>
          <label>
            <input type="checkbox" :value="domaine.code" :checked="coche" :indeterminate="partiel"
              @change="cocher(domaine, $event.target.checked)">
            {{ domaine.libelle }}
          </label>
        </div>
      </div>
    </fieldset>
  </aside>
</template>

<style scoped>
.filtres { align-self: start; padding: 1rem; background: #fdfdf8; border: 1px solid #ccd4c9; border-radius: .65rem; }
header, .saisie, .ligne, .ligne label { display: flex; align-items: center; gap: .4rem; }
header { justify-content: space-between; margin-bottom: 1rem; }
h2 { margin: 0; font: 500 1.5rem 'Spectral', Georgia, serif; }
form > label, legend { display: block; font-weight: 650; margin-bottom: .4rem; }
button, input { font: inherit; }
button { color: #175749; border: 1px solid #c7d1c7; background: #fff; border-radius: .3rem; padding: .35rem .5rem; cursor: pointer; }
button:disabled { opacity: .55; cursor: default; }
.saisie input { min-width: 0; width: 100%; padding: .4rem; border: 1px solid #9caea3; border-radius: .3rem; }
.villes { display: flex; flex-wrap: wrap; gap: .3rem; padding: 0; margin: .6rem 0 0; list-style: none; }
.villes button { border-radius: 1rem; background: #e4efe7; }
fieldset { min-width: 0; margin: 1rem 0 0; padding: 0; border: 0; }
.arbre { max-height: 48vh; overflow: auto; }
.ligne { min-height: 2rem; gap: .15rem; }
.ligne label { align-items: baseline; padding-block: .2rem; cursor: pointer; }
.ligne input { margin: 0; accent-color: #175749; }
.deplier { flex: none; width: 1.65rem; border: 0; background: transparent; }
@media (max-width: 760px) { .arbre { max-height: 12rem; } }
</style>
