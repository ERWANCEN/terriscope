<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { chargerFicheEquipement } from '../api.js'

const props = defineProps({ id: { type: String, required: true } })
const emit = defineEmits(['fermer'])
const fiche = ref(null)
const erreur = ref(false)
const controleur = new AbortController()

async function charger() {
  erreur.value = false
  try {
    fiche.value = await chargerFicheEquipement(props.id, controleur.signal)
  } catch {
    if (!controleur.signal.aborted) erreur.value = true
  }
}

onMounted(charger)
onUnmounted(() => controleur.abort())
</script>

<template>
  <aside class="fiche" aria-label="Fiche équipement">
    <header>
      <span>Fiche équipement</span>
      <button type="button" aria-label="Fermer la fiche" @click="emit('fermer')">×</button>
    </header>
    <div v-if="erreur">
      <p role="alert">Impossible de charger la fiche.</p>
      <button type="button" @click="charger">Réessayer</button>
    </div>
    <p v-else-if="!fiche" role="status">Chargement de la fiche…</p>
    <template v-else>
      <h2>{{ fiche.nom || 'Équipement sans nom' }}</h2>
      <dl>
        <dt>Adresse</dt>
        <dd>{{ fiche.adresse || 'Adresse non renseignée' }}<br>{{ fiche.codepostal }} {{ fiche.ville }}</dd>
        <dt>SIRET</dt>
        <dd>{{ fiche.siret || 'Non renseigné' }}</dd>
        <dt>Domaine</dt>
        <dd>{{ fiche.domaine1 || 'Non renseigné' }}</dd>
        <dt>Sous-domaine</dt>
        <dd>{{ fiche.domaine2 || 'Non renseigné' }}</dd>
        <dt>Type d’équipement</dt>
        <dd>{{ fiche.domaine3 || 'Non renseigné' }}</dd>
      </dl>
    </template>
  </aside>
</template>

<style scoped>
.fiche {
  position: absolute;
  z-index: 1;
  inset: .75rem .75rem auto auto;
  width: min(20rem, calc(100% - 1.5rem));
  max-height: calc(100% - 1.5rem);
  overflow: auto;
  overflow-wrap: anywhere;
  padding: 1rem 1.25rem;
  background: #fdfdf8;
  border: 1px solid #c7d1c7;
  border-radius: .55rem;
  box-shadow: 0 .2rem 1rem #183c3526;
}
header { display: flex; align-items: center; justify-content: space-between; color: #50635c; }
button { font: inherit; color: inherit; cursor: pointer; }
header button { border: 0; background: transparent; font-size: 1.5rem; padding: 0 .4rem; }
h2 { margin: .6rem 0 1rem; font: 500 1.65rem/1.15 'Spectral', Georgia, serif; }
dl { margin: 0; }
dt { margin-top: .75rem; color: #50635c; font-size: .85rem; }
dd { margin: .15rem 0 0; }
@media (max-width: 650px) {
  .fiche { inset: auto .5rem 1.6rem; width: auto; max-height: 45%; }
}
</style>
