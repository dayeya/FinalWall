import Vuex from 'vuex'
import axios from 'axios';
import { Operation } from './ops';

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
        deployedAt: '',
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
            state.accessEvents = events
            state.allowedTransactions = events.length
        },
        updateSecurityEvents(state, events) {
            state.securityEvents = events
            state.blockedTransactions = events.length
        },
        updateAttackDistribution(state, scores) {
            state.attackDistribution = scores
        },
        updateHealth(state, health) {
            state.health = health
        },
        updateTopAttackSources(state) {
            state.attackSources = {}
            state.securityEvents.forEach(event => {
                if (!state.attackSources[event.ip]) {
                    state.attackSources[event.ip] = 0;
                }
                state.attackSources[event.ip]++;
            });
            const sortedDistributions = Object.keys(state.attackSources)
            .map(ip => ({ ip: ip, times: state.attackSources[ip] }))
            .sort((a, b) => b.times - a.times);
            state.attackSources["sources"] = sortedDistributions.slice(0, 5).map((source) => source.ip);
            state.attackSources["numbers"] = sortedDistributions.slice(0, 5).map((source) => source.times);
        }
    },
    actions: {
        async updateAccessEvents() {
            await axios.get(`http://localhost:5001/api/authorized_events`)
            .then((response) => {
                if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                    // pass
                }
                this.commit('updateAccessEvents', response.data.events);
                this.commit('updateTotalTransactions');
                this.commit('updateLatestUpdate');
                this.commit('updateState');
            });
        },
        async updateSecurityEvents() {
            await axios.get(`http://localhost:5001/api/security_events`)
            .then((response) => {
                if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                    // pass
                }
                this.commit('updateSecurityEvents', response.data.events)
                this.commit('updateTotalTransactions');

                this.dispatch('updateAttackDistribution');
                this.commit('updateTopAttackSources');
                this.commit('updateLatestUpdate');
                this.commit('updateState');
            });
        },
        async updateAttackDistribution() {
            await axios.get(`http://localhost:5001/api/attack_distribution`)
            .then((response) => {
                if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                    // pass
                }
                this.commit('updateAttackDistribution', response.data.scores);
                this.commit('updateState');
            });
        },
        async updateHealth() {
            await axios.get(`http://localhost:5001/api/health`)
            .then((response) => {
                if (response.data.status == Operation.CLUSTER_HEALTH_FAILURE) {
                    // pass
                }
                this.commit('updateHealth', response.data.health);
                this.commit('updateState');
            });
        }
    }
});

export default store