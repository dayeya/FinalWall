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

// Save the state to localStorage
const saveStateToLocalStorage = (state) => {
    localStorage.setItem('vuexState', JSON.stringify(state));
};

// Load the state from localStorage
const loadStateFromLocalStorage = () => {
    const state = localStorage.getItem('vuexState');
    return state ? JSON.parse(state) : {
        deployedAt: '',
        lastUpdate: '',
        allowedTransactions: 0,
        blockedTransactions: 0,
        totalTransactions: 0,
        accessEvents: [],
        securityEvents: [],
        vulnerabilityScores: {},
    };
};

const store = new Vuex.Store({
    state: loadStateFromLocalStorage(),
    mutations: {
        updateTotalTransactions(state) {
            state.totalTransactions = state.allowedTransactions + state.blockedTransactions
            saveStateToLocalStorage(state);
        },
        updateLatestUpdate(state) {
            state.lastUpdate = currentTimeFormatted();
            saveStateToLocalStorage(state);
        },
        async updateAccessEvents(state) {
            try {
                await axios.get(`http://localhost:5001/api/authorized_events`)
                .then((response) => {
                    if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                        console.log("Failed to fetch ongoing access events.")
                    }
                    state.accessEvents = response.data.events
                    state.allowedTransactions = response.data.events.length
                    this.commit('updateTotalTransactions');
                    this.commit('updateLatestUpdate');
                    saveStateToLocalStorage(state);
                });
            } catch (error) {
                console.log(error.response.data)
            }
        },
        async updateSecurityEvents(state) {
            try {
                await axios.get(`http://localhost:5001/api/security_events`)
                .then((response) => {
                    if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                        console.log("Failed to fetch ongoing security events.")
                    }
                    state.securityEvents = response.data.events
                    state.blockedTransactions = response.data.events.length
                    this.commit('updateTotalTransactions');
                    this.commit('updateVulnerabilityScores');
                    this.commit('updateLatestUpdate');
                    saveStateToLocalStorage(state);
                });
            } catch (error) {
                console.log(error.response.data)
            }
        },
        async updateVulnerabilityScores(state) {
            try {
                await axios.get(`http://localhost:5001/api/vulnerability_scores`)
                .then((response) => {
                    if (response.data.status == Operation.CLUSTER_EVENT_FETCHING_FAILURE) {
                        console.log("Failed to fetch ongoing security events.")
                    }
                    state.vulnerabilityScores = response.data.scores
                    this.commit('updateLatestUpdate');
                    saveStateToLocalStorage(state);
                });
            } catch (error) {
                console.log(error.response.data)
            }
        }
    },
    getters: {
        getAccessEvents: (state) => { return state.accessEvents }, 
        getSecurityEvents: (state) => { return state.securityEvents },
        getClusters: (state) => { return state.clusters }
    }
});

export default store