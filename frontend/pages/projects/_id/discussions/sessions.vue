<template>
  <div>
    <v-card v-if="isAdmin">
      <v-card-title>Discussion Sessions</v-card-title>
      
      <v-card-text>
        <!-- Show active session with close button -->
        <v-alert v-if="activeSession" type="info">
          Active session since {{ formatDate(activeSession.startedAt) }}
          <v-btn @click="closeSession" color="error" small class="ml-2">
            Close Session
          </v-btn>
          <v-btn @click="joinSession" color="primary" small class="ml-2">
            Join Session
          </v-btn>
        </v-alert>
        
        <!-- Show option to start new session when none exists -->
        <v-alert v-else type="warning">
          No active discussion session
          <v-btn @click="startSession" color="primary" small class="ml-2">
            Start New Session
          </v-btn>
        </v-alert>

        <!-- Show pending closure warning -->
        <div v-if="pendingClosure" class="mt-4">
          <v-alert type="warning">
            Session closure pending database connection
            <v-btn @click="cancelClosure" color="secondary" small class="ml-2">
              Cancel Closure
            </v-btn>
          </v-alert>
        </div>
      </v-card-text>
    </v-card>
    
    <!-- Member view -->
    <v-card v-else class="mt-4">
      <v-card-title>Discussion Session</v-card-title>
      <v-card-text>
        <div v-if="activeSession">
          <p>Active discussion session started at {{ formatDate(activeSession.startedAt) }}</p>
          <v-btn @click="joinSession" color="primary">
            Join Session
          </v-btn>
        </div>
        <div v-else>
          <p>No active discussion session</p>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import Vue from 'vue';
export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'discussion'],

  data() {
    return {
      currentRole: ''
    }
  },
  async created() {
    await this.loadCurrentRole();
    await this.fetchActiveSession();
  },
  computed: {
    isAdmin() {
      return this.currentRole === 'project_admin';
    },
    activeSession() {
      return this.$store.state.discussion.activeSession;
    },
    pendingClosure() {
      return this.$store.state.discussion.pendingClosure;
    }
  },
  methods: {
    async loadCurrentRole() {
      try {
        const role = await this.$repositories.member.fetchMyRole(this.$route.params.id);
        this.currentRole = role.rolename;
      } catch (error) {
        console.error('Failed to load current role:', error);
      }
    },
    async fetchActiveSession() {
      await this.$store.dispatch('discussion/fetchActiveSession', this.$route.params.id);
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    async startSession() {
      try {
        await this.$services.discussion.startSession(this.$route.params.id)
        this.$store.dispatch('discussion/fetchActiveSession', this.$route.params.id)
      } catch (error) {
        this.handleError(error, 'start session')
      }
    },
    async joinSession() {
      await this.$store.dispatch('discussion/joinSession', {
        projectId: this.$route.params.id,
        sessionId: this.activeSession.id
      })
      this.$router.push(`/projects/${this.$route.params.id}/discussions`)
    },
    async closeSession() {
      if (!this.activeSession) return;
      
      try {
        await this.$store.dispatch('discussion/closeSession', {
          projectId: this.$route.params.id,
          sessionId: this.activeSession.id
        });
        
        await this.$store.dispatch('discussion/fetchActiveSession', this.$route.params.id);
        
        this.successMessage = 'Session closed successfully';
      } catch (error) {
        this.handleError(error, 'close session');
      }
    },

    async cancelClosure() {
      if (!this.activeSession) return
      
      try {
        await this.$services.discussion.cancelClosure(
          this.$route.params.id,
          this.activeSession.id
        )
        this.$store.commit('discussion/setPendingClosure', false)
        this.successMessage = 'Closure cancelled successfully'
      } catch (error) {
        this.handleError(error, 'cancel closure')
      }
    },
    handleError(error, context) {
      if (error.response?.data?.error) {
        this.errorMessage = error.response.data.error
      } else if (error.response?.data?.detail) {
        this.errorMessage = error.response.data.detail
      } else if (error instanceof Error) {
        this.errorMessage = error.message
      } else {
        this.errorMessage = `Failed to ${context}. Please try again.`
      }
      setTimeout(() => { this.errorMessage = '' }, 5000)
    },
  }
})
</script>