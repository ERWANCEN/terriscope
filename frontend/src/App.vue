<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { chargerImplantations, chargerUtilisateur, deconnecter, lireToken } from './api.js'
import FicheEquipement from './components/FicheEquipement.vue'
import FiltresPanel from './components/FiltresPanel.vue'
import MapView from './components/MapView.vue'
import LoginForm from './components/LoginForm.vue'
import ImplantationForm from './components/ImplantationForm.vue'

const equipementSelectionne = ref(null)
const filtres = ref({ domaines: {}, villes: [] })
const utilisateur = ref(null)
const implantations = ref([])
const typesCommerce = ref([])
const modeAjout = ref(false)
const position = ref(null)
const implantation = ref(null)
const erreurSession = ref('')
const chargement = ref(false)
let versionSession = 0
let tokenSession = null

function fermerFormulaire() {
  modeAjout.value = false
  position.value = null
  implantation.value = null
}

async function actualiserSession() {
  const version = ++versionSession
  tokenSession = lireToken()
  utilisateur.value = null
  implantations.value = []
  erreurSession.value = ''
  fermerFormulaire()
  chargement.value = Boolean(tokenSession)
  if (!tokenSession) return

  // Un changement de compte rend caduques les réponses de la session précédente.
  const actuelle = () => version === versionSession && tokenSession === lireToken()
  try {
    const compte = await chargerUtilisateur()
    if (!actuelle()) return
    utilisateur.value = compte
    const points = await chargerImplantations()
    if (actuelle()) implantations.value = points
  } catch {
    if (!actuelle()) return
    if (utilisateur.value) {
      erreurSession.value = 'Impossible de charger vos implantations.'
    } else {
      deconnecter()
      tokenSession = null
      erreurSession.value = 'Session indisponible. Veuillez vous reconnecter.'
    }
  } finally {
    if (version === versionSession) chargement.value = false
  }
}

function suivreSession() {
  if (lireToken() !== tokenSession) actualiserSession()
}
onMounted(() => {
  actualiserSession()
  window.addEventListener('storage', suivreSession)
})
onUnmounted(() => {
  versionSession++
  window.removeEventListener('storage', suivreSession)
})

function commencerAjout() {
  fermerFormulaire()
  equipementSelectionne.value = null
  modeAjout.value = true
}

function placer(coordonnees) {
  if (!modeAjout.value || !utilisateur.value) return
  position.value = coordonnees
  modeAjout.value = false
}

function ouvrirImplantation(feature) {
  fermerFormulaire()
  equipementSelectionne.value = null
  implantation.value = feature
}

function ouvrirEquipement(id) {
  fermerFormulaire()
  equipementSelectionne.value = id
}

function enregistrer(feature) {
  implantations.value = [...implantations.value.filter(point => point.id !== feature.id), feature]
  fermerFormulaire()
}

function supprimer(id) {
  implantations.value = implantations.value.filter(point => point.id !== id)
  fermerFormulaire()
}

function filtrer(selection) {
  equipementSelectionne.value = null
  filtres.value = selection
}
</script>

<template>
  <header class="brand"><span aria-hidden="true" class="brand-mark"></span>TerriScope</header>
  <main>
    <h1>Les équipements de Tours</h1>
    <p class="description">Base permanente des équipements · Insee 2025</p>
    <div class="atlas">
      <div class="outils">
        <LoginForm :key="utilisateur?.id ?? 'anonyme'" :utilisateur="utilisateur"
          @connecte="actualiserSession" @deconnecte="actualiserSession" />
        <p v-if="erreurSession" role="alert">
          {{ erreurSession }}
          <button v-if="utilisateur" type="button" @click="actualiserSession">Réessayer</button>
        </p>
        <button v-if="utilisateur && !erreurSession" class="ajouter" type="button" :disabled="chargement"
          @click="modeAjout ? fermerFormulaire() : commencerAjout()">
          {{ modeAjout ? 'Annuler le placement' : 'Ajouter une implantation' }}
        </button>
        <FiltresPanel @filtrer="filtrer" @types-charges="typesCommerce = $event" />
      </div>
      <div class="exploration">
        <MapView :filtres="filtres" :implantations="implantations" :mode-ajout="modeAjout"
          @selection="ouvrirEquipement" @position="placer" @implantation="ouvrirImplantation" />
        <ImplantationForm
          v-if="utilisateur && (position || implantation)"
          :key="implantation?.id ?? 'nouvelle'"
          class="edition"
          :position="position" :implantation="implantation" :domaines="typesCommerce"
          @enregistre="enregistrer" @supprime="supprimer" @fermer="fermerFormulaire"
        />
        <FicheEquipement
          v-if="equipementSelectionne"
          :key="equipementSelectionne"
          :id="equipementSelectionne"
          @fermer="equipementSelectionne = null"
        />
      </div>
    </div>
  </main>
</template>

<style>
:root {
  font-family: 'Inter', system-ui, sans-serif;
  color: #183c35;
  background: #f8f8f2;
}
* { box-sizing: border-box; }
body { margin: 0; }
.brand {
  display: flex;
  align-items: center;
  gap: .7rem;
  padding: .95rem clamp(1rem, 4vw, 4rem);
  border-bottom: 1px solid #d2d9ce;
  font-size: 1.1rem;
  font-weight: 750;
}
.brand-mark {
  width: 1rem;
  height: 1rem;
  border: .32rem solid #267164;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
}
main { max-width: 112rem; margin: auto; padding: 1.5rem clamp(1rem, 4vw, 4rem); }
h1 { margin: 0; font: 500 clamp(1.9rem, 4vw, 3.2rem)/1.1 'Spectral', Georgia, serif; }
.description { margin: .5rem 0 1.1rem; color: #50635c; }
.atlas { display: grid; grid-template-columns: minmax(15rem, 19rem) minmax(0, 1fr); gap: 1rem; }
@media (max-width: 760px) { .atlas { grid-template-columns: minmax(0, 1fr); } }
.exploration { position: relative; isolation: isolate; }
.exploration > .cadre { z-index: 0; }
.outils { display: grid; align-content: start; gap: .65rem; }
.ajouter { border: 0; border-radius: .4rem; padding: .65rem; background: #6432bb; color: white; font: inherit; cursor: pointer; }
.edition { position: absolute; z-index: 1; inset: .75rem .75rem auto auto; width: min(20rem, 94%); max-height: calc(100% - 1.5rem); overflow: auto; }
.exploration { align-self: start; }
@media (max-width: 650px) { .edition { inset: auto .5rem 1.6rem; width: auto; max-height: 55%; } }
</style>
