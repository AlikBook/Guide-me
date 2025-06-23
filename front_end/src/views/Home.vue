<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="app-title">Metro Paris</h1>
    </header>

    <main class="main-content">
      <div class="layout-container">
        <!-- Colonne de gauche pour les résultats -->
        <div class="results-column">
          <div class="search-section">
            <div class="search-card">
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

              <div class="search-input-container">
                <div class="search-icon">
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
            </div>
          </div>

          <div v-if="trip && trip.total_time" class="trip-summary">
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
              <span>Temps estimé : {{ trip.total_time }} minutes</span>
            </div>
          </div>

          <div v-if="trip && trip.stations" class="journey-container">
            <div class="journey-card">
              <div
                v-for="lineObj in cleanedTrip"
                :key="Object.keys(lineObj)[0]"
                class="line-section"
                :style="{
                  borderLeftColor: getColorCode(Object.keys(lineObj)[0]),
                }"
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
                    Direction {{ getLastStation(lineObj).station }}
                  </div>
                </div>

                <div class="stations-list">
                  <div
                    v-for="(station, index) in Object.values(lineObj)[0]"
                    :key="station.id"
                    class="station-item"
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
                        :style="{
                          backgroundColor: getColorCode(
                            Object.keys(lineObj)[0]
                          ),
                        }"
                      ></div>
                    </div>
                    <div class="station-details">
                      <div class="station-name">{{ station.station }}</div>
                      <div v-if="index === 0" class="station-time">Départ</div>
                      <div
                        v-else-if="
                          index === Object.values(lineObj)[0].length - 1
                        "
                        class="station-time"
                      >
                        Arrivée
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="stations-list-container">
            <h2>Toutes les stations</h2>
            <ul v-if="data && data.stations" class="all-stations-list">
              <li
                v-for="item in data.stations"
                :key="item.id"
                class="station-list-item"
              >
                <span class="station-id">ID: {{ item.id }}</span>
                <span class="station-name">{{ item.station }}</span>
                <span class="station-line">Ligne: {{ item.line }}</span>
              </li>
            </ul>
            <div v-else class="loading-message">Chargement en cours...</div>
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

onMounted(async () => {
  const response = await fetch("http://127.0.0.1:8000/station_ids");
  const result = await response.json();
  data.value = result;
  allStations.value = result.stations;

});

function extractLineNumber(stationName) {
  const match = stationName.match(/;\d+/);
  return match ? match[0].replace(";", "") : "?";
}

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
    showSuggestions1.value = false;
  } else {
    station2.value = station.id;
    station2Input.value = station.station;
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
}

function getColorCode(lineName) {
  const normalized = lineName.trim().toLowerCase().replace(/\s+/g, "-");
  const colors = {
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
  };
  return colors[normalized] || "#000";
}

const cleanedTrip = computed(() => {
  if (!trip.value || !trip.value.stations) return [];

  const cleaned = [];
  const stations = trip.value.stations;

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
</script>

<style>
:root {
  --primary-color: #2f2f7e;
  --secondary-color: #ff5a5f;
  --text-color: #333;
  --light-text: #666;
  --border-color: #e0e0e0;
  --background-light: #f8f9fa;
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans",
    sans-serif;
  color: var(--text-color);
  background-color: #fff;
  line-height: 1.6;
}

.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-header {
  padding: 20px 0;
  text-align: center;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
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

.search-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
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

.trip-summary {
  margin-bottom: 20px;
  text-align: center;
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
}

.time-badge svg {
  fill: var(--primary-color);
}

.journey-container {
  margin-bottom: 24px;
}

.journey-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.line-section {
  padding-left: 16px;
  border-left: 4px solid;
  margin-bottom: 24px;
}

.line-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.line-badge {
  padding: 4px 10px;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  margin-right: 10px;
}

.line-direction {
  font-size: 14px;
  color: var(--light-text);
}

.stations-list {
  margin-left: 8px;
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
  height: 100%;
  position: absolute;
  top: 16px;
  left: 7px;
}

.station-details {
  flex: 1;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--border-color);
}

.station-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.station-time {
  font-size: 12px;
  color: var(--light-text);
}

.metro-map {
  width: 100%;
  border-radius: 8px;
}

.stations-list-container {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
  margin-top: 24px;
}

.stations-list-container h2 {
  margin-bottom: 16px;
  font-size: 18px;
  color: var(--primary-color);
}

.all-stations-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
  padding: 8px;
}

.station-list-item {
  padding: 12px;
  background-color: var(--background-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  font-size: 14px;
}

.station-id {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.station-name {
  margin-bottom: 4px;
}

.station-line {
  font-size: 12px;
  color: var(--light-text);
}

.loading-message {
  text-align: center;
  padding: 20px;
  color: var(--light-text);
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
}
</style>