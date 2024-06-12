<script>
import { mapState } from 'vuex';

export default {
  data() {
    return {
      currentFilter: '',

      displaySecurityEvents: false,
      displayAuthorizedEvents: true,

      filters: [],
      isDropDownOpen: false,
    };
  },
  computed: {
    ...mapState([
      'accessEvents', 
      'securityEvents',
      'toggledAdvancedAccessEvents',
      'toggledAdvancedSecurityEvents'
    ])
  },
  methods: {
    toggleAuthorizedEvents() {
      this.displayAuthorizedEvents = true;
      this.displaySecurityEvents = false;
      this.filters = ["IP", "Port", "Event ID", "Time", "Geolocation"]
    },
    toggleSecurityEvents() {
      this.displaySecurityEvents = true;
      this.displayAuthorizedEvents = false;
      this.filters = ["Activity Token", "IP", "Port", "Vulnerability", "Time", "Geolocation"]
    },
    toggleDropDown() {
      this.isDropDownOpen = !this.isDropDownOpen
    },
    setFilter(filter) {
      this.currentFilter = filter
      this.isDropDownOpen = false;
    },
    updateToggledAEvents(index) {
      this.$store.state.commit('toggleAccessEvent', index)
    },
    updateToggledSecEvents(index) {
      this.$store.state.commit('toggleSecurityEvent', index)
    }
  }
};
</script>

<template>
  <div class="v-admin-events">
    <h1 class="v-admin-events-header">Events</h1>
    <div class="v-admin-events-toolbar">
      <div class="v-admin-events-toolbar-btns">
        <button type="button" @click="toggleAuthorizedEvents">Authorized Events</button>
        <button tpye="button" @click="toggleSecurityEvents">Security Events</button>
      </div>
      <div class="v-admin-events-toolbar-filter-bar">
        <input
            v-model="currentFilter"
            class="filter-input-bar" 
            placeholder="Filter:"
            type="text"
        />
        <svg
            class="drop-down-icon"
            @click="toggleDropDown"
            fill="#000000" 
            version="1.1" 
            id="Capa_1" 
            xmlns="http://www.w3.org/2000/svg" 
            xmlns:xlink="http://www.w3.org/1999/xlink" 
            width="20px" 
            height="20px" 
            viewBox="0 0 971.986 971.986" 
            xml:space="preserve"
            >
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
            <g id="SVGRepo_iconCarrier"><g> 
            <path d="M370.216,459.3c10.2,11.1,15.8,25.6,15.8,40.6v442c0,26.601,32.1,40.101,51.1,21.4l123.3-141.3 c16.5-19.8,25.6-29.601,25.6-49.2V500c0-15,5.7-29.5,15.8-40.601L955.615,75.5c26.5-28.8,6.101-75.5-33.1-75.5h-873 c-39.2,0-59.7,46.6-33.1,75.5L370.216,459.3z"></path>
            </g></g>
        </svg>
        <div class="drop-down-menu" v-if="isDropDownOpen">
          <div v-for="(filter, index) in filters" 
            :key="index"
            @click="setFilter(filter)"
          >
          {{ filter }}
          </div>
        </div>
      </div>
    </div>
    <div class="v-admin-events-table-con">
      <div class="v-admin-events-authorized" v-if="displayAuthorizedEvents">
        <table class="v-admin-au-events-table">
          <thead>
            <tr>
              <th scope="col">Event ID</th>
              <th scope="col">Time</th>
              <th scope="col">Source IP</th>
              <th scope="col">Port</th>
              <th scope="col">Resource</th>
              <th scope="col">Request Size [bytes]</th>
              <th scope="col">Geolocation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(event, index) in accessEvents" :key="index">
            <td>{{ event.id }}</td>
            <td>{{ event.log.creation_date }}</td>
            <td>{{ event.log.ip }}</td>
            <td>{{ event.log.port }}</td>
            <td>{{ event.request.url[2] }}</td>
            <td>{{ event.request.size }}</td>
            <td>{{ event.log.geolocation["continent"] }}, {{ event.log.geolocation["country"] }}, {{ event.log.geolocation["city"] }}</td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="v-admin-events-security" v-if="displaySecurityEvents">
        <table class="v-admin-sec-events-table">
          <thead>
            <tr>
              <th scope="col">Activity Token</th>
              <th scope="col">Time</th>
              <th scope="col">Source IP</th>
              <th scope="col">Port</th>
              <th scope="col">Vulnerability</th>
              <th scope="col">Request Size [bytes]</th>
              <th scope="col">Geolocation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(event, index) in securityEvents" :key="index">
            <td>{{ event.id }}</td>
            <td>{{ event.log.creation_date }}</td>
            <td>{{ event.log.ip }}</td>
            <td>{{ event.log.port }}</td>
            <td>{{ event.log.classifiers[0] }}</td>
            <td>{{ event.request.size }}</td>
            <td>{{ event.log.geolocation["continent"] }}, {{ event.log.geolocation["country"] }}, {{ event.log.geolocation["city"] }}</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>