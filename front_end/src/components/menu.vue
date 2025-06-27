<template>
  <div class="menu">
    <router-link to="/">Home</router-link>
    <SearchBar />
    <button>Sign up</button>
    <button>Log in</button>
  </div>
</template>

<script>
import SearchBar from "../components/SearchBar.vue";

export default {
  components: {
    SearchBar,
  },
};
</script>

<style>
.menu {
  background-color: rgb(107, 107, 115);
  display: flex;
  justify-content: space-between;
  gap: 20px;
  height: 60px;
  align-items: center;
  padding: 0 20px;
}

.menu a {
  color: white;
  text-decoration: none;
}

.menu button {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
