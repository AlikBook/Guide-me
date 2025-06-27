<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import 'ol/ol.css'
import Feature from 'ol/Feature.js';
import Map from 'ol/Map'
import View from 'ol/View'
import Point from 'ol/geom/Point.js';
import TileLayer from 'ol/layer/Tile'
import ImageLayer from 'ol/layer/Image'
import ImageStatic from 'ol/source/ImageStatic'
import Projection from 'ol/proj/Projection.js';
import VectorLayer from 'ol/layer/Vector.js';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector.js';
import Circle from 'ol/style/Circle.js';
import Fill from 'ol/style/Fill.js';
import Icon from 'ol/style/Icon.js';
import Stroke from 'ol/style/Stroke.js';
import Style from 'ol/style/Style.js';
import { fromLonLat } from 'ol/proj'

// Variable de base
const mapContainer = ref(null)
const backendAdress = 'http://127.0.0.1:8000'
const data = ref(null)

// Location et limites V1 (pixels)
const metroImageSize = {x: 987, y: 952}
const imageBounds = [0, 0, metroImageSize.x, metroImageSize.y]

// Location et limites V2 (format EPSG:3857)
const ParisLocation = [261845.71, 6250564.35] // 2.3522, 48.8566 en ESPG:4326
const maxSw = fromLonLat([2.2242, 48.8156]) // ESPG: 4326 --> 3857
const maxNe = fromLonLat([2.4699, 48.9022])
const mapBounds = [ maxSw[0], maxSw[1], maxNe[0], maxNe[1] ]

// Eléments de la carte
/*const pointStyle = new Style({
    image: new Circle({
      radius: 3.5,
      fill: new Fill({
        color: 'white',
      }),
      stroke: new Stroke({
        color: 'red',
        width: 1.5,
      }),
    }),
  });*/
const features = []
const linesColors = {
  '1': '#0000FF', // Ligne 1
  '2': '#00FF00', // Ligne 2
  '3': '#FF0000', // Ligne 3
  '3bis': '#FF0000', // Ligne 3bis
  '4': '#FFFF00', // Ligne 4
  '5': '#FF00FF', // Ligne 5
  '6': '#00FFFF', // Ligne 6
  '7': '#FFA500', // Ligne 7
  '8': '#800080', // Ligne 8
  '9': '#008000', // Ligne 9
  '10': '#808080', // Ligne 10
  '11': '#FFC0CB', // Ligne 11
  '12': '#A52A2A', // Ligne 12
}

// Numéro de la version du projet
const version = 2

onMounted( async () => {
  // Génération de l'affichage des stations
  await getMetroPoints()
  setStationPoints()

  // Couche pour l'affichage des éléments vectoriels
  const vectorSource = new VectorSource({
    features: features,
  });
  const vectorLayer = new VectorLayer({
    source: vectorSource,
  });

  // Changement du type de map selon la version
  if(version == 1){
    const metroMapProjection = new Projection({
      code: 'IMAGE_PIXELS',
      units: 'pixels',
      extent: imageBounds
    })
    var Layer = new ImageLayer({
      source: new ImageStatic({
        url: '/metrof_r.png',
        projection: metroMapProjection,
        imageExtent: imageBounds
      })
    })
    var center = [metroImageSize.x/2, metroImageSize.y/2]
    var bounds = imageBounds
    var zoom = 1
    var view = new View({
      projection: metroMapProjection,
      center: center, 
      zoom: zoom,
      minZoom: zoom,
      extent: bounds
    })
  }
  else if(version == 2){
    var Layer = new TileLayer({
        source: new OSM()
      })
    var center = [ParisLocation[0], ParisLocation[1]]
    var bounds = mapBounds
    var zoom = 17.3
    var view = new View({
      center: center, 
      zoom: zoom,
      minZoom: zoom,
      extent: bounds
    })
  }

  // Création de la carte
  const map = new Map({
    target: mapContainer.value,
    layers: [
      Layer,
      vectorLayer
    ],
    view: view
  })
})

async function getMetroPoints(){
  /**
   * Fonction qui récupère la position des stations
   */
  if(version == 1){
    const response = await fetch( backendAdress + '/stations_position')
    data.value = await response.json()
    console.log(data.value)
  }
  else if(version == 2){
    const response = await fetch( backendAdress + '/stations_position')
    data.value = await response.json()
  }
}

async function setStationPoints(){
  /**
   * Fonction qui ajoute des points à l'emplacement des stations
   */
  if(version == 1){
    for(let lineNum in data.value){
      let line = data.value[lineNum]
      for(let stationName in line){
        let stationData = line[stationName]
        let p = new Point([stationData.x, metroImageSize.y - stationData.y])
        let f = new Feature({geometry: p})
        if(stationData.d > 2){
          var pointStyle = new Style({
            image: new Circle({
              radius: 3.5,
              fill: new Fill({
                color: 'white',
              }),
              stroke: new Stroke({
                color: linesColors[lineNum],
                width: 1.5,
              }),
            }),
          })
        }
        else{
          var pointStyle = new Style({
            image: new Circle({
              radius: 3.5,
              fill: new Fill({
                color: linesColors[lineNum],
              }),
            }),
          })
        }
        f.setStyle([pointStyle])
        features.push(f)
      }
    }
  }
  else if(version == 2){
    for(let lineNum in data.value){
      let line = data.value[lineNum]
      for(let stationName in line){
        let position = line[stationName]
        let p = new Point([(position[0]/952)*(maxSw[0]-maxNe[0])+maxNe[0], (position[1]/987)*(maxSw[1]-maxNe[1])+maxNe[1]])
        let f = new Feature({geometry: p})
        f.setStyle([pointStyle])
        features.push(f)
      }
    }
  }
}

</script>

<style scoped>
.map-container {
  width: 987px;
  height: 952px;
}
</style>
