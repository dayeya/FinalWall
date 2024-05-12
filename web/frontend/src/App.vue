<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <v-app id="inspire">
    <v-system-bar app color="primary">
      <v-spacer></v-spacer>

      <v-icon color="accent">mdi-laptop</v-icon>

      <v-icon color="accent">mdi-needle</v-icon>

      <v-icon color="accent">mdi-shield-bug</v-icon>
    </v-system-bar>

    <v-navigation-drawer
      v-model="drawer"
      app
    >
      <v-sheet
        color="grey lighten-4"
        class="pa-4"
      >
        <v-icon
          class="mb-4"
          color="primary"
          size="64"
        >mdi-virus</v-icon>

        <h1>Sparta</h1>
      </v-sheet>

      <v-divider></v-divider>
    </v-navigation-drawer>
    <RouterView />
  </v-app>
</template>