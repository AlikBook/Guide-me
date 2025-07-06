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
                      v-for="groupedStation in filteredStations1"
                      :key="'departure-' + groupedStation.station"
                      @mousedown="selectGroupedStation(groupedStation, 1)"
                      class="suggestion-item"
                    >
                      <div class="station-info">
                        <span class="station-name">{{ groupedStation.station }}</span>
                        <span class="station-meta">
                          {{ groupedStation.lines.join(', ') }}
                          <span v-if="groupedStation.lines.length > 1" class="multiple-lines">
                            ({{ groupedStation.lines.length }} lignes)
                          </span>
                        </span>
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
                      v-for="groupedStation in filteredStations2"
                      :key="'arrival-' + groupedStation.station"
                      @mousedown="selectGroupedStation(groupedStation, 2)"
                      class="suggestion-item"
                    >
                      <div class="station-info">
                        <span class="station-name">{{ groupedStation.station }}</span>
                        <span class="station-meta">
                          {{ groupedStation.lines.join(', ') }}
                          <span v-if="groupedStation.lines.length > 1" class="multiple-lines">
                            ({{ groupedStation.lines.length }} lignes)
                          </span>
                        </span>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Time input -->
              <div class="time-input-container">
                <div class="time-icon">
                  <svg viewBox="0 0 24 24" width="20" height="20">
                    <path
                      fill="currentColor"
                      d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.7L16.2,16.2Z"
                    />
                  </svg>
                </div>
                <input
                  type="time"
                  v-model="departureTime"
                  class="time-input"
                  title="Heure de départ"
                />
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
                      {{ calculateChangesForTrip(tripOption) }} changement{{ calculateChangesForTrip(tripOption) > 1 ? 's' : '' }}
                    </span>
                    <!-- Show wheelchair accessibility -->
                    <span v-if="tripOption.timing_details && tripOption.timing_details.wheelchair_accessible" 
                          class="wheelchair-accessible" title="Accessible PMR">
                      ♿
                    </span>
                    <!-- Show wait time if available -->
                    <span v-if="tripOption.timing_details && tripOption.timing_details.total_wait_time !== undefined" 
                          class="wait-time" title="Temps d'attente total">
                      🕐 {{ Math.round(tripOption.timing_details.total_wait_time / 60) }}min
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

              <!-- Journey Time Display -->
              <div v-if="journeyTimes" class="journey-times">
                <div class="time-display">
                  <div class="departure-time">
                    <span class="time-label">Départ:</span>
                    <span class="time-value">{{ departureTime }}</span>
                  </div>
                  <div class="arrival-time">
                    <span class="time-label">Arrivée:</span>
                    <span class="time-value">{{ journeyTimes[journeyTimes.length - 1]?.time }}</span>
                  </div>
                </div>
              </div>

              <!-- Detailed timing breakdown -->
              <div v-if="currentTrip && currentTrip.timing_details" class="timing-breakdown">
                <div class="timing-items">
                  <div v-if="currentTrip.timing_details.total_travel_time > 0" class="timing-item">
                    <span class="timing-label">Voyage:</span>
                    <span class="timing-value">{{ Math.round(currentTrip.timing_details.total_travel_time / 60) }}min</span>
                  </div>
                  <div v-if="currentTrip.timing_details.total_wait_time !== undefined" class="timing-item">
                    <span class="timing-label">Attente:</span>
                    <span class="timing-value">{{ Math.round(currentTrip.timing_details.total_wait_time / 60) }}min</span>
                  </div>
                  <div v-if="currentTrip.timing_details.total_transfer_time !== undefined" class="timing-item">
                    <span class="timing-label">Correspondances:</span>
                    <span class="timing-value">{{ Math.round(currentTrip.timing_details.total_transfer_time / 60) }}min</span>
                  </div>
                  <div v-if="currentTrip.timing_details.wheelchair_accessible !== undefined" class="timing-item accessibility">
                    <span class="timing-label">Accessibilité PMR:</span>
                    <span class="accessibility-status" :class="currentTrip.timing_details.wheelchair_accessible ? 'accessible' : 'not-accessible'">
                      {{ currentTrip.timing_details.wheelchair_accessible ? '✓ Accessible' : '✗ Non accessible' }}
                    </span>
                  </div>
                </div>
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
                    <div class="line-info">
                      <div class="line-direction">
                        Descendre à : {{ getLastStation(lineObj).station }}
                      </div>
                      <div class="line-times">
                        <span class="line-start-time">{{ getLineStartTime(lineIndex) }}</span>
                        →
                        <span class="line-end-time">{{ getLineEndTime(lineIndex) }}</span>
                      </div>
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
                      <span class="connection-time" v-if="getTransferTime(lineIndex + 1)">
                        {{ getTransferTime(lineIndex + 1) }}
                      </span>
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
import { ref, onMounted, computed, watch } from "vue";

const data = ref(null);
const station1 = ref(0);
const station2 = ref(0);
const station1Input = ref("");
const station2Input = ref("");
const departureTime = ref("08:30"); // Default departure time
const trip = ref(null);
const showSuggestions1 = ref(false);
const showSuggestions2 = ref(false);
const allStations = ref([]);
const expandedLines = ref([]);
const selectedDeparture = ref(null);
const selectedArrival = ref(null);
const showTripDetails = ref(false);
const selectedTripIndex = ref(0); 

onMounted(async () => {
  const response = await fetch("http://127.0.0.1:8000/station_ids");
  const result = await response.json();
  data.value = result;
  allStations.value = result.stations;
});

// Watch for departure time changes and recalculate trip if both stations are selected
watch(departureTime, (newTime) => {
  if (station1.value && station2.value && trip.value) {
    call_trip(station1.value, station2.value);
  }
});

const filteredStations1 = computed(() => {
  if (!station1Input.value) return [];
  const query = station1Input.value.toLowerCase();
  
  // First filter stations
  const filtered = allStations.value.filter(
    (station) =>
      station.station.toLowerCase().includes(query) ||
      station.id.toString().includes(query)
  );
  
  // Group by station name
  const grouped = {};
  filtered.forEach(station => {
    const stationName = station.station;
    if (!grouped[stationName]) {
      grouped[stationName] = {
        station: stationName,
        lines: [],
        ids: []
      };
    }
    grouped[stationName].lines.push(station.line);
    grouped[stationName].ids.push(station.id);
  });
  
  // Convert to array and limit results
  return Object.values(grouped).slice(0, 5);
});

const filteredStations2 = computed(() => {
  if (!station2Input.value) return [];
  const query = station2Input.value.toLowerCase();
  
  // First filter stations
  const filtered = allStations.value.filter(
    (station) =>
      station.station.toLowerCase().includes(query) ||
      station.id.toString().includes(query)
  );
  
  // Group by station name
  const grouped = {};
  filtered.forEach(station => {
    const stationName = station.station;
    if (!grouped[stationName]) {
      grouped[stationName] = {
        station: stationName,
        lines: [],
        ids: []
      };
    }
    grouped[stationName].lines.push(station.line);
    grouped[stationName].ids.push(station.id);
  });
  
  // Convert to array and limit results
  return Object.values(grouped).slice(0, 5);
});

const journeyStats = computed(() => {
  // Use cleanedTrip data instead of raw stations data
  if (!cleanedTrip.value || cleanedTrip.value.length === 0) {
    return { totalStations: 0, changes: 0 };
  }

  const stationSet = new Set();
  cleanedTrip.value.forEach((lineObj) => {
    // Get the stations array, filtering out transfer_time
    const lineKey = Object.keys(lineObj).find(key => key !== 'transfer_time');
    if (lineKey) {
      const stations = lineObj[lineKey];
      stations.forEach((station) => {
        stationSet.add(station.id);
      });
    }
  });

  const totalStations = stationSet.size;
  const changes = cleanedTrip.value.length - 1; // Use cleaned data length
  return { totalStations, changes };
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

// Computed property for journey times
const journeyTimes = computed(() => {
  return calculateJourneyTimes(currentTrip.value, departureTime);
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

function selectGroupedStation(groupedStation, field) {
  // For grouped stations, we need to pick one ID from the available options
  // We'll use the first ID as default, but the backend algorithm will handle finding the best path
  const selectedId = groupedStation.ids[0];
  
  // Find the full station object from allStations for the selected ID
  const fullStation = allStations.value.find(station => station.id == selectedId);
  
  if (fullStation) {
    if (field === 1) {
      station1.value = selectedId;
      station1Input.value = groupedStation.station;
      selectedDeparture.value = fullStation;
      showSuggestions1.value = false;
    } else {
      station2.value = selectedId;
      station2Input.value = groupedStation.station;
      selectedArrival.value = fullStation;
      showSuggestions2.value = false;
    }
  }
}

function getLastStation(lineObj) {
  const stations = Object.values(lineObj)[0];
  return stations[stations.length - 1];
}

function getLineStartTime(lineIndex) {
  if (!journeyTimes.value || !journeyTimes.value.length || !cleanedTrip.value) return '';
  
  // First line starts at departure time
  if (lineIndex === 0) {
    return departureTime.value;
  }
  
  // Find the corresponding line change time
  const lineChangeEvents = journeyTimes.value.filter(event => event.type === 'line_change');
  if (lineIndex - 1 < lineChangeEvents.length) {
    return lineChangeEvents[lineIndex - 1].time;
  }
  
  return '';
}

function getLineEndTime(lineIndex) {
  if (!journeyTimes.value || !journeyTimes.value.length || !cleanedTrip.value) return '';
  
  // If this is the last line, return arrival time
  if (lineIndex === cleanedTrip.value.length - 1) {
    const arrivalEvent = journeyTimes.value.find(event => event.type === 'arrival');
    return arrivalEvent ? arrivalEvent.time : '';
  }
  
  // Otherwise, return the time of the next line change
  const lineChangeEvents = journeyTimes.value.filter(event => event.type === 'line_change');
  if (lineIndex < lineChangeEvents.length) {
    return lineChangeEvents[lineIndex].time;
  }
  
  return '';
}

function calculateChangesForTrip(tripOption) {
  if (!tripOption || !tripOption.stations) return 0;
  
  // Apply the same cleaning logic as cleanedTrip for this specific trip
  const stations = tripOption.stations;
  const cleaned = [];

  for (let i = 0; i < stations.length; i++) {
    const current = stations[i];
    // Get the line data, filtering out transfer_time
    const lineKey = Object.keys(current).find(key => key !== 'transfer_time');
    if (!lineKey) continue;
    
    const currentLine = current[lineKey];
    const isSingleStation = currentLine.length === 1;
    const stationName = currentLine[0].station;

    const prev = stations[i - 1];
    const next = stations[i + 1];

    const prevLineKey = prev ? Object.keys(prev).find(key => key !== 'transfer_time') : null;
    const nextLineKey = next ? Object.keys(next).find(key => key !== 'transfer_time') : null;

    const prevStations = prev && prevLineKey ? prev[prevLineKey] : null;
    const nextStations = next && nextLineKey ? next[nextLineKey] : null;

    const prevEnd = prevStations && prevStations.length ? prevStations[prevStations.length - 1].station : null;
    const nextStart = nextStations && nextStations.length ? nextStations[0].station : null;

    if (isSingleStation && (stationName === prevEnd || stationName === nextStart)) {
      continue;
    }

    cleaned.push(current);
  }

  return Math.max(0, cleaned.length - 1);
}

function getTransferTime(lineIndex) {
  // Use cleanedTrip instead of raw stations data
  if (!cleanedTrip.value || lineIndex >= cleanedTrip.value.length) return null;
  
  // Get the line segment at the specified index from cleanedTrip
  const lineSegment = cleanedTrip.value[lineIndex];
  
  // Check if this segment has transfer_time property
  if (lineSegment && lineSegment.transfer_time) {
    return lineSegment.transfer_time;
  }
  
  return null;
}

// Utility functions for time calculations
function addSecondsToTime(timeStr, seconds) {
  const [hours, minutes] = timeStr.split(':').map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  date.setSeconds(date.getSeconds() + seconds);
  
  const newHours = date.getHours().toString().padStart(2, '0');
  const newMinutes = date.getMinutes().toString().padStart(2, '0');
  return `${newHours}:${newMinutes}`;
}

function calculateJourneyTimes(currentTrip, departureTime) {
  if (!currentTrip || !currentTrip.timing_details || !currentTrip.timing_details.segment_details) {
    return null;
  }
  
  const segments = currentTrip.timing_details.segment_details;
  const journeyTimes = [];
  let currentTime = departureTime.value;
  
  // Add departure time
  journeyTimes.push({
    type: 'departure',
    time: currentTime,
    location: 'Départ'
  });
  
  // Calculate time for each segment
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i];
    
    // Add wait time
    if (segment.wait_time_seconds > 0) {
      currentTime = addSecondsToTime(currentTime, segment.wait_time_seconds);
    }
    
    // Add travel time
    currentTime = addSecondsToTime(currentTime, segment.travel_time_seconds);
    
    // Add line change time if not the last segment
    if (i < segments.length - 1) {
      const nextSegment = segments[i + 1];
      journeyTimes.push({
        type: 'line_change',
        time: currentTime,
        location: `Changement vers ${nextSegment.line}`,
        transfer_time: segment.transfer_time_seconds || 0,
        from_line: segment.line,
        to_line: nextSegment.line
      });
      
      // Add transfer time if it exists
      if (segment.transfer_time_seconds > 0) {
        currentTime = addSecondsToTime(currentTime, segment.transfer_time_seconds);
      }
    }
  }
  
  // Add arrival time
  journeyTimes.push({
    type: 'arrival',
    time: currentTime,
    location: 'Arrivée'
  });
  
  return journeyTimes;
}

async function call_trip(value1, value2) {
  const res = await fetch("http://127.0.0.1:8000/calculate_trip", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      start: value1, 
      end: value2, 
      actual_time: departureTime.value + ":00" // Convert HH:MM to HH:MM:SS format
    }),
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

.time-input-container {
  position: relative;
  margin-bottom: 12px;
}

.time-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--light-text);
}

.time-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
  background: white;
}

.time-input:focus {
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

.multiple-lines {
  font-weight: 600;
  color: var(--primary-color);
  margin-left: 8px;
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

.journey-times {
  margin-bottom: 16px;
  padding: 12px;
  background: linear-gradient(135deg, var(--primary-color), #4a4ab8);
  border-radius: 8px;
  color: white;
}

.time-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.departure-time,
.arrival-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.time-label {
  font-size: 12px;
  opacity: 0.8;
  font-weight: 500;
}

.time-value {
  font-size: 18px;
  font-weight: 600;
}

.timing-breakdown {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--background-light);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.timing-items {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.timing-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.timing-label {
  color: var(--light-text);
  font-weight: 500;
}

.timing-value {
  color: var(--text-color);
  font-weight: 600;
}

.timing-item.accessibility {
  flex: 1 0 100%;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.accessibility-status.accessible {
  color: #28a745;
  font-weight: 600;
}

.accessibility-status.not-accessible {
  color: #dc3545;
  font-weight: 600;
}

.wheelchair-accessible {
  color: #28a745;
  font-size: 16px;
  margin-left: 4px;
}

.wait-time {
  font-size: 11px;
  color: var(--light-text);
  background: rgba(255, 193, 7, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 4px;
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

.line-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.line-direction {
  font-size: 14px;
  color: var(--light-text);
}

.line-times {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 600;
}

.line-start-time,
.line-end-time {
  background: rgba(47, 47, 126, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
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
