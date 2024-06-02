<script>
import store from '../static/store';
import { mapState, mapMutations } from 'vuex';
import SystemHealth from '../components/Health.vue';
export default {
  components: { SystemHealth },
  computed: mapState([
    'services'
  ]),
  methods: {
    clusterReport() {
      console.log("Report incoming!")
    }
  }
};
</script>

<template>
  <div class="v-admin-cluster">
    <h1 class="v-admin-cluster-header">Cluster information</h1>
    <div class="v-admin-cluster-menu">
      <div>Cluster ID: 8585</div>
      <button>Download Report</button>
    </div>
    <h2 class="v-admin-cluster-services-header">Services</h2>
    <div class="v-admin-cluster-services">
      <div class="v-admin-waf-service">
        <h3>WAF</h3>
        <div class="v-admin-waf-service-inner">
          <div>
            <p>Host: {{ this.services["waf_host"] }}</p>
            <p>Port: {{ this.services["waf_port"] }}</p>
          </div>
          <div>
            <p>Proxy: {{ this.services["state"] }}</p>
            <p>Environment: {{ this.services["environment"] }}</p>
          </div>
          <div>
            <p>Organization Server Host: {{ this.services["organization_server_host"] }}</p>
            <p>Organization Server Port: {{ this.services["organization_server_port"] }}</p>
          </div>
        </div>
        <div class="service-health" id="waf">
          <SystemHealth />
        </div>
      </div>
      <div class="v-admin-redis-service">
        <h3>Redis</h3>
        <div class="v-admin-redis-service-inner">
          <div>
            <p>Host: {{ this.services["redis_host"] }}</p>
            <p>Port: {{ this.services["redis_port"] }}</p>
          </div>
          <div>
            <p>Cache Size: {{ this.services["cache_size"] }}</p>
            <p>Authorized Events: {{ this.services["access_events_size"] }}</p>
            <p>Security Events: {{ this.services["security_events_size"] }}</p>
          </div>
          <div>
            <p>Last authorized update: {{ this.services["last_access_update"] }}</p>
            <p>Last security update: {{ this.services["last_security_update"] }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>