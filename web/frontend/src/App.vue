<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue';
import MenuBar from './components/Menu.vue'
</script>

<template>
  <main class="v-main-container">
    <NavBar />
    <div class="v-content-container">
      <MenuBar /> 
      <RouterView />
    </div>
  </main>
</template>