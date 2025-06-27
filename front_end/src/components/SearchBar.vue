<template>
  <div class="search-container">
    <input
      type="text"
      v-model="searchQuery"
      @input="handleInput"
      @focus="showSuggestions = true"
      @blur="onBlur"
      placeholder="Rechercher une station..."
    />
    <ul v-if="showSuggestions && filteredStations.length" class="suggestions">
      <li
        v-for="station in filteredStations"
        :key="station.id"
        @mousedown="selectStation(station)"
      >
        {{ station.station }} (Ligne {{ station.line }})
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: "",
      showSuggestions: false,
      allStations: [],
      selectedStation: null,
    };
  },
  computed: {
    filteredStations() {
      if (!this.searchQuery) return [];
      const query = this.searchQuery.toLowerCase();
      return this.allStations
        .filter(
          (station) =>
            station.station.toLowerCase().includes(query) ||
            station.id.toString().includes(this.searchQuery)
        )
        .slice(0, 10); // Limiter à 10 suggestions
    },
  },
  methods: {
    handleInput() {
      if (!this.searchQuery) {
        this.showSuggestions = false;
      }
    },
    selectStation(station) {
      this.searchQuery = `${station.station} (Ligne ${station.line})`;
      this.selectedStation = station;
      this.showSuggestions = false;
      this.$emit("station-selected", station);
    },
    onBlur() {
      setTimeout(() => {
        this.showSuggestions = false;
      }, 200);
    },
    async fetchAllStations() {
      try {
        const response = await fetch("/station_ids");
        const data = await response.json();
        this.allStations = data.stations.map((station) => ({
          id: station.id,
          station: station.station,
          line: this.extractLineNumber(station.station),
        }));
      } catch (error) {
        console.error("Error fetching stations:", error);
      }
    },
    extractLineNumber(stationName) {
      // Cette fonction extrait le numéro de ligne du nom de station si présent
      const match = stationName.match(/;\d+/);
      return match ? match[0].replace(";", "") : "?";
    },
  },
  mounted() {
    this.fetchAllStations();
  },
};
</script>

<style scoped>
.search-container {
  position: relative;
  width: 300px;
  margin: 0 auto;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
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
  padding: 10px;
  cursor: pointer;
}

.suggestions li:hover {
  background-color: #f0f0f0;
}
</style>
