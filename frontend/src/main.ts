import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import QueryView from '@/components/query/QueryView.vue';
import MachineView from '@/components/manage/machine/MachineView.vue';
import DocumentView from '@/components/manage/document/DocumentView.vue';
import { VueQueryPlugin } from '@tanstack/vue-query';

const routes = [
  { path: '/', component: QueryView },
  { path: '/query', component: QueryView },
  { path: '/manage/machine', component: MachineView },
  { path: '/manage/document', component: DocumentView },
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

createApp(App)
  .use(router)
  .use(VueQueryPlugin)
  .mount('#app')
