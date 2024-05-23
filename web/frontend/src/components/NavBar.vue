<script>
export default {
    name: 'NavBar',
    data() {
        return {
            brand: "FinalWall",
            options: [
                {name: 'Help', link: '/admin/help'},
                {name: 'Logout', link: '/'} // Redirects to home page.
            ]
        }
    }
};
</script>

<template>
    <div class="nvbar">
        <div class="nvbar-brand">{{ brand }}</div>
        <ol class="nv-list">
            <li v-for="opt in options" :key="opt">
                <router-link :to="opt.link">{{ opt.name }}</router-link>
            </li>
        </ol>
    </div>
</template>
