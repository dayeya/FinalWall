<script>
import { RouterLink } from 'vue-router';
export default {
    props: ['name', 'link'],
    name: 'EventsItem'
}
</script>

<template>
    <div class="v-menu-item">
        <router-link :to="link">
            <svg fill="#000000" version="1.1" id="Icons" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 32 32" xml:space="preserve">
                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                <g id="SVGRepo_iconCarrier">
                    <path d="M29.6,5.2C29.3,5,29,4.9,28.7,5.1c-4.3,1.4-8.7,0.3-12-2.8c-0.4-0.4-1-0.4-1.4,0c-3.3,3.1-7.7,4.2-12,2.8 C3,4.9,2.7,5,2.4,5.2S2,5.7,2,6c0,15.7,6.9,20.9,13.6,23.9C15.7,30,15.9,30,16,30s0.3,0,0.4-0.1C23.1,26.9,30,21.7,30,6 C30,5.7,29.8,5.4,29.6,5.2z"></path>
                </g>
            </svg>
            {{ name }}
        </router-link>
    </div>
</template>