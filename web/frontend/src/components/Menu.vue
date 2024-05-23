<script>
import { RouterLink } from 'vue-router'
export default {
    name: 'MenuBar',
    data() {
        return {
            redirections: [
                {name: "Admin Panel", link: "/admin/panel"},
                {name: "Configuration", link: "/admin/config"},
                {name: "Events", link: "/admin/events"},
                {name: "Clusters", link: "/admin/clusters"},
                {name: "Rules", link: "/admin/rules"}
            ]
        }
    }
}
</script>

<template>
    <div class="menu-bar">
        <router-link v-for="redirection in redirections" :key="redirection" :to="redirection.link">
            {{ redirection.name }}
        </router-link>
    </div>
</template>