import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import SearchResults from "./components/SearchResults.vue";

const routes = [
  { path: "/", component: Home, meta: { title: "Guide me" } },
  {
    path: "/search",
    component: SearchResults,
    meta: { title: "Search Results" },
    props: (route) => ({ query: route.query.q }),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const defaultTitle = "Metro Assistant";
  document.title = to.meta.title || defaultTitle;
  next();
});

export default router;
