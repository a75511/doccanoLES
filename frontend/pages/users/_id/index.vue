<template>
  <v-container class="py-8">
    <v-alert
        v-if="error"
        type="error"
        class="mb-4"
      >
        {{ error }}
  </v-alert>
    <v-card v-if="user" class="elevation-12 rounded-lg">
      <v-card-title class="d-flex align-center">
        <v-avatar color="primary" size="56" class="mr-4">
          <v-icon dark size="32">{{ mdiAccountCircle }}</v-icon>
        </v-avatar>
        <div>
          <div class="text-h5 font-weight-bold">{{ user.username }}</div>
          <div class="text-subtitle-1 text--secondary">{{ user.email }}</div>
        </div>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-6">
        <v-list class="transparent">
          <v-list-item v-if="isAdmin" class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiCardAccountDetails }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="text-subtitle-2 text--primary">ID</v-list-item-title>
              <v-list-item-subtitle 
              class="text-body-1 font-weight-medium">{{ user.id }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiAccount }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title 
              class="text-subtitle-2 text--primary">Username</v-list-item-title>
              <v-list-item-subtitle 
              class="text-body-1 font-weight-medium">{{ user.username }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item v-if="user.firstName" class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiAccountCircle }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="text-subtitle-2 text--primary">Full Name</v-list-item-title>
              <v-list-item-subtitle 
class="text-body-1 font-weight-medium">
{{ user.firstName }} {{ user.lastName }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiEmail }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="text-subtitle-2 text--primary">Email</v-list-item-title>
              <v-list-item-subtitle 
              class="text-body-1 font-weight-medium">{{ user.email }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item v-if="user.age" class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiNumeric }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="text-subtitle-2 text--primary">Age</v-list-item-title>
              <v-list-item-subtitle 
              class="text-body-1 font-weight-medium">{{ user.age }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item v-if="user.sex" class="px-0">
            <v-list-item-icon class="mr-4">
              <v-icon color="primary">{{ mdiGenderMaleFemale }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="text-subtitle-2 text--primary">Gender</v-list-item-title>
              <v-list-item-subtitle 
              class="text-body-1 font-weight-medium">{{ user.sex }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions class="px-6 pb-6">
        <v-btn
          color="primary"
          large
          class="text-capitalize"
          @click="$router.push('/users')"
        >
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Back to Users
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-skeleton-loader
      v-else
      type="card"
      class="elevation-12 rounded-lg"
    ></v-skeleton-loader>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue';
import { mapGetters } from 'vuex'
import { 
  mdiCardAccountDetails,
  mdiAccountCircle,
  mdiAccount,
  mdiEmail,
  mdiNumeric,
  mdiGenderMaleFemale,
  mdiArrowLeft,
} from '@mdi/js'
import { APIUserRepository } from '@/repositories/user/apiUserRepository';
import { UserItem } from '@/domain/models/user/user';

export default Vue.extend({
  layout: 'users',
  middleware: ['check-auth', 'auth'],
  data() {
    return {
      user: null as UserItem | null,
      isLoading: false,
      mdiCardAccountDetails,
      mdiAccountCircle,
      mdiAccount,
      mdiEmail,
      mdiNumeric,
      mdiGenderMaleFemale,
      mdiArrowLeft,
      error: '' as string,
    };
  },

  computed: {
    ...mapGetters('auth', ['isAdmin']),
  },
  
  async created() {
    await this.fetchUser();
  },

  methods: {
    async fetchUser() {
      this.isLoading = true;
      try {
        const userRepository = new APIUserRepository();
        const userId = this.$route.params.id;
        this.user = await userRepository.findById(userId);
      } catch (error) {
        this.error = 'Database Unavailable. Please try again later.'
        console.error('Error fetching user details:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
</script>

<style scoped>
.v-card {
  max-width: 800px;
  margin: 0 auto;
  overflow: hidden;
}

.v-list-item {
  transition: background-color 0.3s ease;
}

.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.v-card__actions {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

@media (max-width: 600px) {
  .v-card__title {
    flex-direction: column;
    text-align: center;
  }
  
  .v-avatar {
    margin-right: 0;
    margin-bottom: 16px;
  }
}
</style>