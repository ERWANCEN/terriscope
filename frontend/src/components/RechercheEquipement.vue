<script setup>
import { ref, watch } from 'vue'
import { chercherEquipements } from '../api.js'

const emit = defineEmits(['selection'])
const saisie = ref('')
const resultats = ref([])
const message = ref('')

watch(saisie, (valeur, _, nettoyer) => {
  resultats.value = []
  message.value = ''
  const nom = valeur.trim()
  if (nom.length < 3) return

  const requete = new AbortController()
  const delai = setTimeout(async () => {
    message.value = 'Recherche en cours…'
    try {
      const points = await chercherEquipements(nom, requete.signal)
      if (requete.signal.aborted) return
      resultats.value = points
      message.value = points.length ? 'Choisissez un équipement.' : 'Aucun équipement trouvé.'
    } catch {
      if (!requete.signal.aborted) message.value = 'Recherche indisponible. Modifiez la saisie pour réessayer.'
    }
  }, 250)
  nettoyer(() => {
    clearTimeout(delai)
    requete.abort()
  })
})

function choisir(point) {
  saisie.value = ''
  emit('selection', point)
}
</script>

<template>
  <section class="recherche" role="search" aria-label="Recherche d’équipements">
    <label for="nom-equipement">Rechercher un équipement par nom</label>
    <input id="nom-equipement" v-model="saisie" type="search" maxlength="255"
      autocomplete="off" placeholder="Nom de l’équipement (3 caractères minimum)">
    <p role="status">{{ message }}</p>
    <ul v-if="resultats.length" aria-label="Équipements trouvés">
      <li v-for="point in resultats" :key="point.id">
        <button type="button" @click="choisir(point)">
          <strong>{{ point.nom }}</strong>
          <span><template v-if="point.adresse">{{ point.adresse }} · </template>{{ point.codepostal }} {{ point.ville }}</span>
        </button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.recherche { margin-bottom: .65rem; padding: .8rem 1rem; border: 1px solid #ccd4c9; border-radius: .65rem; background: #fdfdf8; }
label { display: block; margin-bottom: .4rem; font-weight: 650; }
input { width: 100%; font: inherit; border: 1px solid #9caea3; border-radius: .3rem; padding: .45rem .6rem; }
p { margin: .5rem 0 0; }
p:empty { margin: 0; }
ul { list-style: none; padding: 0; margin: .35rem 0 0; max-height: 16rem; overflow-y: auto; }
button { display: grid; gap: .15rem; width: 100%; padding: .5rem; font: inherit; text-align: left; color: #175749; background: transparent; border: 0; cursor: pointer; }
button:hover, button:focus-visible { background: #e4efe7; }
span { color: #50635c; font-size: .9rem; }
</style>
