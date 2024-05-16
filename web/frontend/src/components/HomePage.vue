<script>

export default {
  name: 'HomePage'
}
</script>

<template>
  <v-main class="con">
    <div class="flex-project-link">
      <h1 class="fwheader">FinalWall</h1>
      <h2 class="fwheader-2">An open-source Web Application Firewall engine</h2>
      <div class="g-link-con">
        <div class="g-inline-c"></div>
        <div class="g-inline-line"></div>
        <div class="g-inline-glink"><a href="https://github.com/dayeya/FinalWall">GitHub</a></div>
      </div>
    </div>
    <div class="register-panel">
      <p class="register-p">Want to protect your application?</p>
      <button class="register-btn">register.now</button>
      <img src="../assets/server.png" width="50%" height="50%"/>
    </div>
  </v-main>
</template>