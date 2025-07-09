<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import 'ol/ol.css'
import Feature from 'ol/Feature.js';
import Map from 'ol/Map';
import View from 'ol/View';
import Point from 'ol/geom/Point.js';
import TileLayer from 'ol/layer/Tile';
import ImageLayer from 'ol/layer/Image';
import ImageStatic from 'ol/source/ImageStatic';
import Projection from 'ol/proj/Projection.js';
import VectorLayer from 'ol/layer/Vector.js';
import GeoJSON from 'ol/format/GeoJSON'
// import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ'
import VectorSource from 'ol/source/Vector.js';
import Circle from 'ol/style/Circle.js';
import Fill from 'ol/style/Fill.js';
// import Icon from 'ol/style/Icon.js';
import Stroke from 'ol/style/Stroke.js';
import Style from 'ol/style/Style.js';
import LineString from 'ol/geom/LineString.js';
// import { apply } from 'ol-mapbox-style';
import { fromLonLat } from 'ol/proj';

// Variable de base
const mapContainer = ref(null)
const backendAdress = 'http://127.0.0.1:8000'
const metroPoints = ref(null)

// Location et limites V1 (pixels)
const metroImageSize = {x: 987, y: 952}
const imageBounds = [0, 0, metroImageSize.x, metroImageSize.y]

// Location et limites V2 (format EPSG:3857)
const ParisLocation = [261845.71, 6250564.35] // 2.3522, 48.8566 en ESPG:4326
const maxSw = fromLonLat([2.2, 48.76]) // ESPG: 4326 --> 3857
const maxNe = fromLonLat([2.49, 48.95])
const mapBounds = [ maxSw[0], maxSw[1], maxNe[0], maxNe[1] ]

// Eléments de la carte
const features = []
const linesColors = ref(null)
const API_KEY = "vLhXmBp5kOsQj3uKFlLZ"
const linesInfo = ref(null)
const metroLinesGeojson = ref(null)
let linesIdName
let linesLayer
let stationLayer

// Vaiables de styles par défaut
const DEFAULT_LINE_WIDTH = 3
const LOW_LINE_WIDTH = 1
const HIGHLIGHT_LINE_DELTA = 3

const DEFAULT_STOP_RADIUS = 3.5
const LOW_STOP_RADIUS = 1
const HIGHLIGHT_STOP_DELTA = 2

// Numéro de la version du projet
const version = 2

const props = defineProps({
  trip: Object
})

watch(() => props.trip, (newVal, oldVal) => {
  console.log(`La prop a changé : ${JSON.stringify(oldVal, null, 2)} → ${JSON.stringify(newVal, null, 2)}`)
  if(newVal !== ''){
    highlightCourse(newVal);
  } else {
    resetHighlight()
  }
})

onMounted( async () => {
  // Génération de l'affichage des stations
  await getLinesInfo()
  await getMetroPoints()
  setStationPoints()
  getLines_id()
  
  // Affichage des lignes
  await getLinesTraces()
  linesLayer =  await setLinesTraces()

  // Couche pour l'affichage des éléments vectoriels
  const vectorSource = new VectorSource({
    features: features,
  });
  stationLayer = new VectorLayer({
    source: vectorSource,
  });

  // Changement du type de map selon la version
  if(version == 1){
    const metroMapProjection = new Projection({
      code: 'IMAGE_PIXELS',
      units: 'pixels',
      extent: imageBounds
    })
    var mapLayer = new ImageLayer({
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
    var mapLayer = new TileLayer({
        source: new XYZ({
          url: `https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=${API_KEY}`,
          tileSize: 512,
          crossOrigin: ''
        })
      })
    var center = [ParisLocation[0]/* - 1300*/, ParisLocation[1]]
    var bounds = mapBounds
    var zoom = 11.9
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
      mapLayer,
      linesLayer,
      stationLayer
    ],
    view: view
  })

  // Affichage des infobulles
  map.on('pointermove', (event) => {
    const feature = map.forEachFeatureAtPixel(event.pixel, (f) => f);
    const container = map.getTargetElement();

    if (feature && feature.get('stationName')) {
      container.setAttribute('title', feature.get('stationName'));
    } else {
      container.removeAttribute('title');
    }
  });

  // Affichage du possible trajet
  if(props.trip !== null){
    highlightCourse(props.trip)
  }
})

async function getMetroPoints(){
  /**
   * Fonction qui récupère la position des stations
   */
  if(version == 1){
    const response = await fetch( backendAdress + '/stations_position')
    metroPoints.value = await response.json()
  }
  else if(version == 2){
    const response = await fetch( backendAdress + '/stops_position')
    metroPoints.value = await response.json()
  }
}

async function getLinesInfo(){
  /**
   * Fonction qui récupère des informations sur les lignes de transport
   */
  const response = await fetch( backendAdress + '/lines_info')
  linesInfo.value = await response.json()
}

async function getLinesTraces(){
  /**
   * Fonction qui récupère le tracés des lignes de transport
   */
  if(version == 2){
    const response = await fetch( backendAdress + '/metro_lines.geojson')
    metroLinesGeojson.value = await response.json()
  }
}

async function getLines_id(){
   /**
   * Fonction qui récupère la relation entre le nom des lignes et leur id
   */
  if(version == 2){
    const response = await fetch( backendAdress + '/lines_id_name')
    linesIdName = await response.json()
  }
}

async function setLinesTraces(){
  /**
   * Fonction qui ajoute les tracés des lignes de transport à la carte
   */
  const format = new GeoJSON()
  const geojsonFeatures = format.readFeatures(metroLinesGeojson.value, {
    featureProjection: 'EPSG:3857'
  })

  const vectorSource = new VectorSource({
    features: geojsonFeatures,
  })

  const linesLayer = new VectorLayer({
    source: vectorSource,
    style: function(feature) {
      const lineColor = '#' + (feature.values_.colourweb_hexa ?? '#000000')
      return new Style({
        stroke: new Stroke({
          color: lineColor,
          width: 3,
        }),
      })
    }
  })

  return linesLayer
}

async function setStationPoints(){
  /**
   * Fonction qui ajoute des points à l'emplacement des stations
   */
  if(version == 1){
    for(let lineNum in metroPoints.value){
      let line = metroPoints.value[lineNum]
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
    var features_over = []
    for(let stop_id in metroPoints.value){
      let stop = metroPoints.value[stop_id]
      if(stop.ref!=-1){
        let p = new Point(fromLonLat([stop.long, stop.lat]))
        let f = new Feature({geometry: p})
        f.set('stationName', stop.name);
        f.setId(stop_id) 
        f.setProperties(stop)
        if (stop.line == 15){
          stop.line = "3B"
        }
        else if (stop.line == 16){
          stop.line = "7B"
        }

        var pointStyle = new Style({
          image: new Circle({
            radius: 3.5,
            fill: new Fill({
              color: '#' + (linesInfo.value.Lines[String(stop.line).trim()]?.color ?? 'CCCCCC'),
            }),/*
            stroke: new Stroke({
              color: '#' + (linesInfo.value.Lines[String(stop.line).trim()]?.color ?? 'CCCCCC'),
              width: 1.5,
            }),*/
          }),
        })
        f.setStyle([pointStyle])
        features.push(f)
      } else if (stop.line==0){
        let stop = metroPoints.value[stop_id]
        let p = new Point(fromLonLat([stop.long, stop.lat]))
        let f = new Feature({geometry: p})
        f.set('stationName', stop.name);
        if (stop.line == 15){
          stop.line = "3B"
        }
        else if (stop.line == 16){
          stop.line = "7B"
        }

        var pointStyle = new Style({
          zIndex: 10,
          image: new Circle({
            radius: 3.5,
            fill: new Fill({
              color: 'white',
            }),
            stroke: new Stroke({
              color: 'black',
              width: 1,
            }),
          }),
        })
        f.setStyle([pointStyle])
        features_over.push(f)
      }
    }
    for(let fo of features_over){
      features.push(fo)
    }
  }
}

async function setAllLowlight(){
  linesLayer.getSource().getFeatures().forEach(f => {
    const st = resolveStyle(f, linesLayer)
    const stroke = st.getStroke()
    if (stroke) stroke.setWidth(LOW_LINE_WIDTH)
    f.setStyle(st)
  })
  
  stationLayer.getSource().getFeatures().forEach(f => {
    const st = resolveStyle(f, stationLayer)
    const img = st.getImage()
    if (img) img.setRadius(LOW_STOP_RADIUS)
    f.setStyle(st)
  })
} 

async function resetHighlight(){
  linesLayer.getSource().getFeatures().forEach(f => {
    const st = resolveStyle(f, linesLayer)
    const stroke = st.getStroke()
    if (stroke) stroke.setWidth(DEFAULT_LINE_WIDTH)
    f.setStyle(st)
  })

  stationLayer.getSource().getFeatures().forEach(f => {
    const st = resolveStyle(f, stationLayer)
    const img = st.getImage()
    if (img) img.setRadius(DEFAULT_STOP_RADIUS)
    f.setStyle(st)
  })
}

async function highlightSegment(segmentStopId1, segmentStopId2){
  const ftr1 = getStopFeatureById(segmentStopId1)
  const ftr2 = getStopFeatureById(segmentStopId2)
  // On vérifie si les points existe sur la map
  if (ftr1 && ftr2) {
    // Highlight des stops
    highlightStop(segmentStopId1)
    highlightStop(segmentStopId2)
    // récupération des ref id
    let stop1Ref = ftr1.get('ref')
    let stop2Ref = ftr2.get('ref')
    if(stop1Ref === ''){
      stop1Ref = segmentStopId1
    }
    if(stop2Ref === ''){
      stop2Ref = segmentStopId2
    }
    let bOk = false
    // Parcours des lignes pour trouver celle correspondante
    const lineName = String(ftr1.get('line'))
    linesLayer.getSource().getFeatures().forEach(f => {
      // Récupération de l'id de ligne et récupération de son nom
      const res_com_id = String(f.get('idrefligc') || '')
      const res_com = linesIdName[res_com_id]

      // Récupération des id de ref des stops de la ligne
      if (res_com == lineName) {
        let loopSegmentStartId = f.get("start_id") //getStopFeatureById(f.get("start_id")).get("ref")
        let loopSegmentEndId = f.get("end_id") //getStopFeatureById(f.get("end_id")).get("ref")
        /*console.log()
        console.log()
        console.log()*/
        if (loopSegmentStartId === ''){
          loopSegmentStartId = f.get("start_id")
        }
        if (loopSegmentEndId === ''){
          loopSegmentEndId = f.get("end_id")
        }

        if ((loopSegmentStartId === stop1Ref && loopSegmentEndId === stop2Ref) || (loopSegmentStartId === stop2Ref && loopSegmentEndId === stop1Ref) /*|| f.get("shape_leng") === 47.4053594243 || f.get("shape_id") === 'C01376_IDFM:22160_IDFM:22158'*/){
          // console.log(f.get("shape_id") + "\n" + "resea: " + stop1Ref + ", " + stop2Ref + "\n" + "actua: " + loopSegmentStartId + ", " + loopSegmentEndId + "\n" + (loopSegmentStartId === stop1Ref && loopSegmentEndId === stop2Ref) || (loopSegmentStartId === stop2Ref && loopSegmentEndId === stop1Ref))
          const style = f.getStyle()
          style.getStroke().setWidth(DEFAULT_LINE_WIDTH + HIGHLIGHT_LINE_DELTA)
          f.setStyle(style)
          bOk = true
        }
      }

    })
    if(!bOk){
      const lineGeom = new LineString([ fromLonLat([ftr1.get("long"), ftr1.get("lat")]),  fromLonLat([ftr2.get("long"), ftr2.get("lat")])])

      const lineFeature = new Feature({
        geometry: lineGeom,
        name: 'to remove'
      })
      console.log(ftr1.get("lat"))

      lineFeature.setStyle(new Style({
        stroke: new Stroke({
          color: '#' + (linesInfo.value.Lines[String(ftr1.get("line")).trim()]?.color ?? 'CCCCCC'),
          width: DEFAULT_LINE_WIDTH + HIGHLIGHT_LINE_DELTA
        })
      }))
      
      linesLayer.getSource().addFeature(lineFeature)
    }
  }
}

async function highlightLine(lineName){
  await setAllLowlight()
  const shortName = lineName.replace(/^Metro\s*/i, '').trim()

  linesLayer.getSource().getFeatures().forEach(f => {
    const rsn = String(f.get('route_short_name') || '')
    if (rsn === shortName) {
      const style = f.getStyle()
      style.getStroke().setWidth(DEFAULT_LINE_WIDTH + HIGHLIGHT_LINE_DELTA)
      f.setStyle(style)
    }
  })

  stationLayer.getSource().getFeatures().forEach(f => {
    if (String(f.get('line')) === shortName) {
      const style = f.getStyle()
      style.getImage().setRadius(DEFAULT_STOP_RADIUS + HIGHLIGHT_STOP_DELTA)
      f.setStyle(style)
    }
  })
}

async function highlightCourse(course){
  /*for(let metro of route.stations){
    var tmp_stop = {}
    for(let stop of metro){
      if(tmp_stop != {}){
        highlightCourse(stop)
      }
      highlightStop(stop)
      tmp_stop = stop
    }
  }*/
  await setAllLowlight()
  /*course.stations.forEach(segment => {
    const lineName = Object.keys(segment)[0]  
    const stops = segment[lineName].map(s => s.id)
    linesLayer.getSource().getFeatures().forEach(f => {
      const rsn = String(f.get('route_short_name') || '')
      if (rsn === lineName.replace(/^Metro\s*i, '').trim()) {
        const style = f.getStyle()
        style.getStroke().setWidth(DEFAULT_LINE_WIDTH + HIGHLIGHT_LINE_DELTA)
        f.setStyle(style)
      }
    })
    stops.forEach(id => highlightStop(id))
  })*/
  for (const segment of course.stations) {
    const lineName = Object.keys(segment)[0]
    const stopIds  = segment[lineName].map(s => s.id)

    for (let i = 1; i < stopIds.length; i++) {
      await highlightSegment(stopIds[i - 1], stopIds[i])
    }
  }
}

async function highlightStop(stopId){
  const f = getStopFeatureById(stopId)
  if (!f) return
  const st = resolveStyle(f, stationLayer)
  const img = st.getImage()
  if (img) img.setRadius(DEFAULT_STOP_RADIUS + HIGHLIGHT_STOP_DELTA)
  f.setStyle(st)
  /*for(let feature of features){
    if(feature.id != stop.id){
      let style = feature.getStyle()
      let stroke = style.getStroke
      stroke.set
    }
  }*/
}

function getStopFeatureById(id) {
  return stationLayer.getSource().getFeatureById(String(id))
}

function resolveStyle(feature, layer) {
  let style = feature.getStyle()

  if (!style) {
    const layerStyle = layer.getStyle()
    style = typeof layerStyle === 'function'
      ? layerStyle(feature)
      : layerStyle
  }

  if (Array.isArray(style)) {
    style = style[0]
  }

  return style.clone ? style.clone() : style
}

</script>

<style scoped>
.map-container {
  width: 768px;
  height: 768px;
}
</style>
