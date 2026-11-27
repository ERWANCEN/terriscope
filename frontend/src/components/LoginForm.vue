<script setup>
import { ref } from 'vue'
import { connecter, deconnecter, inscrire } from '../api.js'

const props = defineProps({
  utilisateur: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['connecte', 'deconnecte'])

const mode = ref('connexion') // 'connexion' ou 'inscription'
const username = ref('')
const password = ref('')
const erreur = ref('')
const chargement = ref(false)

async function soumettre() {
  erreur.value = ''
  if (!username.value.trim() || !password.value) {
    erreur.value = 'Renseigne un identifiant et un mot de passe.'
    return
  }

  chargement.value = true
  try {
    if (mode.value === 'connexion') {
      await connecter(username.value.trim(), password.value)
    } else {
      await inscrire(username.value.trim(), password.value)
    }
    password.value = ''
    emit('connecte')
  } catch (e) {
    erreur.value = e.message || 'Impossible de se connecter.'
  } finally {
    chargement.value = false
  }
}

function seDeconnecter() {
  deconnecter()
  username.value = ''
  password.value = ''
  erreur.value = ''
  emit('deconnecte')
}

function basculerMode() {
  mode.value = mode.value === 'connexion' ? 'inscription' : 'connexion'
  erreur.value = ''
}
</script>

<template>
  <div class="auth-box">
    <div v-if="props.utilisateur" class="auth-connecte">
      <span>Connecté : <strong>{{ props.utilisateur.username }}</strong></span>
      <button type="button" class="btn-secondaire" @click="seDeconnecter">
        Déconnexion
      </button>
    </div>

    <form v-else class="auth-form" @submit.prevent="soumettre">
      <h3>{{ mode === 'connexion' ? 'Connexion' : 'Créer un compte' }}</h3>

      <label>
        Identifiant
        <input
          v-model="username"
          type="text"
          autocomplete="username"
          placeholder="ex. alice"
          required
        />
      </label>

      <label>
        Mot de passe
        <input
          v-model="password"
          type="password"
          :autocomplete="mode === 'connexion' ? 'current-password' : 'new-password'"
          required
        />
      </label>

      <p v-if="erreur" class="auth-erreur">{{ erreur }}</p>

      <button type="submit" class="btn-primaire" :disabled="chargement">
        {{ chargement ? 'Chargement...' : (mode === 'connexion' ? 'Se connecter' : "S'inscrire") }}
      </button>

      <button type="button" class="btn-lien" @click="basculerMode">
        {{ mode === 'connexion' ? 'Pas encore de compte ? Créer un compte' : 'Déjà un compte ? Se connecter' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.auth-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
}

.auth-connecte {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-form h3 {
  margin: 0 0 4px;
  font-size: 15px;
}

.auth-form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-weight: 500;
}

.auth-form input {
  padding: 6px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}

.auth-erreur {
  margin: 0;
  color: #b91c1c;
  font-size: 13px;
}

.btn-primaire {
  background: #7c3aed;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primaire:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondaire {
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
}

.btn-lien {
  background: none;
  border: none;
  color: #7c3aed;
  padding: 4px 0 0;
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  text-decoration: underline;
}
</style>