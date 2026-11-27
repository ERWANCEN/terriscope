<script setup>
import { onUnmounted, ref } from 'vue'
import { chercherAdresses } from '../api.js'

defineProps({ adresse: String })
const emit = defineEmits(['localiser', 'effacer'])
const saisie = ref('')
const champ = ref(null)
const resultats = ref([])
const message = ref('')
const chargement = ref(false)
let requete

function annulerRecherche() {
  requete?.abort()
  chargement.value = false
  resultats.value = []
  message.value = ''
}

async function rechercher() {
  const texte = saisie.value.trim()
  annulerRecherche()
  if (texte.length < 3) return
  requete = new AbortController()
  const { signal } = requete
  chargement.value = true
  message.value = 'Recherche en cours…'
  try {
    const adresses = await chercherAdresses(texte, signal)
    if (signal.aborted) return
    resultats.value = adresses
    message.value = adresses.length
      ? 'Choisissez une adresse dans la liste.'
      : 'Aucune adresse trouvée. Précisez la rue, le code postal ou la commune.'
  } catch {
    if (!signal.aborted) message.value = 'La recherche d’adresse est indisponible. Réessayez dans un instant.'
  } finally {
    if (!signal.aborted) chargement.value = false
  }
}

function localiser(resultat) {
  annulerRecherche()
  saisie.value = resultat.adresse
  emit('localiser', resultat)
}

function effacer() {
  annulerRecherche()
  saisie.value = ''
  emit('effacer')
  champ.value.focus()
}

onUnmounted(() => requete?.abort())
</script>

<template>
  <form class="recherche-adresse" role="search" aria-label="Recherche d’adresse" @submit.prevent="rechercher">
    <label for="adresse-postale">Rechercher une adresse</label>
    <div class="saisie">
      <input id="adresse-postale" ref="champ" v-model="saisie" type="search" autocomplete="off"
        maxlength="200" placeholder="Rue, code postal, commune" @input="annulerRecherche">
      <button type="submit" :disabled="chargement || saisie.trim().length < 3">Rechercher</button>
    </div>
    <p role="status">{{ message }}</p>
    <ul v-if="resultats.length" aria-label="Adresses trouvées">
      <li v-for="point in resultats" :key="point.adresse + point.coordonnees">
        <button type="button" @click="localiser(point)">
          {{ point.adresse }}<small v-if="point.horsZone"> · Hors zone</small>
        </button>
      </li>
    </ul>
    <div v-if="adresse" class="selection">
      <span role="status">Adresse sur la carte · {{ adresse }}</span>
      <button type="button" @click="effacer">Effacer le repère</button>
    </div>
  </form>
</template>

<style scoped>
.recherche-adresse { margin-bottom: .65rem; padding: .8rem 1rem; border: 1px solid #ccd4c9; border-radius: .65rem; background: #fdfdf8; }
label { display: block; margin-bottom: .4rem; font-weight: 650; }
.saisie, .selection { display: flex; align-items: center; gap: .5rem; }
input, button { font: inherit; border: 1px solid #9caea3; border-radius: .3rem; padding: .45rem .6rem; }
input { flex: 1; min-width: 0; }
button { background: white; color: #175749; cursor: pointer; }
button[type=submit] { background: #175749; color: white; border-color: #175749; }
button:disabled { opacity: .55; cursor: default; }
p, .selection { margin: .5rem 0 0; }
p:empty { margin: 0; }
ul { list-style: none; margin: .35rem 0 0; padding: 0; }
li button { width: 100%; text-align: left; border: 0; background: transparent; }
li button:hover, li button:focus-visible { background: #e4efe7; }
.selection { flex-wrap: wrap; font-size: .9rem; }
</style>
