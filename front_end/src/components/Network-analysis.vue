<template>
    <div>
      <!-- BOUTON -->
      <button @click="openPopup" class="network-button">
        Analyser le réseau
      </button>
  
      <!-- POPUP -->
      <div v-if="showPopup" class="popup-overlay">
        <div class="popup-container">
          <h2 class="popup-title">Résultat de l’analyse</h2>
  
          <div v-if="loading" class="popup-loading">Chargement...</div>
          <div v-else-if="error" class="popup-error">{{ error }}</div>
          <div v-else>
            <p class="popup-line">{{ analysis.message }}</p>
            <p class="popup-line">
              <strong>Temps total MST :</strong> {{ analysis.mst_total_time }}
            </p>
            <p class="popup-line">
              <strong>Temps total en seconde :</strong> {{ analysis.mst_cost_seconds }}
            </p>
          </div>
  
          <button @click="closePopup" class="close-button">Fermer</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const showPopup = ref(false)
  const analysis = ref({})
  const loading = ref(false)
  const error = ref(null)
  
  const openPopup = async () => {
    showPopup.value = true
    loading.value = true
    error.value = null
  
    try {
      const response = await axios.get('http://localhost:8000/analyze_network') // à adapter si besoin
      analysis.value = response.data
    } catch (err) {
      error.value = "Impossible de charger les données du graphe"
    } finally {
      loading.value = false
    }
  }
  
  const closePopup = () => {
    showPopup.value = false
  }
  </script>
  
  <style scoped>
  .network-button {
    padding: 10px 20px;
    font-size: 16px;
    font-weight: 500;
    background-color: #439df8;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s ease;
  }
  .network-button:hover {
    background-color: #34495e;
  }
  
  .popup-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
  }
  
  .popup-container {
    background-color: white;
    padding: 24px;
    border-radius: 12px;
    max-width: 450px;
    width: 80%;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
  }
  
  .popup-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 16px;
  }
  
  .popup-line {
    margin-bottom: 10px;
    font-size: 16px;
  }
  
  .popup-loading {
    font-style: italic;
  }
  
  .popup-error {
    color: red;
    font-weight: 600;
  }
  
  .close-button {
    margin-top: 16px;
    padding: 10px 20px;
    background-color: #777;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  .close-button:hover {
    background-color: #555;
  }
  </style>
  