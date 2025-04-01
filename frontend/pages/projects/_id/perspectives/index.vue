<template>
  <v-card>
    <v-card-title>
      <v-btn
        class="text-capitalize ms-2"
        :disabled="!canAssociate"
        outlined
        @click.stop="associatePerspective"
      >
        {{ $t('perspectives.associate') }}
      </v-btn>
    </v-card-title>

    <v-alert v-if="successMessage" type="success" class="mt-4">
      {{ successMessage }}
    </v-alert>
    <v-alert v-if="errorMessage" type="error" class="mt-4">
      {{ errorMessage }}
    </v-alert>

    <perspective-list
      v-model="selected"
      :items="item.items"
      :is-loading="isLoading"
      :total="item.count"
      :current-project="currentProject"
      @update:query="updateQuery"
    />
  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import { mapGetters } from 'vuex'
import Vue from 'vue'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import { PerspectiveItem } from '~/domain/models/perspective/perspective'
import { Page } from '~/domain/models/page'
import { SearchQueryData } from '~/services/application/perspectives/perspectiveApplicationService'


export default Vue.extend({
  components: {
    PerspectiveList
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  data() {
    return {
      dialogDelete: false,
      item: {} as Page<PerspectiveItem>,
      selected: [] as PerspectiveItem[],
      isLoading: false,
      successMessage: '',
      errorMessage: '',
    }
  },

  async fetch() {
    this.isLoading = true
    await this.$store.dispatch('projects/setCurrentProject', this.projectId);
    this.item = await this.$services.perspective.list(
      this.projectId,
      this.$route.query as unknown as SearchQueryData
    )
    this.isLoading = false
  },

  computed: {
    ...mapGetters('projects', {
      currentProject: 'currentProject'
    }),

    canAssociate(): boolean {
      return this.selected.length === 1
    },

    projectId(): string {
      return this.$route.params.id
    }
  },

  watch: {
    '$route.query': _.debounce(function () {
      // @ts-ignore
      this.$fetch()
    }, 1000)
  },

  methods: {
    async checkMemberProgress(): Promise<boolean> {
      try {
        const stats = await this.$repositories.metrics.fetchMemberProgress(this.projectId);

        if (stats.total === 0) {
          return true;
        }
        
        const hasCompletedMember = stats.progress.some((item) => {
          return item.done === stats.total;
        });

        return !hasCompletedMember;
      } catch (error) {
        console.error('Failed to fetch member progress:', error);
        return false; // Assume the worst-case scenario and block the association
      }
    },

    async associatePerspective() {
      if (this.selected.length === 1) {
        const canAssociate = await this.checkMemberProgress();

        if (!canAssociate) {
          this.errorMessage = "Can't change perspective: Some annotators have finished their job.";
          this.successMessage = '';

          setTimeout(() => {
            this.errorMessage = '';
          }, 3000);

          return;
        }
        const perspectiveId = this.selected[0].id;
        try {
            const response = await this.$services.perspective.assignToProject(
                this.projectId,
                perspectiveId
            );
            await this.$repositories.example.resetConfirmation(this.projectId);
            this.$store.commit('projects/updateCurrentProjectPerspective', response.data.project.perspective);

            this.successMessage = 'Perspective associated successfully. All annotations have been deleted.';
            this.errorMessage = '';

            setTimeout(() => {
                this.successMessage = '';
            }, 3000);
        } catch (error: any) {
            console.error('Failed to associate perspective:', error);
            if (error.response && error.response.data && error.response.data.detail) {
                this.errorMessage = error.response.data.detail;
            } else if (error.response && error.response.data && error.response.data.error) {
                this.errorMessage = error.response.data.error;
            } else if (error instanceof Error) {
                this.errorMessage = error.message;
            } else {
                this.errorMessage = 'Failed to associate perspective. Please try again.';
            }
            this.successMessage = '';

            setTimeout(() => {
                this.errorMessage = '';
            }, 3000);
          }
      }
    },

    updateQuery(query: object) {
      this.$router.push(query)
    },
  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}
</style>