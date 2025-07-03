<template>
    <div>
      <button
        @click="showPopup = true"
        class="carbon-button"
        :disabled="!totalStations"
      >
        Voir l’empreinte carbone
      </button>
  
      <div v-if="showPopup" class="popup-overlay">
        <div class="popup-container">
          <h2 class="popup-title">Empreinte carbone du trajet</h2>
  
          <p class="popup-line">
            🧭 Distance estimée : {{ totalStations }} stations
          </p>
          <p class="popup-line">
            🌱 Émissions estimées : <strong>{{ emission }} g CO₂</strong>
          </p>
          <p class="popup-line text-green">
            Ce trajet est très peu polluant 💚
          </p>
  
          <button @click="showPopup = false" class="close-button">Fermer</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  
  const props = defineProps({
    totalStations: Number
  })
  
  const showPopup = ref(false)
  
  const emission = computed(() =>
    props.totalStations ? (props.totalStations * 0.15).toFixed(2) : 0
  )
  </script>
  
  <style scoped>
  .carbon-button {
    padding: 10px 20px;
    font-size: 16px;
    background-color: #2ecc71;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 10px;
  }
  .carbon-button:hover {
    background-color: #27ae60;
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
    background: white;
    padding: 24px;
    border-radius: 10px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
  }
  .popup-title {
    font-size: 20px;
    margin-bottom: 16px;
  }
  .popup-line {
    margin-bottom: 10px;
    font-size: 16px;
  }
  .text-green {
    color: #2ecc71;
  }
  .close-button {
    margin-top: 15px;
    background: #7f8c8d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
  }
  .close-button:hover {
    background: #616a6b;
  }
  </style>
  