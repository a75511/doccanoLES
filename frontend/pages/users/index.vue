<template>
  <v-card>
    
    <user-list
      v-model="selected"
      :items="users.items"
      :is-loading="isLoading"
      :total="users.count"
      @update:query="updateQuery"
    />
  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue from 'vue'
import UserList from '~/components/users/UserList.vue'
import { Page } from '~/domain/models/page'
import { UserItem } from '~/domain/models/user/user'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'


export default Vue.extend({
  components: {
    UserList
  },
  layout: 'users',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      users: {} as Page<UserItem>,
      selected: [] as UserItem[],
      isLoading: false
    }
  },

  async fetch() {
    this.isLoading = true
    this.users = await this.$services.user.list(this.$route.query as unknown as SearchQueryData)
    this.isLoading = false
  },

  watch: {
    '$route.query': _.debounce(function() {
      // @ts-ignore
      this.$fetch()
    }, 1000)
  },

  methods: {

    updateQuery(query: object) {
      this.$router.push(query)
    }
  }
})
</script>