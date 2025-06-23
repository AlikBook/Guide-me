<template>
  <div>
    <h1>Metro app</h1>

    <div class="search-container">
      <input
        type="text"
        v-model="station1Input"
        @input="filterStations(1)"
        @focus="showSuggestions1 = true"
        @blur="hideSuggestions(1)"
        placeholder="Rechercher station départ..."
      />
      <ul v-if="showSuggestions1 && filteredStations1.length" class="suggestions">
        <li
          v-for="station in filteredStations1"
          :key="'departure-' + station.id"
          @mousedown="selectStation(station, 1)"
        >
          {{ station.station }} ID: {{ station.id }}, Ligne: {{ station.line }}
        </li>
      </ul>
    </div>

    <div class="search-container">
      <input
        type="text"
        v-model="station2Input"
        @input="filterStations(2)"
        @focus="showSuggestions2 = true"
        @blur="hideSuggestions(2)"
        placeholder="Rechercher station arrivée..."
      />
      <ul v-if="showSuggestions2 && filteredStations2.length" class="suggestions">
        <li
          v-for="station in filteredStations2"
          :key="'arrival-' + station.id"
          @mousedown="selectStation(station, 2)"
        >
          {{ station.station }} (ID: {{ station.id }}, Ligne: {{ station.line }})
        </li>
      </ul>
    </div>

    <button @click="call_trip(station1, station2)">Calculer trajet</button>

    <p v-if="trip && trip.total_time">Total time : {{ trip.total_time }}</p>

    <div v-if="trip && trip.stations" class="map-container">
      <div
        v-for="lineObj in cleanedTrip"
        :key="Object.keys(lineObj)[0]"
        class="line-section line-visual"
        :class="getLineClass(Object.keys(lineObj)[0])"
        :style="{ '--line-color': getColorCode(Object.keys(lineObj)[0]) }"
      >
        <h3 class="line-name">{{ Object.keys(lineObj)[0] }}</h3>
        <div class="line-track">
          <div
            v-for="(station, index) in Object.values(lineObj)[0]"
            :key="station.id"
            class="station-entry"
          >
            <div
              class="circle"
              :class="{
                start: isFirstStation(lineObj, index),
                end: isLastStation(lineObj, index),
              }"
            ></div>
            <span class="station-label">{{ station.station }}</span>
          </div>
        </div>
      </div>
    </div>

    <br />
    <h1>All the station IDS</h1>
    <ul v-if="data && data.stations">
      <li v-for="item in data.stations" :key="item.id">
        ID: {{ item.id }} Station: {{ item.station }} line: {{ item.line }}
      </li>
    </ul>
    <div v-else>Loading...</div>

    <img class="ratp_metro" src="/metrof_r.png" alt="Plan métro" />
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

const filteredStations1 = computed(() => {
  if (!station1Input.value) return [];
  const query = station1Input.value.toLowerCase();
  return allStations.value
    .filter(
      (station) =>
        station.station.toLowerCase().includes(query) ||
        station.id.toString().includes(query)
    )
    .slice(0, 10);
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
    .slice(0, 10);
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
    station1Input.value = `${station.station} (Ligne: ${station.line})`;
    showSuggestions1.value = false;
  } else {
    station2.value = station.id;
    station2Input.value = `${station.station} (Ligne: ${station.line})`; 
    showSuggestions2.value = false;
  }
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

function getLineClass(lineName) {
  return lineName.replace(/\s+/g, "-").toLowerCase();
}

function getColorCode(lineName) {
  const normalized = lineName.trim().toLowerCase().replace(/\s+/g, "-");
  const colors = {
    "metro-1": "#21A1E1",
    "metro-2": "#F2A201",
    "metro-3": "#BBD63D",
    "metro-3bis": "#89C1E4",
    "metro-4": "#BB60A5",
    "metro-5": "#F16745",
    "metro-6": "#7EB26D",
    "metro-7": "#B69FD3",
    "metro-7bis": "#E15792",
    "metro-8": "#E05574",
    "metro-9": "#CDC06B",
    "metro-10": "#DFA13B",
    "metro-11": "#90713C",
    "metro-12": "#3C968F",
    "metro-13": "#4C7BC6",
    "metro-14": "#A04F9E",
  };
  return colors[normalized] || "#000";
}

function isFirstStation(lineObj, index) {
  return index === 0;
}

function isLastStation(lineObj, index) {
  return index === Object.values(lineObj)[0].length - 1;
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
      nextStations && nextStations.length
        ? nextStations[0].station
        : null;

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
.ratp_metro {
  width: 500px;
  margin-top: 30px;
}

.map-container {
  margin-top: 30px;
  border: 4px solid rgb(85, 30, 10);
  border-radius: 50px;
  margin-left: 8%;
  margin-right: 65%;
  padding-left: 5%;
  padding-top: 3%;
  font-family: Arial, Helvetica, sans-serif;
  background-color: rgb(221, 230, 230);
}

.line-section {
  margin-bottom: 40px;
}

.line-name {
  font-weight: bold;
  margin-bottom: 10px;
}

.line-track {
  position: relative;
  padding-left: 30px;
  margin-left: 20px;
}

.line-track::before {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 6px;
  width: 4px;
  background-color: var(--line-color);
  border-radius: 2px;
  z-index: 1;
}

.station-entry {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 14px;
}

.circle {
  width: 12px;
  height: 12px;
  border: 2px solid var(--line-color);
  background-color: white;
  border-radius: 50%;
  position: absolute;
  left: -28px;
  top: 2px;
  z-index: 2;
}

.circle.start,
.circle.end {
  background-color: var(--line-color);
}

.station-label {
  font-size: 14px;
  color: #111;
}

.search-container {
  position: relative;
  margin-bottom: 15px;
  width: 300px;
}

.search-container input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  list-style: none;
  padding: 0;
  margin: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  max-height: 300px;
  overflow-y: auto;
}

.suggestions li {
  padding: 8px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.suggestions li:hover {
  background-color: #f5f5f5;
}

button {
  padding: 8px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

button:hover {
  background-color: #45a049;
}
</style>
