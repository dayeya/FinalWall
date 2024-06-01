<script>
import { mapState } from 'vuex'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, ArcElement, Tooltip, Legend, CategoryScale } from 'chart.js'

ChartJS.register(Title, ArcElement, Tooltip, Legend, CategoryScale)

export default {
    components: { Doughnut },
    computed: {
        ...mapState([
            'attackDistribution'
        ]),
        buildData() {
            return {
                labels: ['SQLi', 'XSS', 'Unauthorization', 'Anonymization', 'Geolocation'],
                datasets: [{
                    label: 'Attack Distribution',
                    data: [
                        this.attackDistribution["Sql Injection"], 
                        this.attackDistribution["Cross Site Scripting"], 
                        this.attackDistribution["Unauthorized Access"], 
                        this.attackDistribution["Anonymization"],
                        this.attackDistribution["Banned Geolocation"]
                    ],
                    backgroundColor: [
                    'rgb(92, 4, 138)', // Sqli
                    'rgb(245, 234, 20)', // XSS
                    'rgb(245, 108, 144)', // Unauthorized Access
                    'rgb(47, 62, 89)', // Anonymization
                    'rgb(0, 128, 128)', // Banned geolocation
                    ],
                    hoverOffset: 4
                }]
            };
        },
        options() {
            return {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            font: { family: 'Fira sans', size: 16 }
                        }
                    }
                }
            }
        }
    }
};
</script>


<template>
    <div class="v-admin-dashboard-pie-chart">
        <Doughnut :data="buildData" :options="options"/>
    </div>
</template>