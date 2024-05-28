<script>
import { mapState, mapMutations } from 'vuex';
import store from '../static/store'
export default {
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
      <div class="v-admin-cluster-name">clusterName</div>
      <button class="v-admin-report_button" type="button" @click="clusterReport">Download Report</button>
    </div>
  </div>
</template>