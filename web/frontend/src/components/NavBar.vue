<script>
export default {
    name: 'NavBar',

    data() {
        return {
            brand: "FinalWall",
            options: [
                "Help",
                "Logout"
            ]
        }
    }
};
</script>

<template>
    <div class="nvbar">
        <div class="nvbar-brand">{{ brand }}</div>
        <ol class="nv-list">
            <li v-for="opt in options">
                <a v-bind:href="_">{{ opt }}</a>
            </li>
        </ol>
    </div>
</template>