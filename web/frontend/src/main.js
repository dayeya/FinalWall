import './assets/main.css'

import { createApp } from 'vue'
import io from 'socket.io-client';

import App from './App.vue'
import router from './router'
import store from './static/store.js'
import { Events } from './static/ops'

const socket = io('http://localhost:5001');


// Create an event listener for each tunnel event forwarded by the backend.

socket.on(Events.AccessLogUpdate, (data) => {
    store.dispatch(
        'updateAccessEvents', 
        { events: data }
    );
});

socket.on(Events.SecurityLogUpdate, (data) => {
    store.dispatch(
        'updateSecurityEvents',
        { events: data.events, distribution: data.distribution }
    );
});

socket.on(Events.WafServicesUpdate, (data) => {
    store.dispatch(
        'updateServices', 
        { services: data }
    );
});

socket.on(Events.WafHealthUpdate, (data) => {
    store.dispatch(
        'updateHealth', 
        { health: data }
    );
});

const app = createApp(App);

app.use(store);
app.use(router);

app.mount('#app');
