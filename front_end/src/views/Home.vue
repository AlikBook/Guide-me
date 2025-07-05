<template>
  <div class="app-container">
    <header class="app-header glass-header">
      <div class="header-content">
        <img src="/Logo.png" alt="Logo" class="logo" />
        <h1 class="app-title">Guide <span class="highlight">Me</span></h1>
      </div>
    </header>

    <main class="main-content">
      <div class="layout-container">
        <!-- Colonne de gauche pour les résultats -->
        <div class="results-column">
          <!-- Barre de recherche -->
          <div class="search-section">
            <div class="search-card">
              <div class="search-row-with-swap">
                <div class="search-input-container">
                  <div class="search-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path
                        fill="currentColor"
                        d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
                      />
                    </svg>
                  </div>
                  <input
                    type="text"
                    v-model="station1Input"
                    @input="filterStations(1)"
                    @focus="showSuggestions1 = true"
                    @blur="hideSuggestions(1)"
                    placeholder="Départ : Nom ou ID de station"
                    class="search-input"
                  />
                  <ul
                    v-if="showSuggestions1 && filteredStations1.length"
                    class="suggestions-dropdown"
                  >
                    <li
                      v-for="station in filteredStations1"
                      :key="'departure-' + station.id"
                      @mousedown="selectStation(station, 1)"
                      class="suggestion-item"
                    >
                      <div class="station-info">
                        <span class="station-name">{{ station.station }}</span>
                        <span class="station-meta"
                          >ID: {{ station.id }} • Ligne {{ station.line }}</span
                        >
                      </div>
                    </li>
                  </ul>
                </div>

                <button
                  class="swap-button"
                  @click="swapStations"
                  title="Inverser"
                >
                  <svg viewBox="0 0 24 24" width="20" height="20">
                    <path
                      fill="currentColor"
                      d="M4,9V5h14.17l-3.59-3.59L16,0l6,6l-6,6l-1.41-1.41L18.17,9H4zm16,6v4H5.83l3.58,3.59L8,24l-6-6l6-6l1.41,1.41L5.83,15H20z"
                    />
                  </svg>
                </button>

                <div class="search-input-container">
                  <div class="search-icon-arrivée">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path
                        fill="currentColor"
                        d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"
                      />
                    </svg>
                  </div>
                  <input
                    type="text"
                    v-model="station2Input"
                    @input="filterStations(2)"
                    @focus="showSuggestions2 = true"
                    @blur="hideSuggestions(2)"
                    placeholder="Arrivée : Nom ou ID de station"
                    class="search-input"
                  />
                  <ul
                    v-if="showSuggestions2 && filteredStations2.length"
                    class="suggestions-dropdown"
                  >
                    <li
                      v-for="station in filteredStations2"
                      :key="'arrival-' + station.id"
                      @mousedown="selectStation(station, 2)"
                      class="suggestion-item"
                    >
                      <div class="station-info">
                        <span class="station-name">{{ station.station }}</span>
                        <span class="station-meta"
                          >ID: {{ station.id }} • Ligne {{ station.line }}</span
                        >
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <button
                @click="call_trip(station1, station2)"
                class="primary-button"
                :disabled="!station1 || !station2"
              >
                <span>Calculer l'itinéraire</span>
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path
                    fill="currentColor"
                    d="M5 13h11.17l-4.88 4.88c-.39.39-.39 1.03 0 1.42.39.39 1.02.39 1.41 0l6.59-6.59c.39-.39.39-1.02 0-1.41l-6.58-6.6c-.39-.39-1.02-.39-1.41 0-.39.39-.39 1.02 0 1.41L16.17 11H5c-.55 0-1 .45-1 1s.45 1 1 1z"
                  />
                </svg>
              </button>
              <NetworkAnalysis />
              <CarbonImpact :trip="trip" :selectedTripIndex="selectedTripIndex" />
            </div>
          </div>

          <!-- Résultats du trajet -->
          <div v-if="trip && ((trip.trips && trip.trips.length > 0) || trip.total_time)" class="trip-results">
            <!-- Trip Options Selector (only show if we have multiple trips) -->
            <div v-if="trip.trips && trip.trips.length > 1" class="trip-options">
              <h3 class="options-title">{{ trip.trips.length }} itinéraires trouvés</h3>
              <div class="trip-selector">
                <button
                  v-for="(tripOption, index) in trip.trips"
                  :key="index"
                  @click="selectTrip(index)"
                  class="trip-option-button"
                  :class="{ active: selectedTripIndex === index }"
                >
                  <div class="trip-option-info">
                    <span class="trip-duration">{{ tripOption.total_time }}</span>
                    <span class="trip-changes">
                      {{ tripOption.stations.length - 1 }} changement{{ tripOption.stations.length - 1 > 1 ? 's' : '' }}
                    </span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Current Trip Display -->
            <div v-if="currentTrip || trip.total_time" class="current-trip">
              <div class="time-badge">
                <svg viewBox="0 0 24 24" width="18" height="18">
                  <path
                    fill="currentColor"
                    d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"
                  />
                  <path
                    fill="currentColor"
                    d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"
                  />
                </svg>
                <span>{{ currentTrip ? currentTrip.total_time : trip.total_time }}</span>
              </div>
              <div class="trip-stats">
                <span>{{ journeyStats.totalStations }} stations</span> •
                <span
                  >{{ journeyStats.changes }} changement{{
                    journeyStats.changes > 1 ? "s" : ""
                  }}</span
                >
              </div>

              <!-- Bloc compact des lignes -->
              <div class="compact-lines-container" @click="toggleTripDetails">
                <div class="compact-lines">
                  <div
                    v-for="(lineObj, index) in cleanedTrip"
                    :key="index"
                    class="line-badge"
                    :style="{
                      backgroundColor: getColorCode(Object.keys(lineObj)[0]),
                    }"
                  >
                    {{ Object.keys(lineObj)[0] }}
                  </div>
                </div>
                <div class="toggle-icon">
                  {{ showTripDetails ? "▼" : "▲" }}
                </div>
              </div>

              <!-- Détails dépliés -->
              <div v-if="showTripDetails" class="trip-details">
                <div
                  v-for="(lineObj, lineIndex) in cleanedTrip"
                  :key="lineIndex"
                  class="line-section"
                >
                  <div class="line-header">
                    <div
                      class="line-badge"
                      :style="{
                        backgroundColor: getColorCode(Object.keys(lineObj)[0]),
                      }"
                    >
                      {{ Object.keys(lineObj)[0] }}
                    </div>
                    <div class="line-direction">
                      Descendre à : {{ getLastStation(lineObj).station }}
                    </div>
                  </div>

                  <div class="stations-list">
                    <div
                      v-for="(station, stationIndex) in Object.values(lineObj)[0]"
                      :key="stationIndex"
                      class="station-item"
                      :class="{
                        'first-station': stationIndex === 0,
                        'last-station':
                          stationIndex === Object.values(lineObj)[0].length - 1,
                      }"
                    >
                      <div class="station-marker-container">
                        <div
                          class="station-marker"
                          :style="{
                            backgroundColor: getColorCode(
                              Object.keys(lineObj)[0]
                            ),
                          }"
                        ></div>
                        <div
                          class="station-line"
                          v-if="
                            stationIndex < Object.values(lineObj)[0].length - 1
                          "
                          :style="{
                            backgroundColor: getColorCode(
                              Object.keys(lineObj)[0]
                            ),
                          }"
                        ></div>
                      </div>
                      <div class="station-info">
                        <div class="station-name-with-accessibility">
                          <span class="station-name">{{ station.station }}</span>
                          <span
                            v-if="isWheelchairAccessible(station)"
                            class="wheelchair-icon accessible"
                            title="Accessible aux personnes à mobilité réduite"
                          >
                            ♿
                          </span>
                          <span
                            v-else
                            class="wheelchair-icon not-accessible"
                            title="Non accessible aux personnes à mobilité réduite"
                          >
                            🚫
                          </span>
                        </div>
                        <div class="station-time" v-if="stationIndex > 0">
                          {{ station.time || "" }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Correspondance -->
                  <div
                    v-if="lineIndex < cleanedTrip.length - 1"
                    class="connection"
                  >
                    <div class="connection-marker"></div>
                    <div class="connection-info">
                      <span>Correspondance</span>
                      <span class="connection-time"></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Colonne de droite pour la carte -->
        <div class="map-column">
          <div class="map-card">
            <img
              class="metro-map"
              src="/metrof_r.png"
              alt="Plan du métro parisien"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import NetworkAnalysis from '../components/Network-analysis.vue'
import CarbonImpact from '../components/CarbonImpact.vue'
import { ref, onMounted, computed } from "vue";

const data = ref(null);
const station1 = ref(0);
const station2 = ref(0);
const station1Input = ref("");
const station2Input = ref("");
const trip = ref(null);
const showSuggestions1 = ref(false);
const showSuggestions2 = ref(false);
const allStations = ref([]);
const expandedLines = ref([]);
const selectedDeparture = ref(null);
const selectedArrival = ref(null);
const showTripDetails = ref(false);
const selectedTripIndex = ref(0); // Track which trip is currently selected

onMounted(async () => {
  const response = await fetch("http://127.0.0.1:8000/station_ids");
  const result = await response.json();
  data.value = result;
  allStations.value = result.stations;
});

const filteredStations1 = computed(() => {
  if (!station1Input.value) return [];
  const query = station1Input.value.toLowerCase();
  return allStations.value
    .filter(
      (station) =>
        station.station.toLowerCase().includes(query) ||
        station.id.toString().includes(query)
    )
    .slice(0, 5);
});

const filteredStations2 = computed(() => {
  if (!station2Input.value) return [];
  const query = station2Input.value.toLowerCase();
  return allStations.value
    .filter(
      (station) =>
        station.station.toLowerCase().includes(query) ||
        station.id.toString().includes(query)
    )
    .slice(0, 5);
});

const journeyStats = computed(() => {
  // Handle new format (multiple trips)
  if (trip.value && trip.value.trips && trip.value.trips.length > 0) {
    const currentTripData = trip.value.trips[selectedTripIndex.value];
    if (!currentTripData || !currentTripData.stations) return { totalStations: 0, changes: 0 };

    const stationSet = new Set();
    currentTripData.stations.forEach((lineObj) => {
      const stations = Object.values(lineObj)[0];
      stations.forEach((station) => {
        stationSet.add(station.id);
      });
    });

    const totalStations = stationSet.size;
    const changes = currentTripData.stations.length - 1;
    return { totalStations, changes };
  }
  
  // Handle old format (single trip)
  if (trip.value && trip.value.stations) {
    const stationSet = new Set();
    trip.value.stations.forEach((lineObj) => {
      const stations = Object.values(lineObj)[0];
      stations.forEach((station) => {
        stationSet.add(station.id);
      });
    });

    const totalStations = stationSet.size;
    const changes = trip.value.stations.length - 1;
    return { totalStations, changes };
  }

  return { totalStations: 0, changes: 0 };
});

// Add computed property for current trip
const currentTrip = computed(() => {
  // Handle new format (multiple trips)
  if (trip.value && trip.value.trips && trip.value.trips.length > 0) {
    return trip.value.trips[selectedTripIndex.value];
  }
  
  // Handle old format (single trip) - return the trip itself
  if (trip.value && trip.value.stations) {
    return trip.value;
  }
  
  return null;
});

// Add function to check wheelchair accessibility
const isWheelchairAccessible = (station) => {
  return station.wheelchair_accessible === 1;
};

function filterStations(field) {
  if (field === 1) {
    showSuggestions1.value = !!station1Input.value;
  } else {
    showSuggestions2.value = !!station2Input.value;
  }
}

function hideSuggestions(field) {
  setTimeout(() => {
    if (field === 1) {
      showSuggestions1.value = false;
    } else {
      showSuggestions2.value = false;
    }
  }, 200);
}

function selectStation(station, field) {
  if (field === 1) {
    station1.value = station.id;
    station1Input.value = station.station;
    selectedDeparture.value = station;
    showSuggestions1.value = false;
  } else {
    station2.value = station.id;
    station2Input.value = station.station;
    selectedArrival.value = station;
    showSuggestions2.value = false;
  }
}

function getLastStation(lineObj) {
  const stations = Object.values(lineObj)[0];
  return stations[stations.length - 1];
}

async function call_trip(value1, value2) {
  const res = await fetch("http://127.0.0.1:8000/calculate_trip", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ start: value1, end: value2 }),
  });
  trip.value = await res.json();
  
  // Handle new format (multiple trips)
  if (trip.value.trips && trip.value.trips.length > 0) {
    expandedLines.value = new Array(trip.value.trips[0].stations.length).fill(false);
    selectedTripIndex.value = 0; // Reset to first trip
  }
  // Handle old format (single trip)
  else if (trip.value.stations) {
    expandedLines.value = new Array(trip.value.stations.length).fill(false);
    selectedTripIndex.value = 0;
  }
  
  showTripDetails.value = false;
}

function getColorCode(lineName) {
  const normalized = lineName.trim().toLowerCase().replace(/\s+/g, "-");
  const colors = {
    // Metro lines
    "metro-1": "#FFCD00",
    "metro-2": "#003CA6",
    "metro-3": "#837902",
    "metro-3bis": "#6EC4E8",
    "metro-4": "#CF009E",
    "metro-5": "#FF7E2E",
    "metro-6": "#6ECA97",
    "metro-7": "#FA9ABA",
    "metro-7bis": "#6ECA97",
    "metro-8": "#E19BDF",
    "metro-9": "#B6BD00",
    "metro-10": "#C9910D",
    "metro-11": "#704B1C",
    "metro-12": "#007852",
    "metro-13": "#6EC4E8",
    "metro-14": "#62259D",
    // RER lines
    "rer-a": "#E3051C",
    "rer-b": "#5291CE", 
    "rer-c": "#FFCE00",
    "rer-d": "#00814F",
    "rer-e": "#C04191"
  };
  return colors[normalized] || "#000";
}

function swapStations() {
  const tempId = station1.value;
  const tempInput = station1Input.value;
  const tempStation = selectedDeparture.value;

  station1.value = station2.value;
  station1Input.value = station2Input.value;
  selectedDeparture.value = selectedArrival.value;

  station2.value = tempId;
  station2Input.value = tempInput;
  selectedArrival.value = tempStation;
}

const cleanedTrip = computed(() => {
  let stations = null;
  
  // Handle new format (multiple trips)
  if (currentTrip.value && currentTrip.value.stations) {
    stations = currentTrip.value.stations;
  }
  // Handle old format (single trip)
  else if (trip.value && trip.value.stations) {
    stations = trip.value.stations;
  }
  
  if (!stations) return [];

  const cleaned = [];

  for (let i = 0; i < stations.length; i++) {
    const current = stations[i];
    const currentLine = Object.values(current)[0];

    const isSingleStation = currentLine.length === 1;
    const stationName = currentLine[0].station;

    const prev = stations[i - 1];
    const next = stations[i + 1];

    const prevStations = prev ? Object.values(prev)[0] : null;
    const nextStations = next ? Object.values(next)[0] : null;

    const prevEnd =
      prevStations && prevStations.length
        ? prevStations[prevStations.length - 1].station
        : null;

    const nextStart =
      nextStations && nextStations.length ? nextStations[0].station : null;

    if (
      isSingleStation &&
      (stationName === prevEnd || stationName === nextStart)
    ) {
      continue;
    }

    cleaned.push(current);
  }

  return cleaned;
});

function selectTrip(index) {
  selectedTripIndex.value = index;
  if (trip.value.trips && trip.value.trips[index] && trip.value.trips[index].stations) {
    expandedLines.value = new Array(trip.value.trips[index].stations.length).fill(false);
  }
  showTripDetails.value = false;
}

function toggleTripDetails() {
  showTripDetails.value = !showTripDetails.value;
}
</script>

<style>
:root {
  --primary-color: #2f2f7e;
  --secondary-color: #ff5a5f;
  --text-color: #333;
  --light-text: #666;
  --border-color: #e0e0e0;
  --background-light: #f8f9fa;
  --card-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Roboto", Arial, sans-serif;
  color: var(--text-color);
  background-color: #fff;
  line-height: 1.5;
}

.app-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 20px;
}

.layout-container {
  display: flex;
  gap: 20px;
}

.results-column {
  flex: 0 0 55%;
  max-width: 55%;
}

.map-column {
  flex: 1;
  position: sticky;
  top: 20px;
  height: fit-content;
}

.map-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
  height: 100%;
}

.search-section {
  margin-bottom: 24px;
}

.search-input-container {
  position: relative;
  margin-bottom: 12px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--light-text);
}

.search-icon-arrivée {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: red;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 100;
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 300px;
  overflow-y: auto;
  margin-top: 2px;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--border-color);
}

.suggestion-item:hover {
  background-color: var(--background-light);
}

.station-info {
  display: flex;
  flex-direction: column;
}

.station-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.station-meta {
  font-size: 12px;
  color: var(--light-text);
}

.primary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.primary-button:hover {
  background-color: #1a1a5a;
}

.primary-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.primary-button svg {
  fill: white;
}

.trip-results {
  margin-bottom: 20px;
}

.time-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: var(--background-light);
  border-radius: 20px;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 12px;
}

.time-badge svg {
  fill: var(--primary-color);
}

.trip-stats {
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--light-text);
}

/* Styles pour l'affichage compact */
.compact-lines-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  cursor: pointer;
  box-shadow: var(--card-shadow);
  transition: all 0.2s;
}

.compact-lines-container:hover {
  background-color: #f5f5f5;
}

.compact-lines {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.line-badge {
  padding: 6px 12px;
  border-radius: 16px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
}

.toggle-icon {
  font-size: 14px;
  color: var(--light-text);
  margin-left: 8px;
}

/* Styles pour les détails dépliés */
.trip-details {
  margin-top: 16px;
  animation: fadeIn 0.3s ease-out;
}

.line-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: var(--card-shadow);
}

.line-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.line-direction {
  font-size: 14px;
  color: var(--light-text);
}

.stations-list {
  margin-left: 8px;
  padding-left: 14px;
  border-left: 2px solid var(--border-color);
}

.station-item {
  display: flex;
  margin-bottom: 16px;
  position: relative;
}

.station-marker-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 12px;
  position: relative;
}

.station-marker {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 2px currentColor;
  z-index: 2;
}

.station-line {
  width: 2px;
  height: calc(100% - 16px);
  position: absolute;
  top: 16px;
  left: 7px;
}

.station-info {
  flex: 1;
}

.station-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.station-time {
  font-size: 13px;
  color: var(--light-text);
}

.first-station .station-marker {
  border-color: #4caf50;
}

.last-station .station-marker {
  border-color: #f44336;
}

.connection {
  display: flex;
  align-items: center;
  margin: 12px 0 0 8px;
}

.connection-marker {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: white;
  border: 2px solid var(--border-color);
  margin-right: 12px;
  position: relative;
}

.connection-info {
  flex: 1;
  font-size: 13px;
  color: var(--light-text);
}

.connection-time {
  margin-left: 8px;
  font-weight: 500;
}

.swap-button {
  position: absolute;
  left: 90%;
  top: 50%;
  transform: translate(-10%, -70%);
  background-color: white;
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  box-shadow: var(--card-shadow);
  transition: background-color 0.2s, color 0.2s;
}

.swap-button:hover {
  background-color: var(--primary-color);
  color: white;
}

.search-row-with-swap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 999;
  padding: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-header {
  background: #2f2f7e;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  margin-bottom: 5%;
  margin-top: 3%;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background-color: #2f2f7e;
  border-radius: 20px;
}

.logo {
  height: 100px;
  width: 100px;
  object-fit: contain;
}

.app-title {
  font-size: 40px;
  font-weight: 700;
  color: white;
  letter-spacing: 1px;
}

.highlight {
  color: #ffd700;
}

.metro-map {
  width: 100%;
  border-radius: 8px;
  height: auto;
  max-height: 600px;
  object-fit: contain;
}

/* Trip options selector styles */
.trip-options {
  margin-bottom: 24px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--card-shadow);
}

.options-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 16px;
  text-align: center;
}

.trip-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trip-option-button {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--background-light);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-family: inherit;
}

.trip-option-button:hover {
  background: #e8f0fe;
  border-color: var(--primary-color);
}

.trip-option-button.active {
  background: #e8f0fe;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.trip-option-info {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.trip-duration {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 16px;
}

.trip-changes {
  font-size: 14px;
  color: var(--light-text);
}

/* Wheelchair accessibility styles */
.station-name-with-accessibility {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wheelchair-icon {
  font-size: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.wheelchair-icon.accessible {
  color: #4caf50;
}

.wheelchair-icon.not-accessible {
  color: #f44336;
  filter: grayscale(100%);
}

/* Current trip section */
.current-trip {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--card-shadow);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  .results-column,
  .map-column {
    flex: 1 1 100%;
    max-width: 100%;
  }

  .map-column {
    order: -1;
    margin-bottom: 20px;
    position: static;
  }

  .metro-map {
    max-height: 400px;
  }
}
</style>
