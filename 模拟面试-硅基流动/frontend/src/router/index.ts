import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import Home from '../views/Home.vue';
import Interview from '../views/Interview.vue';
import Result from '../views/Result.vue';
import History from '../views/History.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/interview',
    name: 'Interview',
    component: Interview,
    props: (route: any) => ({
      job: route.query.job,
      total_questions: route.query.total_questions,
      passing_threshold: route.query.passing_threshold,
      session_id: route.query.session_id
    }),
  },
  {
    path: '/result',
    name: 'Result',
    component: Result,
  },
  {
    path: '/history',
    name: 'History',
    component: History,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

