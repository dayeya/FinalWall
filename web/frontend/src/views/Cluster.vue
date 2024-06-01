<script>
import store from '../static/store';
import { mapState, mapMutations } from 'vuex';
import SystemHealth from '../components/Health.vue';
export default {
  components: { SystemHealth },
  computed: mapState([
    'clusterName'
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
        <div>
          <p>Host: 109.106.43.2</p>
          <p>Port: 5454</p>
        </div>
        <div class="service-health" id="waf">
          <SystemHealth />
        </div>
      </div>
      <div class="v-admin-redis-service">
        <h3>Redis</h3>
        <div>
          <h4>Network</h4>
          <p>Host: localhost</p>
          <p>Port: 6379</p>
        </div>
        <div>
          <h4>Database forensics</h4>
          <p>Total transactions: 421</p>
        </div>
        <div class="service-health" id="redis">
          Health: 
        </div>
      </div>
    </div>
  </div>
</template>