<template>
  <div>
    <h1>Metro app</h1>
    <input type="number" name="Station 1" id="" v-model="station1">
    
    <input type="number" name="Station 2" id="" v-model="station2">
    <button @click="call_trip(station1,station2)">Test</button>


    <ul v-if="data && data.stations">
        <li v-for="item in data.stations" :key="item.id">
            ID: {{ item.id }} Station: {{ item.station }}
        </li>
    </ul>
    <div v-else>Loading...</div>
    <img class="ratp_metro" src="/metrof_r.png" alt="">
    
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const data = ref(null)

onMounted(async () => {
  const response = await fetch('http://127.0.0.1:8000/station_ids')
  data.value = await response.json()
})

async function call_trip(value1, value2) {
  const res = await fetch('http://127.0.0.1:8000/calculate_trip', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start: value1,
      end: value2
    })
  });
  const trip_data = await res.json();
  console.log(trip_data);
}

const station1 = 0
const station2 = 0
</script>

<style>
.ratp_metro{
    width: 500px;    
}
</style>