<template>
  <v-card>
    <v-card-title>Create New User</v-card-title>
    <v-card-text>
      <v-form v-model="valid">
        <first-name-field v-model="userItem.first_name" outlined autofocus />
        <last-name-field v-model="userItem.last_name" outlined />
        <user-name-field v-model="userItem.username" outlined />
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
        class="mr-2"
        @click="goToUsers"
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
    <v-alert v-if="warningMessage" type="warning" class="mt-4">
      {{ warningMessage }}
      <div v-if="generatedPassword" class="mt-2">
        <strong>Password:</strong> {{ generatedPassword }}
      </div>
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
import FirstNameField from '@/components/users/UserFirstNameField.vue';
import LastNameField from '@/components/users/UserLastNameField.vue';
import { APIUserRepository } from '@/repositories/user/apiUserRepository';
import { UserApplicationService } from '~/services/application/user/userApplicationService';

export default Vue.extend({
  components: {
    FirstNameField,
    LastNameField,
    UserNameField,
    UserEmailField,
  },

  layout: 'users',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      valid: false,
      userItem: {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        is_staff: false,
        is_superuser: false,
      },
      successMessage: '',
      errorMessage: '',
      warningMessage: '',
      generatedPassword: '',
    };
  },
  methods: {
    async createUser() {
      try {
        const repository = new APIUserRepository();
        const service = new UserApplicationService(repository);
        const { message, password } = await service.createUser({
          username: this.userItem.username,
          email: this.userItem.email,
          first_name: this.userItem.first_name,
          last_name: this.userItem.last_name,
          is_staff: this.userItem.is_staff,
          is_superuser: this.userItem.is_superuser,
        });
        
        if (message?.includes('but email could not be sent')) {
          this.warningMessage = message;
          this.generatedPassword = password || '';
          this.successMessage = '';
        } else {
          this.successMessage = message || 'User created successfully! Email Sent.';
          this.warningMessage = '';
          setTimeout(() => {
            this.$router.push('/users');
          }, 4000);
        }
        this.errorMessage = '';
      } catch (error: any) {
        this.handleError(error);
      }
    },

    handleError(error: any) {
      this.successMessage = '';
      this.warningMessage = '';
      this.errorMessage = '';
      
      if (error.response) {
        if (error.response.data?.error) {
          this.errorMessage = error.response.data.error;
        } else if (error.response.data?.detail) {
          this.errorMessage = error.response.data.detail;
        } else if (error instanceof Error) {
          this.errorMessage = error.message;
        } else {
          this.errorMessage = 'Failed to create user. Please try again.';
        }
      } else if (error.message) {
        this.errorMessage = error.message;
      } else {
        this.errorMessage = 'An unexpected error occurred.';
      }

      this.successMessage = '';

      if (error.response?.status === 403) {
        setTimeout(() => {
          this.$router.push('/users');
        }, 4000);
      }

      setTimeout(() => {
        this.errorMessage = '';
      }, 4000);
    },

    goToUsers() {
      this.$router.push('/users');
    },
  },
});
</script>