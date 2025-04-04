<template>
  <v-card>
    <v-card-title>Create New User</v-card-title>
    <v-card-text>
      <v-form v-model="valid">
        <user-name-field v-model="userItem.username" outlined autofocus />
        <user-email-field v-model="userItem.email" outlined />
        <v-checkbox
          v-model="userItem.is_staff"
          label="Is Staff"
          color="primary"
        ></v-checkbox>
        <v-checkbox
          v-model="userItem.is_superuser"
          label="Is Superuser"
          color="primary"
        ></v-checkbox>
      </v-form>
    </v-card-text>
    <v-card-actions class="ps-4">
      <v-btn
        color="secondary"
        style="text-transform: none"
        outlined
        @click="goToUsers"
        class="mr-2"
      >
        Cancel
      </v-btn>
      <v-btn
        :disabled="!valid"
        color="primary"
        style="text-transform: none"
        outlined
        @click="createUser"
      >
        Create User
      </v-btn>
    </v-card-actions>
    <v-alert v-if="successMessage" type="success" class="mt-4">
      {{ successMessage }}
    </v-alert>
    <v-alert v-if="errorMessage" type="error" class="mt-4">
      {{ errorMessage }}
    </v-alert>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue';
import UserNameField from '@/components/users/UserNameField.vue';
import UserEmailField from '@/components/users/UserEmailField.vue';
import { APIUserRepository } from '@/repositories/user/apiUserRepository';

export default Vue.extend({
  components: {
    UserNameField,
    UserEmailField,
  },

  layout: 'users',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      valid: false,
      userItem: {
        username: '',
        email: '',
        is_staff: false,
        is_superuser: false,
      },
      successMessage: '',
      errorMessage: '',
    };
  },
  methods: {
    async createUser() {
      try {
        const userRepository = new APIUserRepository();
        await userRepository.createUser(this.userItem);
        this.successMessage = 'User created successfully!';
        this.errorMessage = '';
        setTimeout(() => {
          this.$router.push('/users');
        }, 3000);
      } catch (error: any) {
          console.log('Full error object:', error); // Log the full error object
          console.log('Error response:', error.response); // Log the response object
          if (error.response && error.response.data && error.response.data.error) {
            this.errorMessage = error.response.data.error;
          } else if (error.response && error.response.data && error.response.data.detail) {
            this.errorMessage = error.response.data.detail;
          } else if (error instanceof Error) {
            this.errorMessage = error.message;
          } else {
            this.errorMessage = 'Failed to create user. Please try again.';
          }

        this.successMessage = '';

        if (error.response && error.response.status === 403) {
          setTimeout(() => {
            this.$router.push('/users');
          }, 3000);
        }

        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
      }
    },
    goToUsers() {
      this.$router.push('/users');
    },
  },
});
</script>