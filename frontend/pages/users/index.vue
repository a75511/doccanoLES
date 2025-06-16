<template>
  <v-card>
    <v-card-title>
      <v-btn
        v-if="isAdmin"
        class="text-capitalize"
        color="primary"
        @click="$router.push('/users/create')"
      >
        Create
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-alert
        v-if="error"
        type="error"
        class="mb-4"
      >
        {{ error }}
      </v-alert>

      <user-list
        v-model="selected"
        :items="users.items"
        :is-loading="isLoading"
        :total="users.count"
        @update:query="updateQuery"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue from 'vue'
import { mapGetters } from 'vuex'
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
      isLoading: false,
      error: '' as string
    }
  },

  async fetch() {
    this.isLoading = true
    this.error = ''
    try {
      this.users = await this.$services.user.list(this.$route.query as unknown as SearchQueryData)
    } catch (error) {
      this.error = error.message || 'Database Unavailable. Please try again later.'
      console.error('Failed to load users:', error)
    } finally {
      this.isLoading = false
    }
  },

  computed: {
    ...mapGetters('auth', ['isAdmin']),
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