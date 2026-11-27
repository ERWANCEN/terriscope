<script setup>
import { computed, ref, watch } from 'vue'
import {
  creerImplantation,
  modifierImplantation,
  supprimerImplantation,
} from '../api.js'

const props = defineProps({
  // Feature GeoJSON existante en mode édition, ou null en mode création
  implantation: {
    type: Object,
    default: null,
  },
  // Coordonnées { lon, lat } issues d'un clic sur la carte en mode création
  position: {
    type: Object,
    default: null,
  },
  // Liste optionnelle des domaines (à plat ou hiérarchie renvoyée par /api/domaines/)
  domaines: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['enregistre', 'supprime', 'fermer'])

const titre = ref('')
const domaine3 = ref('')
const commentaire = ref('')
const lon = ref(null)
const lat = ref(null)
const erreur = ref('')
const chargement = ref(false)

const estEdition = computed(() => Boolean(props.implantation?.id))

// Extrait les domaines de niveau 3 quel que soit le format envoyé par le parent
const optionsDomaine3 = computed(() => {
  const resultat = []
  function parcourir(liste) {
    if (!Array.isArray(liste)) return
    for (const item of liste) {
      // L'API /api/domaines/ place les sous-niveaux sous la clé "enfants"
      const enfants = item.enfants || item.domaines2 || item.domaines3 || item.children || item.sous_domaines
      if (Array.isArray(enfants) && enfants.length) {
        parcourir(enfants)
      } else if (item.code && (item.libelle || item.nom)) {
        resultat.push({ code: item.code, libelle: item.libelle || item.nom })
      }
    }
  }
  parcourir(props.domaines)
  return resultat.sort((a, b) => a.libelle.localeCompare(b.libelle, 'fr'))
})

watch(
  () => [props.implantation, props.position],
  ([imp, pos]) => {
    erreur.value = ''
    if (imp) {
      titre.value = imp.properties?.titre || ''
      domaine3.value = imp.properties?.domaine3 || ''
      commentaire.value = imp.properties?.commentaire || ''
      const coords = imp.geometry?.coordinates || []
      lon.value = coords[0] ?? null
      lat.value = coords[1] ?? null
    } else {
      titre.value = ''
      domaine3.value = ''
      commentaire.value = ''
      lon.value = pos?.lon ?? null
      lat.value = pos?.lat ?? null
    }
  },
  { immediate: true }
)

async function soumettre() {
  erreur.value = ''
  if (!titre.value.trim()) {
    erreur.value = 'Le titre est obligatoire.'
    return
  }
  if (lon.value == null || lat.value == null) {
    erreur.value = 'Clique sur la carte pour choisir un emplacement.'
    return
  }

  chargement.value = true
  try {
    const payload = {
      titre: titre.value.trim(),
      domaine3: domaine3.value || null,
      commentaire: commentaire.value.trim(),
      lon: Number(lon.value),
      lat: Number(lat.value),
    }

    const resultat = estEdition.value
      ? await modifierImplantation(props.implantation.id, payload)
      : await creerImplantation(payload)

    emit('enregistre', resultat)
  } catch (e) {
    erreur.value = e.message || "Erreur lors de l'enregistrement."
  } finally {
    chargement.value = false
  }
}

async function supprimer() {
  if (!estEdition.value) return
  if (!window.confirm('Supprimer définitivement cette implantation ?')) return

  chargement.value = true
  erreur.value = ''
  try {
    await supprimerImplantation(props.implantation.id)
    emit('supprime', props.implantation.id)
  } catch (e) {
    erreur.value = e.message || 'Erreur lors de la suppression.'
  } finally {
    chargement.value = false
  }
}
</script>

<template>
  <form class="imp-form" @submit.prevent="soumettre">
    <div class="imp-header">
      <h3>{{ estEdition ? "Modifier l'implantation" : 'Nouvelle implantation' }}</h3>
      <button type="button" class="btn-fermer" aria-label="Fermer" @click="emit('fermer')">
        ×
      </button>
    </div>

    <p v-if="lat != null && lon != null" class="imp-coords">
      Position : {{ Number(lat).toFixed(5) }}, {{ Number(lon).toFixed(5) }}
    </p>

    <label>
      Titre *
      <input
        v-model="titre"
        type="text"
        placeholder="ex. Projet boulangerie centre-ville"
        required
      />
    </label>

    <label>
      Type de commerce (Domaine 3)
      <select v-if="optionsDomaine3.length" v-model="domaine3">
        <option value="">-- Aucun --</option>
        <option v-for="d in optionsDomaine3" :key="d.code" :value="d.code">
          {{ d.libelle }} ({{ d.code }})
        </option>
      </select>
      <input
        v-else
        v-model="domaine3"
        type="text"
        placeholder="Code optionnel, ex. A501"
      />
    </label>

    <label>
      Commentaire
      <textarea
        v-model="commentaire"
        rows="3"
        placeholder="Notes de prospection, loyer, concurrence..."
      />
    </label>

    <p v-if="erreur" class="imp-erreur">{{ erreur }}</p>

    <div class="imp-actions">
      <button type="submit" class="btn-primaire" :disabled="chargement">
        {{ chargement ? 'Enregistrement...' : (estEdition ? 'Enregistrer' : 'Ajouter') }}
      </button>

      <button
        v-if="estEdition"
        type="button"
        class="btn-danger"
        :disabled="chargement"
        @click="supprimer"
      >
        Supprimer
      </button>
    </div>
  </form>
</template>

<style scoped>
.imp-form {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
}

.imp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.imp-header h3 {
  margin: 0;
  font-size: 15px;
}

.btn-fermer {
  background: none;
  border: none;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  color: #64748b;
}

.imp-coords {
  margin: 0;
  font-size: 12px;
  color: #475569;
  background: #f8fafc;
  padding: 4px 8px;
  border-radius: 4px;
}

.imp-form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-weight: 500;
}

.imp-form input,
.imp-form select,
.imp-form textarea {
  padding: 6px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
}

.imp-erreur {
  margin: 0;
  color: #b91c1c;
  font-size: 13px;
}

.imp-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.btn-primaire {
  flex: 1;
  background: #7c3aed;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}

.btn-danger {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primaire:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>