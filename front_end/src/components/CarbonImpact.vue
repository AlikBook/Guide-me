<template>
    <div>
      <button @click="openPopup" class="carbon-button">Voir l’empreinte carbone</button>
  
      <div v-if="showPopup" class="popup-overlay">
        <div class="popup-content">
          <h2>Impact carbone estimé</h2>
  
          <div v-if="trip && trip.stations">
            <p><strong>Nombre de stations :</strong> {{ trip.stations.length }}</p>
            <p><strong>Émission estimée :</strong> {{ estimatedCO2 }} g de CO₂</p>
          </div>
          <div v-else>
            <p>Veuillez d'abord calculer un itinéraire.</p>
          </div>
  
          <button @click="closePopup" class="close-button">Fermer</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, defineProps } from 'vue';
  
  const props = defineProps({
    trip: Object,
  });
  
  const showPopup = ref(false);
  const openPopup = () => (showPopup.value = true);
  const closePopup = () => (showPopup.value = false);
  
  const estimatedCO2 = computed(() => {
    if (!props.trip || !props.trip.stations) return 0;
    const stations = props.trip.stations.length;
    return stations * 4; // 4g de CO₂/station
  });
  </script>
  
  <style scoped>
 .carbon-button {
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
  margin-top: 0; /* très important pour aligner sur la même ligne */
}

.carbon-button:hover {
  background-color: #059669;
}
  
  .popup-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
  }
  
  .popup-content {
    background: white;
    padding: 10px 20px;
    border-radius: 8px;
    max-width: 400px;
    width: 100%;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    text-align: center;
  }
  
  .close-button {
    margin-top: 16px;
    background-color: #6b7280;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  </style>
  
  