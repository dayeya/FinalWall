<script>
import { mapState } from 'vuex'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)


export default {
    components: { Line },
    computed: {
        ...mapState([
            'health'
        ]),
        buildData() {
            return {
                labels: this.health.map((_, i) => i),
                datasets: [{
                    label: 'CPU Usage',
                    data: this.health,
                    fill: true,
                    borderColor: 'rgb(0, 156, 212)',
                    backgroundColor: 'rgb(0, 156, 212)'
                }]
            };
        },
        options() {
            return {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                  x: { title: { display: true, text: 'Time [seconds]' } },
                  y: { title: { display: true, text: 'CPU Usage [%]' } }
                }
            }
        }
    }
};
</script>


<template>
  <Line :data="buildData" :options="options"/>
</template>