import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import { createMemoryHistory, createRouter } from 'vue-router';
import Query from '@/components/query/Query.vue';
import Manage from '@/components/manage/Manage.vue';

const routes = [
  { path: '/', component: Query },
  { path: '/query', component: Query },
  { path: '/manage', component: Manage },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes: routes
})

createApp(App)
  .use(router)    
  .mount('#app')
