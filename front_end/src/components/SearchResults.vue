<template>
  <div class="search-results">
    <h2>Résultats pour "{{ query }}"</h2>
    <div v-if="results.length">
      <ul>
        <li v-for="result in results" :key="result.id">
          {{ result.station }} (ID: {{ result.id }}, Ligne: {{ result.line }})
        </li>
      </ul>
    </div>
    <div v-else>
      <p>Aucun résultat trouvé.</p>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    query: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      results: [],
    };
  },
  async created() {
    try {
      const response = await fetch(`/station_ids`);
      const data = await response.json();
      const query = this.query.toLowerCase();
      this.results = data.stations
        .filter(
          (station) =>
            station.station.toLowerCase().includes(query) ||
            station.id.toString().includes(this.query)
        )
        .slice(0, 10); // Limiter à 50 résultats
    } catch (error) {
      console.error("Error searching stations:", error);
    }
  },
};
</script>

<style scoped>
.search-results {
  padding: 20px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}
</style>
