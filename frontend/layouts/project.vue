<template>
  <v-app>
    <the-header>
      <template #leftDrawerIcon>
        <v-app-bar-nav-icon @click="drawerLeft = !drawerLeft" />
      </template>
    </the-header>

    <v-navigation-drawer v-model="drawerLeft" app clipped>
      <the-side-bar 
        :current-role="currentUserRole"
        :project="currentProject" 
      />
    </v-navigation-drawer>

    <v-main>
      <v-container fluid fill-height>
        <v-layout justify-center>
          <v-flex fill-height>
            <nuxt />
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex'
import TheHeader from '~/components/layout/TheHeader'
import TheSideBar from '~/components/layout/TheSideBar'

export default {
  components: {
    TheSideBar,
    TheHeader
  },

  data() {
    return {
      drawerLeft: null,
      currentUserRole: null
    }
  },

  computed: {
    ...mapGetters('projects', ['currentProject'])
  },

  async created() {
    try {
      const member = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      this.currentUserRole = member.rolename
    } catch (error) {
      this.currentUserRole = null
    }
  }
}
</script>