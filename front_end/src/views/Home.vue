<template>
  <div>
    <h1>Metro app</h1>
    <input type="number" v-model="station1" placeholder="ID station départ">
    <input type="number" v-model="station2" placeholder="ID station arrivée">
    <button @click="call_trip(station1, station2)">Test</button>

    <p v-if="trip && trip.total_time">Total time : {{ trip.total_time }}</p>

    <div v-if="trip && trip.stations" class="map-container">
      <div
        v-for="lineObj in trip.stations"
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
                end: isLastStation(lineObj, index)
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
        ID: {{ item.id }} Station: {{ item.station }}
      </li>
    </ul>
    <div v-else>Loading...</div>

    <img class="ratp_metro" src="/metrof_r.png" alt="Plan métro">
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const data = ref(null);
const station1 = ref(0);
const station2 = ref(0);
const trip = ref(null);

onMounted(async () => {
  const response = await fetch("http://127.0.0.1:8000/station_ids");
  data.value = await response.json();
});

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
  return lineName.replace(/\s+/g, '-').toLowerCase();
}

function getColorCode(lineName) {
  const normalized = lineName.trim().toLowerCase().replace(/\s+/g, '-');
  const colors = {
    'metro-1': '#21A1E1',
    'metro-2': '#F2A201',
    'metro-3': '#BBD63D',
    'metro-3bis': '#89C1E4',
    'metro-4': '#BB60A5',
    'metro-5': '#F16745',
    'metro-6': '#7EB26D',
    'metro-7': '#B69FD3',
    'metro-7bis': '#E15792',
    'metro-8': '#E05574',
    'metro-9': '#CDC06B',
    'metro-10': '#DFA13B',
    'metro-11': '#90713C',
    'metro-12': '#3C968F',
    'metro-13': '#4C7BC6',
    'metro-14': '#A04F9E'
  };
  return colors[normalized] || '#000';
}

function isFirstStation(lineObj, index) {
  return index === 0;
}

function isLastStation(lineObj, index) {
  return index === Object.values(lineObj)[0].length - 1;
}
</script>

<style>
.ratp_metro {
  width: 500px;
  margin-top: 30px;
}

.map-container {
  margin-top: 30px;
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
  content: '';
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
</style>
