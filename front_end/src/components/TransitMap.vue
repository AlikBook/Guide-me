<template>
  <div class="map-container">
    <div id="transit-map" ref="mapContainer" class="transit-map"></div>
    
    <!-- Route Information Panel -->
    <div class="route-info-panel" v-if="selectedTrip && showRouteInfo">
      <div class="route-header">
        <h4>📍 Détails du trajet</h4>
        <button @click="showRouteInfo = false" class="close-btn">×</button>
      </div>
      <div class="route-details">
        <div class="route-summary">
          <div class="route-time">
            <span class="time-value">{{ selectedTrip.time }}</span>
            <span class="time-label">min</span>
          </div>
          <div class="route-distance">
            <span class="transfers-count">{{ selectedTrip.transfers || 0 }} correspondance(s)</span>
          </div>
        </div>
        
        <div class="route-path">
          <div class="path-item start">
            <div class="station-marker-info start-marker">🚇</div>
            <div class="station-info">
              <div class="station-name">{{ selectedTrip.departure_station }}</div>
              <div class="station-line" v-if="selectedTrip.departure_line" 
                   :style="{ color: getLineColorFromKey(selectedTrip.departure_line), fontWeight: 'bold' }">
                {{ selectedTrip.departure_line }}
              </div>
            </div>
          </div>
          
          <div v-if="selectedTrip.transfers && selectedTrip.transfers > 0" class="path-item transfer">
            <div class="station-marker-info transfer-marker">🔄</div>
            <div class="station-info">
              <div class="station-name">Correspondance{{ selectedTrip.transfers > 1 ? 's' : '' }}</div>
              <div class="station-line">{{ selectedTrip.transfers }} changement{{ selectedTrip.transfers > 1 ? 's' : '' }}</div>
            </div>
          </div>
          
          <div class="path-item end">
            <div class="station-marker-info end-marker">🏁</div>
            <div class="station-info">
              <div class="station-name">{{ selectedTrip.arrival_station }}</div>
              <div class="station-line" v-if="selectedTrip.arrival_line" 
                   :style="{ color: getLineColorFromKey(selectedTrip.arrival_line), fontWeight: 'bold' }">
                {{ selectedTrip.arrival_line }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="accessibility-info" v-if="selectedTrip.accessibility">
          <span class="accessibility-icon">♿</span>
          <span class="accessibility-text">Trajet accessible</span>
        </div>
      </div>
    </div>

    <div class="map-controls">
      <button @click="resetView" class="map-button" title="Réinitialiser la vue">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M18,11H13L14.5,9.5L13.08,8.08L12,9.16L10.92,8.08L9.5,9.5L11,11H6V13H11L9.5,14.5L10.92,15.92L12,14.84L13.08,15.92L14.5,14.5L13,13H18V11Z"/>
        </svg>
      </button>
      <button @click="toggleTrajectory" class="map-button" title="Afficher/Masquer trajet" v-if="selectedTrip">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M9,5A4,4 0 0,1 13,9A4,4 0 0,1 9,13A4,4 0 0,1 5,9A4,4 0 0,1 9,5M9,15C11.67,15 17,16.34 17,19V21H1V19C1,16.34 6.33,15 9,15M16.76,5.36L18.18,6.78L12.95,12L18.18,17.22L16.76,18.64L10.54,12.42L16.76,5.36Z"/>
        </svg>
      </button>
      <button @click="showRouteInfo = !showRouteInfo" class="map-button" title="Infos trajet" v-if="selectedTrip">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
        </svg>
      </button>
      <button @click="toggleLegend" class="map-button" title="Afficher/Masquer légende">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M9,12L11,14L15,10L20,15H4M2,6H14L16,8H20V6C20,4.89 19.1,4 18,4H14L12,2H4A2,2 0 0,0 2,4V6Z"/>
        </svg>
      </button>
      <button @click="showHelp = !showHelp" class="map-button" title="Aide">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M11,18H13V16H11V18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,6A4,4 0 0,0 8,10H10A2,2 0 0,1 12,8A2,2 0 0,1 14,10C14,12 11,11.75 11,15H13C13,12.75 16,12.5 16,10A4,4 0 0,0 12,6Z"/>
        </svg>
      </button>
      <div class="legend" v-if="showLegend">
        <div class="legend-item">
          <div class="legend-color metro-line"></div>
          <span>Lignes de métro</span>
        </div>
        <div class="legend-item">
          <div class="legend-color rer-line"></div>
          <span>Lignes RER</span>
        </div>
        <div class="legend-item">
          <div class="legend-color selected-path-colored"></div>
          <span>Trajet sélectionné (couleurs des lignes)</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker">🚇</div>
          <span>Station de départ</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker">🔄</div>
          <span>Correspondance</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker">🏁</div>
          <span>Station d'arrivée</span>
        </div>
      </div>
      <div class="help-panel" v-if="showHelp">
        <h4>🗺️ Guide de la carte</h4>
        <div class="help-section">
          <strong>Fonctionnalités:</strong>
          <ul>
            <li>🔍 Zoom avec la molette ou les boutons +/-</li>
            <li>🖱️ Déplacer en cliquant-glissant</li>
            <li>📍 Cliquer sur une station pour voir les infos</li>
            <li>🎨 Les trajets calculés sont surlignés avec les couleurs des lignes</li>
            <li>✨ Animations sur les marqueurs de correspondance</li>
          </ul>
        </div>
        <div class="help-section">
          <strong>Symboles:</strong>
          <ul>
            <li>🚇 = Gare de départ (couleur de la ligne)</li>
            <li>🏁 = Gare d'arrivée (couleur de la ligne)</li>
            <li>🔄 = Correspondance (couleur animée)</li>
            <li>♿ = Station accessible PMR</li>
          </ul>
        </div>
        <div class="help-section">
          <strong>Couleurs:</strong>
          <ul>
            <li>Chaque ligne a sa couleur officielle RATP</li>
            <li>Trajets avec contour blanc pour meilleure visibilité</li>
            <li>Lignes en pointillés colorés = segments du trajet</li>
            <li>Stations orange = correspondances multiples</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default {
  name: 'TransitMap',
  props: {
    stations: {
      type: Array,
      default: () => []
    },
    selectedTrip: {
      type: Object,
      default: null
    },
    allConnections: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      map: null,
      stationMarkers: [],
      connectionLines: [],
      trajectoryLines: [],
      showTrajectory: true,
      showLegend: true,
      showHelp: false,
      showRouteInfo: false,
      stationCoordinates: {},
      lineDefinitions: {},
      
      // Paris metro/RER line colors
      lineColors: {
        // Metro lines
        '1': '#FFCE00',
        '2': '#0055C8', 
        '3': '#837902',
        '3bis': '#87CEEB',
        '4': '#CF009E',
        '5': '#FF7E2E',
        '6': '#82DC73',
        '7': '#FA9ABA',
        '7bis': '#9ECA00',
        '8': '#CEADD2',
        '9': '#D5C900',
        '10': '#8D5524',
        '11': '#8D5524',
        '12': '#00814F',
        '13': '#87CEEB',
        '14': '#62259D',
        
        // RER lines
        'A': '#E2231A',
        'B': '#0055C8',
        'C': '#F99D1C',
        'D': '#00A88F',
        'E': '#C760FF'
      },
      
      // Default positions for Paris stations (approximate)
      parisCenter: [48.8566, 2.3522],
      defaultZoom: 11
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.initMap();
      this.loadNetworkData();
    });
  },
  watch: {
    stations: {
      handler() {
        this.updateStationMarkers();
      },
      deep: true
    },
    selectedTrip: {
      handler() {
        this.updateTrajectory();
      },
      deep: true
    }
  },
  beforeUnmount() {
    if (this.map) {
      this.map.remove();
    }
  },
  methods: {
    initMap() {
      // Make sure the container element exists
      if (!this.$refs.mapContainer) {
        console.error('Map container not found');
        return;
      }

      try {
        // Initialize the map
        this.map = L.map(this.$refs.mapContainer, {
          center: this.parisCenter,
          zoom: this.defaultZoom,
          zoomControl: true
        });

        // Add OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 18
        }).addTo(this.map);

        // Custom station icon
        this.stationIcon = L.divIcon({
          className: 'station-marker',
          html: '<div class="station-dot"></div>',
          iconSize: [8, 8],
          iconAnchor: [4, 4]
        });

        // Custom transfer station icon  
        this.transferIcon = L.divIcon({
          className: 'transfer-marker',
          html: '<div class="transfer-dot"></div>',
          iconSize: [12, 12],
          iconAnchor: [6, 6]
        });

        console.log('Map initialized successfully');
      } catch (error) {
        console.error('Error initializing map:', error);
      }
    },

    async loadNetworkData() {
      try {
        console.log('Loading network data...');
        // Fetch station coordinates and network data
        const response = await fetch('http://127.0.0.1:8000/station_coordinates');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Network data loaded successfully:', {
          stationsCount: Object.keys(data.stations || {}).length,
          linesCount: Object.keys(data.lines || {}).length
        });
        
        this.stationCoordinates = data.stations;
        this.lineDefinitions = data.lines;
        
        // Load stations and connections
        this.updateStationMarkers();
        this.addConnectionLines();
        
      } catch (error) {
        console.error('Error loading network data:', error);
        // Fallback to generated positions if API fails
        this.generateFallbackPositions();
      }
    },

    updateStationMarkers() {
      if (!this.map) {
        console.log('Map not ready yet');
        return;
      }
      
      if (!this.stations.length) {
        console.log('No stations provided yet');
        return;
      }

      console.log('Updating station markers:', this.stations.length, 'stations');

      // Clear existing markers
      this.stationMarkers.forEach(marker => this.map.removeLayer(marker));
      this.stationMarkers = [];

      // Add markers for stations with coordinates
      this.stations.forEach(station => {
        const stationName = station.station_name || station.station;
        const coords = this.stationCoordinates[stationName];
        
        if (coords) {
          const lines = station.lines || [];
          const isTransfer = lines.length > 1;
          const icon = isTransfer ? this.transferIcon : this.stationIcon;
          
          const marker = L.marker(coords, { icon })
            .bindPopup(this.createStationPopup(stationName, { 
              lines: lines, 
              wheelchair: station.wheelchair_accessible || 0 
            }))
            .addTo(this.map);
            
          this.stationMarkers.push(marker);
        } else {
          console.log('No coordinates found for station:', stationName);
        }
      });
      
      console.log('Added', this.stationMarkers.length, 'station markers');
    },

    addConnectionLines() {
      if (!this.map || !this.lineDefinitions) return;

      // Clear existing lines
      this.connectionLines.forEach(line => this.map.removeLayer(line));
      this.connectionLines = [];

      // Fetch line topology from backend and draw lines
      this.drawMetroLines();
    },

    async drawMetroLines() {
      try {
        // Get line topology from backend
        const response = await fetch('http://127.0.0.1:8000/station_coordinates');
        const data = await response.json();
        
        // Draw lines for each metro/RER line using topology
        Object.entries(data.lines).forEach(([lineId, lineInfo]) => {
          this.drawSingleLine(lineId, lineInfo);
        });
        
      } catch (error) {
        console.error('Error loading line topology:', error);
        // Fallback to grouping by station data
        this.drawLinesFallback();
      }
    },

    drawSingleLine(lineId, lineInfo) {
      // Get stations for this line from our station data
      const lineStations = [];
      
      this.stations.forEach(station => {
        const stationName = station.station_name || station.station;
        const coords = this.stationCoordinates[stationName];
        const lines = station.lines || [];
        
        if (coords && lines.includes(lineId)) {
          lineStations.push({
            name: stationName,
            lat: coords[0],
            lng: coords[1],
            order: this.getStationOrder(stationName, lineId)
          });
        }
      });

      if (lineStations.length < 2) return;

      // Sort stations by their order on the line
      lineStations.sort((a, b) => a.order - b.order);
      
      const coordinates = lineStations.map(station => [station.lat, station.lng]);
      const color = lineInfo.color || this.getLineColor(lineId);
      
      const polyline = L.polyline(coordinates, {
        color: color,
        weight: 4,
        opacity: 0.8,
        className: `line-${lineId}`
      }).addTo(this.map);
      
      // Add line label
      if (coordinates.length > 0) {
        const midPoint = coordinates[Math.floor(coordinates.length / 2)];
        const lineLabel = L.marker(midPoint, {
          icon: L.divIcon({
            className: 'line-label',
            html: `<div class="line-badge" style="background-color: ${color};">${lineInfo.type === 'rer' ? 'RER ' : ''}${lineId}</div>`,
            iconSize: [30, 20],
            iconAnchor: [15, 10]
          })
        }).addTo(this.map);
        
        this.connectionLines.push(lineLabel);
      }
      
      this.connectionLines.push(polyline);
    },

    getStationOrder(stationName, lineId) {
      // This would ideally come from the backend, but for now we'll use a simple approach
      // Return a hash-based order to maintain consistency
      return Array.from(stationName).reduce((hash, char) => {
        return char.charCodeAt(0) + ((hash << 5) - hash);
      }, 0);
    },

    drawLinesFallback() {
      // Fallback method - group stations by line
      const lineStations = {};
      
      this.stations.forEach(station => {
        const stationName = station.station_name || station.station;
        const coords = this.stationCoordinates[stationName];
        const lines = station.lines || [];
        
        if (coords) {
          lines.forEach(line => {
            if (!lineStations[line]) {
              lineStations[line] = [];
            }
            lineStations[line].push({
              name: stationName,
              lat: coords[0],
              lng: coords[1]
            });
          });
        }
      });

      // Draw lines for each metro/RER line
      Object.entries(lineStations).forEach(([line, stations]) => {
        if (stations.length < 2) return;
        
        // Sort stations by geographical position to create a logical line
        stations.sort((a, b) => a.lat - b.lat);
        
        const coordinates = stations.map(station => [station.lat, station.lng]);
        const color = this.getLineColor(line);
        
        const polyline = L.polyline(coordinates, {
          color: color,
          weight: 3,
          opacity: 0.7
        }).addTo(this.map);
        
        this.connectionLines.push(polyline);
      });
    },

    generateFallbackPositions() {
      console.log('Generating fallback positions for', this.stations.length, 'stations');
      // Fallback method if API fails
      const centerLat = 48.8566;
      const centerLng = 2.3522;
      
      this.stationCoordinates = {};
      
      this.stations.forEach((station, index) => {
        const stationName = station.station_name || station.station;
        const angle = (index * 137.5) % 360;
        const distance = 0.02 + (index % 10) * 0.008;
        
        const lat = centerLat + distance * Math.cos(angle * Math.PI / 180);
        const lng = centerLng + distance * Math.sin(angle * Math.PI / 180);
        
        this.stationCoordinates[stationName] = [lat, lng];
      });

      console.log('Generated fallback coordinates for', Object.keys(this.stationCoordinates).length, 'stations');
      this.updateStationMarkers();
      this.addConnectionLines();
    },

    updateTrajectory() {
      // Clear existing trajectory
      this.trajectoryLines.forEach(line => this.map.removeLayer(line));
      this.trajectoryLines = [];

      if (!this.selectedTrip || !this.showTrajectory) return;

      // Extract and highlight the trajectory
      this.highlightSelectedPath();
    },

    highlightSelectedPath() {
      if (!this.selectedTrip || !this.selectedTrip.stations) return;

      const allPathStations = [];
      const segmentPaths = [];

      // Process each segment of the trip
      this.selectedTrip.stations.forEach((segment, segmentIndex) => {
        Object.entries(segment).forEach(([lineKey, stations]) => {
          // Skip transfer_time entries
          if (lineKey === 'transfer_time') return;
          
          if (Array.isArray(stations)) {
            const segmentStations = [];
            
            stations.forEach(station => {
              const stationName = station.station;
              const coords = this.stationCoordinates[stationName];
              if (coords) {
                allPathStations.push({
                  name: stationName,
                  coords: coords,
                  lineKey: lineKey,
                  segmentIndex: segmentIndex
                });
                segmentStations.push({
                  name: stationName,
                  coords: coords
                });
              }
            });

            if (segmentStations.length > 1) {
              segmentPaths.push({
                lineKey: lineKey,
                stations: segmentStations,
                segmentIndex: segmentIndex
              });
            }
          }
        });
      });

      // Draw each segment with different styling
      segmentPaths.forEach((segment, index) => {
        const coordinates = segment.stations.map(s => s.coords);
        const lineColor = this.getLineColorFromKey(segment.lineKey);
        
        // Main trajectory line with actual line color
        const trajectoryLine = L.polyline(coordinates, {
          color: lineColor,
          weight: 8,
          opacity: 0.9,
          className: `trajectory-segment-${index}`
        }).addTo(this.map);

        // Highlighted overlay with line color but stronger emphasis
        const highlightLine = L.polyline(coordinates, {
          color: lineColor,
          weight: 12,
          opacity: 0.7,
          dashArray: '15, 8',
          className: `trajectory-highlight-${index}`,
          // Add a subtle shadow effect
          shadowColor: '#000000',
          shadowWeight: 16,
          shadowOpacity: 0.3
        }).addTo(this.map);

        // Add white outline for better visibility
        const outlineLine = L.polyline(coordinates, {
          color: '#FFFFFF',
          weight: 14,
          opacity: 0.6,
          className: `trajectory-outline-${index}`
        }).addTo(this.map);

        // Store lines in correct order (outline first, then highlight, then main)
        this.trajectoryLines.push(outlineLine, highlightLine, trajectoryLine);

        // Add segment markers with line color
        if (coordinates.length > 0) {
          // Start of segment marker (except for first segment)
          if (index > 0) {
            const transferMarker = L.marker(coordinates[0], {
              icon: L.divIcon({
                className: 'transfer-point',
                html: `<div class="transfer-indicator" style="background: linear-gradient(45deg, ${lineColor}, ${this.lightenColor(lineColor, 20)});">🔄</div>`,
                iconSize: [28, 28],
                iconAnchor: [14, 14]
              })
            }).bindPopup(`<strong>Correspondance</strong><br>${segment.lineKey}`)
            .addTo(this.map);
            this.trajectoryLines.push(transferMarker);
          }
        }
      });

      // Add start and end markers
      if (allPathStations.length > 0) {
        const startStation = allPathStations[0];
        const endStation = allPathStations[allPathStations.length - 1];
        
        // Get colors for start and end lines
        const startLineColor = this.getLineColorFromKey(startStation.lineKey);
        const endLineColor = this.getLineColorFromKey(endStation.lineKey);

        const startMarker = L.marker(startStation.coords, {
          icon: L.divIcon({
            className: 'journey-start',
            html: `<div class="journey-point start-point" style="background: linear-gradient(45deg, ${startLineColor}, ${this.lightenColor(startLineColor, 30)}); border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.4);">🚇</div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
          })
        }).bindPopup(`<strong>Départ:</strong> ${startStation.name}<br><span style="color: ${startLineColor}; font-weight: bold;">${startStation.lineKey}</span>`).addTo(this.map);

        const endMarker = L.marker(endStation.coords, {
          icon: L.divIcon({
            className: 'journey-end',
            html: `<div class="journey-point end-point" style="background: linear-gradient(45deg, ${endLineColor}, ${this.lightenColor(endLineColor, 30)}); border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.4);">🏁</div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
          })
        }).bindPopup(`<strong>Arrivée:</strong> ${endStation.name}<br><span style="color: ${endLineColor}; font-weight: bold;">${endStation.lineKey}</span>`).addTo(this.map);

        this.trajectoryLines.push(startMarker, endMarker);
      }

      // Fit map to trajectory with padding
      if (allPathStations.length > 0) {
        const bounds = L.latLngBounds(allPathStations.map(s => s.coords));
        this.map.fitBounds(bounds, {
          padding: [30, 30]
        });
      }
    },

    getLineColorFromKey(lineKey) {
      // Extract line number/letter from line key (e.g., "Metro 1", "RER A")
      const match = lineKey.match(/(?:Metro|RER)\s*(.+)/);
      if (match) {
        const lineId = match[1];
        return this.getLineColor(lineId);
      }
      return '#666666';
    },

    createStationPopup(stationName, stationData) {
      const linesText = (stationData.lines || []).join(', ');
      const wheelchairText = stationData.wheelchair ? '♿ Accessible' : '';
      
      return `
        <div class="station-popup">
          <strong>${stationName}</strong><br>
          <span class="lines">Lignes: ${linesText || 'Non spécifié'}</span><br>
          ${wheelchairText ? `<span class="wheelchair">${wheelchairText}</span>` : ''}
        </div>
      `;
    },

    getLineColor(line) {
      // Remove prefixes and get base line identifier
      const cleanLine = line.replace(/^(Metro|RER)\s*/, '');
      return this.lineColors[cleanLine] || '#666666';
    },

    lightenColor(color, percent) {
      // Convert hex to RGB, lighten, and convert back
      const num = parseInt(color.replace("#", ""), 16);
      const amt = Math.round(2.55 * percent);
      const R = (num >> 16) + amt;
      const G = (num >> 8 & 0x00FF) + amt;
      const B = (num & 0x0000FF) + amt;
      return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    },

    clearMap() {
      // Remove all station markers
      this.stationMarkers.forEach(marker => this.map.removeLayer(marker));
      this.stationMarkers = [];

      // Remove all connection lines
      this.connectionLines.forEach(line => this.map.removeLayer(line));
      this.connectionLines = [];

      // Remove trajectory lines
      this.trajectoryLines.forEach(line => this.map.removeLayer(line));
      this.trajectoryLines = [];
    },

    resetView() {
      this.map.setView(this.parisCenter, this.defaultZoom);
    },

    toggleTrajectory() {
      this.showTrajectory = !this.showTrajectory;
      this.updateTrajectory();
    },

    toggleLegend() {
      this.showLegend = !this.showLegend;
    }
  }
};
</script>

<style scoped>
.map-container {
  position: relative;
  height: 100%;
  width: 100%;
  min-height: 500px;
}

.transit-map {
  height: 100%;
  width: 100%;
  min-height: 500px;
  border-radius: 12px;
  overflow: hidden;
}

/* Route Information Panel */
.route-info-panel {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.route-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #333;
}

.route-details {
  padding: 20px;
}

.route-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
}

.route-time {
  text-align: center;
}

.time-value {
  font-size: 24px;
  font-weight: bold;
  display: block;
}

.time-label {
  font-size: 12px;
  opacity: 0.8;
}

.route-distance {
  text-align: center;
}

.transfers-count {
  font-size: 14px;
  font-weight: 500;
}

.route-path {
  margin-bottom: 15px;
}

.path-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  transition: background 0.2s ease;
}

.path-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.path-item.start {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
}

.path-item.transfer {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 183, 77, 0.1));
}

.path-item.end {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(239, 83, 80, 0.1));
}

.station-marker-info {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-right: 12px;
  font-size: 14px;
  font-weight: bold;
}

.start-marker {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
}

.transfer-marker {
  background: linear-gradient(135deg, #FF9800, #FFB74D);
  color: white;
}

.end-marker {
  background: linear-gradient(135deg, #F44336, #EF5350);
  color: white;
}

.station-info {
  flex: 1;
}

.station-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.station-line {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.accessibility-info {
  display: flex;
  align-items: center;
  padding: 10px;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.accessibility-icon {
  margin-right: 8px;
  font-size: 16px;
}

.accessibility-text {
  color: #2E7D32;
  font-weight: 500;
  font-size: 14px;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1000;
}

.map-button {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.legend {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 12px;
  font-size: 12px;
  min-width: 150px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.help-panel {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 8px;
  padding: 16px;
  font-size: 12px;
  max-width: 280px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  max-height: 400px;
  overflow-y: auto;
}

.help-panel h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
}

.help-section {
  margin-bottom: 12px;
}

.help-section:last-child {
  margin-bottom: 0;
}

.help-section strong {
  color: #555;
  display: block;
  margin-bottom: 4px;
}

.help-section ul {
  margin: 0;
  padding-left: 16px;
  list-style-type: none;
}

.help-section li {
  margin-bottom: 2px;
  font-size: 11px;
  line-height: 1.4;
}

.help-section li::before {
  content: "•";
  color: #007bff;
  margin-right: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-color {
  width: 16px;
  height: 3px;
  border-radius: 2px;
}

.legend-color.metro-line {
  background: #0055C8;
}

.legend-color.rer-line {
  background: #E2231A;
}

.legend-color.selected-path {
  background: #FF0000;
}

.legend-color.selected-path-colored {
  background: linear-gradient(90deg, #0055C8, #E2231A, #82DC73);
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.legend-marker {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border-radius: 50%;
  background: linear-gradient(45deg, #4CAF50, #2196F3);
  color: white;
}

/* Custom marker styles */
:deep(.station-marker) {
  background: transparent;
  border: none;
}

:deep(.station-dot) {
  width: 8px;
  height: 8px;
  background: #2196F3;
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

:deep(.transfer-marker) {
  background: transparent;
  border: none;
}

:deep(.transfer-dot) {
  width: 12px;
  height: 12px;
  background: #FF9800;
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

:deep(.station-popup) {
  font-family: inherit;
}

:deep(.station-popup .lines) {
  color: #666;
  font-size: 12px;
}

:deep(.station-popup .wheelchair) {
  color: #4CAF50;
  font-size: 12px;
}

:deep(.start-marker), :deep(.end-marker) {
  background: transparent;
  border: none;
}

:deep(.start-dot), :deep(.end-dot) {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-size: 12px;
}

:deep(.line-label) {
  background: transparent;
  border: none;
}

:deep(.line-badge) {
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-size: 10px;
  font-weight: bold;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  min-width: 20px;
}

:deep(.journey-start), :deep(.journey-end), :deep(.transfer-point) {
  background: transparent;
  border: none;
}

:deep(.journey-point) {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 14px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
}

:deep(.start-point) {
  background: linear-gradient(45deg, #4CAF50, #66BB6A);
  color: white;
}

:deep(.end-point) {
  background: linear-gradient(45deg, #F44336, #EF5350);
  color: white;
}

:deep(.transfer-indicator) {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.4);
  border: 2px solid white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

:deep(.journey-point) {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  animation: bounce 3s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-3px); }
  60% { transform: translateY(-2px); }
}

/* Responsive design */
@media (max-width: 768px) {
  .legend {
    font-size: 10px;
    padding: 8px;
    min-width: 120px;
  }
  
  .map-button {
    padding: 6px;
  }
  
  .map-button svg {
    width: 16px;
    height: 16px;
  }
  
  .route-info-panel {
    width: 100% !important;
    left: 0 !important;
    bottom: 0 !important;
    top: auto !important;
    border-radius: 15px 15px 0 0;
  }
}
</style>
