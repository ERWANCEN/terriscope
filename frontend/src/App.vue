<script setup>
import { ref } from 'vue'
import FicheEquipement from './components/FicheEquipement.vue'
import FiltresPanel from './components/FiltresPanel.vue'
import MapView from './components/MapView.vue'

const equipementSelectionne = ref(null)
const filtres = ref({ domaines: {}, villes: [] })

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
      <FiltresPanel @filtrer="filtrer" />
      <div class="exploration">
        <MapView :filtres="filtres" @selection="equipementSelectionne = $event" />
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
</style>
