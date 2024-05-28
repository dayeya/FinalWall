<script>
import DashboardItem from './MenuItems/DashboardItem.vue'
import EventsItem from './MenuItems/EventsItem.vue'
import ClusterItem from './MenuItems/ClusterItem.vue'
import ConfigurationItem from './MenuItems/ConfigurationItem.vue'
export default {
    name: 'MenuBar',
    components: { DashboardItem, EventsItem, ClusterItem, ConfigurationItem },
    setup() {
        return {
            redirections: [
                {
                    name: "Dashboard",
                    component: DashboardItem,
                    props: { name: "Dashboard", link: "/admin/dashboard" }
                },
                {
                    name: "Clusters",
                    component: ClusterItem,
                    props: { name: "Clusters", link: "/admin/cluster" }
                },
                {
                    name: "Events",
                    path: "/admin/events",
                    component: EventsItem,
                    props: { name: "Events", link: "/admin/events" }
                },
                {
                    name: "Configuration",
                    path: "/admin/config",
                    component: ConfigurationItem,
                    props: { name: "Configuration", link: "/admin/config" }
                },
            ]
        }
    }
}
</script>

<template>
    <div class="menu-bar">
        <component 
            v-for="(item, index) in redirections" 
            :key="index"
            :is="item.component"
            v-bind="item.props"
        />
    </div>
</template>