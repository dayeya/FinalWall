<script>
import { mapState } from 'vuex'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default {
  components: { Bar },
  computed: {
    ...mapState([
      'attackSources'
    ]),
    buildData() {
      return {
        labels: this.attackSources["sources"],
        datasets: [
          {
            barPercentage: 0.125,
            label: 'Attack Per Public IP Address',
            backgroundColor: '#426cf5',
            data: this.attackSources["numbers"]
          }
        ]
      };
    },
    options() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: 'y',
        plugins: {
            legend: {
                display: true,
                labels: {
                    font: { family: 'Fira sans', size: 14 }
                }
            }
        }
      }
    }
  }
}
</script>

<template>
  <div class="v-admin-dashboard-bar-chart">
    <Bar :data="buildData" :options="options"/>
  </div>
</template>