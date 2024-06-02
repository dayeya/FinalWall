import Vuex from 'vuex'
import axios from 'axios';
import { Operation } from './ops';
import Help from '@/views/Help.vue';

const currentTimeFormatted = () => {
    let now = new Date();
    let options = { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: false
    };
    let dateString = now.toLocaleString('en-GB', options);
    return dateString;
};

// Load the state from localStorage
const loadStateFromLocalStorage = () => {
    localStorage.removeItem('vuexState');
    const state = localStorage.getItem('vuexState');
    return state ? JSON.parse(state) : {
        lastUpdate: '',
        totalTransactions: 0,
        allowedTransactions: 0,
        blockedTransactions: 0,
        accessEvents: [],
        securityEvents: [],
        health: [],
        attackDistribution: {},
        attackSources: {
            "sources": [],
            "numbers": []
        },
        services: {}
    };
};

const store = new Vuex.Store({
    state: loadStateFromLocalStorage(),
    mutations: {
        updateState(state) {
            localStorage.setItem('vuexState', JSON.stringify(state));
        },
        updateTotalTransactions(state) {
            state.totalTransactions = state.allowedTransactions + state.blockedTransactions
        },
        updateLatestUpdate(state) {
            state.lastUpdate = currentTimeFormatted();
        },
        updateAccessEvents(state, events) {
            state.accessEvents = events.map(event => { return JSON.parse(event) });
            state.allowedTransactions = events.length
        },
        updateSecurityEvents(state, events) {
            state.securityEvents = events.map(event => { return JSON.parse(event) });
            state.blockedTransactions = events.length
        },
        updateAttackDistribution(state, scores) {
            state.attackDistribution = scores
        },
        updateHealth(state, health) {
            state.health = health
        },
        updateServices(state, services) {
            console.log(services)
            console.log(typeof services)
            state.services = services
        },
        updateDeployTime(state, time) {
            state.deployedAt = time
        },
        updateTopAttackSources(state) {
            state.attackSources = {}
            state.securityEvents.forEach(event => {
                if (!state.attackSources[event.log.ip]) {
                    state.attackSources[event.log.ip] = 0;
                }
                state.attackSources[event.log.ip]++;
            });
            const sortedDistributions = Object.keys(state.attackSources)
            .map(ip => ({ ip: ip, times: state.attackSources[ip] }))
            .sort((a, b) => b.times - a.times);
            state.attackSources["sources"] = sortedDistributions.slice(0, 5).map((source) => source.ip);
            state.attackSources["numbers"] = sortedDistributions.slice(0, 5).map((source) => source.times);
        }
    },
    actions: {
        updateAccessEvents({ commit }, { events }) {
            commit('updateAccessEvents', events);
            commit('updateTotalTransactions');
            commit('updateLatestUpdate');
            commit('updateState');
        },
        updateSecurityEvents({ commit }, { events, distribution }) {
            commit('updateSecurityEvents', events);
            commit('updateTotalTransactions');
            commit('updateLatestUpdate');
            commit('updateTopAttackSources')
            commit('updateState');
            this.dispatch('updateAttackDistribution', { distribution });
        },
        updateAttackDistribution({ commit }, { distribution }) {
            commit('updateAttackDistribution', distribution);
            commit('updateLatestUpdate');
            commit('updateState');
        },
        updateHealth({ commit }, { health }) {
            commit('updateHealth', health);
            commit('updateState');
        },
        updateServices({ commit }, { services }) {
            commit('updateServices', services);
            commit('updateState');
        }
    }
});

export default store