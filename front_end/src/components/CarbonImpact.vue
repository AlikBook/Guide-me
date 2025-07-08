<template>
    <div>
      <button @click="openPopup" class="carbon-button">Voir l’empreinte carbone</button>
  
      <div v-if="showPopup" class="popup-overlay">
        <div class="popup-content">
          <h2>Impact carbone estimé</h2>
  
          <div v-if="hasValidTrip">
            <p><strong>Nombre de stations :</strong> {{ totalStations }}</p>
            <p><strong>Émission estimée :</strong> {{ estimatedCO2 }} g de CO₂</p>
            <p><small>Calculé sur la base de 4g de CO₂ par station</small></p>
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
    selectedTripIndex: {
      type: Number,
      default: 0
    }
  });
  
  const showPopup = ref(false);
  const openPopup = () => (showPopup.value = true);
  const closePopup = () => (showPopup.value = false);
  
  const estimatedCO2 = computed(() => {
    if (!hasValidTrip.value) return 0;
    return totalStations.value * 4; // 4g de CO₂/station
  });

  const hasValidTrip = computed(() => {
    // Check new format (multiple trips)
    if (props.trip && props.trip.trips && props.trip.trips.length > 0) {
      const selectedTrip = props.trip.trips[props.selectedTripIndex];
      return selectedTrip && selectedTrip.stations && selectedTrip.stations.length > 0;
    }
    // Check old format (single trip)
    return props.trip && props.trip.stations && props.trip.stations.length > 0;
  });

  const totalStations = computed(() => {
    if (!hasValidTrip.value) return 0;
    
    // Handle new format (multiple trips) - use selected trip for carbon calculation
    if (props.trip.trips && props.trip.trips.length > 0) {
      const selectedTrip = props.trip.trips[props.selectedTripIndex];
      if (selectedTrip && selectedTrip.stations) {
        const stationSet = new Set();
        selectedTrip.stations.forEach((lineObj) => {
          const stations = Object.values(lineObj)[0];
          stations.forEach((station) => {
            stationSet.add(station.id);
          });
        });
        return stationSet.size;
      }
    }
    
    // Handle old format (single trip)
    if (props.trip.stations) {
      const stationSet = new Set();
      props.trip.stations.forEach((lineObj) => {
        const stations = Object.values(lineObj)[0];
        stations.forEach((station) => {
          stationSet.add(station.id);
        });
      });
      return stationSet.size;
    }
    
    return 0;
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
  
  