<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'

const mapContainer = ref(null)

onMounted(() => {
  const map = new Map({
    target: mapContainer.value,
    layers: [
      new TileLayer({
        source: new OSM()
      })
    ],
    view: new View({
      center: [261845.71, 6250564.35], // coordonnée en projection EPSG:3857
      zoom: 12
    })
  })
})
</script>

<style scoped>
.map-container {
  width: 60%;
  height: 500px;
  border: 1px solid #ccc;
}
</style>
