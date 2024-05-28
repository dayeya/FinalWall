<script>
import { mapState } from 'vuex';
export default {
  computed: {
    ...mapState([
      'deployedAt',
      'lastUpdate',
      'totalTransactions',
      'allowedTransactions',
      'blockedTransactions',
      'card_informations',
      'vulnerabilityScores'
    ])
  },
}
</script>

<template>
  <div class="v-admin-dashboard">
    <h1 class="v-admin-dashboard-header">Dashboard</h1>
    <div class="v-admin-dashboard-cards">
      <div>
        <p>
          <span class="v-card-title">Blocked</span><br>
          <span class="v-card-data">{{ blockedTransactions }}</span> Transactions
        </p>
      </div>
      <div>
        <p>
          <span class="v-card-title">Allowed</span><br>
          {{ allowedTransactions }} Transactions
        </p>
      </div>
      <div>
        <p>
          <span class="v-card-title">Total</span><br>
          {{ totalTransactions }} Transactions
        </p>
      </div>
      <div>
        <p>
          <span class="v-card-title">Lastest update</span><br>
          {{ lastUpdate }}
        </p>
      </div>
      <div>
        <p>
          <span class="v-card-title">Deployed at</span><br>
          {{ deployedAt }}
        </p>
      </div>
    </div>
    
  </div>
</template>
