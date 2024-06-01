import './assets/main.css'

import { createApp } from 'vue'
import io from 'socket.io-client';

import App from './App.vue'
import router from './router'
import store from './static/store.js'
import { Events } from './static/ops'

const socket = io('http://localhost:5001');


// Create an event listener for each tunnel event forwarded by the backend.

socket.on(Events.AccessLogUpdate, () => {
    store.dispatch('updateAccessEvents');
});

socket.on(Events.SecurityLogUpdate, () => {
    store.dispatch('updateSecurityEvents');
});

socket.on(Events.WafHealthUpdate, () => {
    store.dispatch('updateHealth');
});

const app = createApp(App);

app.use(store);
app.use(router);

app.mount('#app');
