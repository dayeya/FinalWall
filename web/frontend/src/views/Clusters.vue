<script>
import axios from 'axios';
import Operation from '../static/ops'
export default {
  data() {
    return {
      clusters: []
    };
  },
  mounted() { 
    this.getCurrentClusters();
  },
  methods: {
    getCurrentClusters() {
      axios.get("http://localhost:5001/clusters")
      .then((response) => {
        this.clusters = response.data.clusters
      });
    },
    createCluster() {
      axios.post("http://localhost:5001/clusters")
      .then((response) => {
          // Display a worning sign.
          if (response.data.status == Operation.CLUSTER_REGISTRATION_FAILURE) {
            console.log("Cluster creation failed!")
          }
          // Update the cluster table.
          this.getCurrentClusters();
      });
    },
    clusterReport() {
      console.log("Report incoming!")
    }
  }
};
</script>

<template>
  <div class="v-admin-clusters">
    <h1 class="v-admin-clusters-header">Clusters</h1>
    <div class="v-admin-clusters-menu">
      <button @click="createCluster">Create new cluster</button>
      <button @click="clusterReport">Download cluster report</button>
      <div>Total clusters: {{ clusters.length }}</div>
    </div>
    <table class="v-admin-clusters-table">
      <thead>
        <tr>
          <th scope="col">Cluster ID</th>
          <th scope="col">Host</th>
          <th scope="col">Endpoint</th>
          <th scope="col">Status</th>
        </tr>
      </thead>
      <tr v-for="cluster, index in clusters" :key="index">
        <td>{{ cluster.ucid }}</td>
        <td>{{ cluster.host }}</td>
        <td>{{ cluster.endpoint }}</td>
        <td>{{ cluster.status }}</td>
      </tr>
    </table>
  </div>
</template>