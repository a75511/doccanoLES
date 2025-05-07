<!-- pages/projects/_id/voting/index.vue -->
<template>
    <div>
  
      <v-row>
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title>
              {{ $t('voting.title') }}
              <v-chip v-if="votingStatus" small :color="statusColor" class="ml-2">
                {{ formattedStatus }}
              </v-chip>
            </v-card-title>
  
            <v-card-text>
              <v-alert v-if="errorMessage" type="error" class="mb-4">
                {{ errorMessage }}
              </v-alert>
  
              <v-alert v-if="successMessage" type="success" class="mb-4">
                {{ successMessage }}
              </v-alert>
  
              <template v-if="votingStatus">
                <div v-if="votingStatus.status === 'voting'">
                  <v-subheader>{{ $t('voting.current_guidelines') }}</v-subheader>
                  <div class="guidelines-preview pa-4 mb-4"
                  style="white-space: pre-wrap;"
                  v-html="project.guideline"></div>
  
                  <v-subheader>{{ $t('voting.cast_your_vote') }}</v-subheader>
                  <div class="d-flex justify-center my-4">
                    <v-btn
                      x-large
                      color="success"
                      :disabled="hasVoted || isLoading"
                      :loading="isSubmittingVote"
                      @click="submitVote(true)"
                    >
                      <v-icon left>{{ mdiCheckBold }}</v-icon>
                      {{ $t('voting.agree') }}
                    </v-btn>
  
                    <v-btn
                      x-large
                      color="error"
                      class="ml-4"
                      :disabled="hasVoted || isLoading"
                      :loading="isSubmittingVote"
                      @click="submitVote(false)"
                    >
                      <v-icon left>{{ mdiCloseThick }}</v-icon>
                      {{ $t('voting.disagree') }}
                    </v-btn>
                  </div>
  
                  <v-alert v-if="hasVoted" type="info" class="mt-4">
                    {{ $t('voting.already_voted') }}
                  </v-alert>
                </div>
  
                <div v-else-if="votingStatus.status === 'completed'">
                  <v-subheader>{{ $t('voting.results') }}</v-subheader>
                  <v-row class="my-4">
                    <v-col cols="6" class="text-center">
                      <v-progress-circular
                        :rotate="-90"
                        :size="150"
                        :width="15"
                        :value="votingStatus.agreeCount / votingStatus.votes.length * 100"
                        color="success"
                        
                      >
                        {{ votingStatus.agreeCount / votingStatus.votes.length*100 }}%
                      </v-progress-circular>
                      <div class="mt-2">{{ $t('voting.agreement') }}</div>
                    </v-col>
                    <v-col cols="6">
                      <div class="d-flex align-center mb-2">
                        <v-icon color="success" class="mr-2">{{ mdiCheckBold }}</v-icon>
                        <span>{{ votingStatus.agreeCount }} {{ $t('voting.agree') }}</span>
                      </div>
                      <div class="d-flex align-center">
                        <v-icon color="error" class="mr-2">{{ mdiCloseThick }}</v-icon>
                        <span>{{ votingStatus.disagreeCount }} {{ $t('voting.disagree') }}</span>
                      </div>
                    </v-col>
                  </v-row>
                  <v-subheader>{{ $t('voting.votes') }}</v-subheader>
                <v-data-table
                  :headers="voteHeaders"
                  :items="votingStatus.votes"
                  :loading="isLoading"
                  :no-data-text="$t('vuetify.noDataAvailable')"
                  hide-default-footer
                >
                  <template #[`item.agrees`]="{ item }">
                    <v-icon :color="item.agrees ? 'success' : 'error'">
                      {{ item.agrees ? mdiCheckBold : mdiCloseThick }}
                    </v-icon>
                  </template>
                  <template #[`item.votedAt`]="{ item }">
                    {{ formatDate(item.votedAt) }}
                  </template>
                </v-data-table>
                </div>
  
                <div v-else>
                  <v-alert type="info">
                    {{ $t('voting.not_started') }}
                  </v-alert>
                </div>
  
                <v-divider class="my-4"></v-divider>
  
              </template>
  
              <v-skeleton-loader v-else type="article, actions"></v-skeleton-loader>
            </v-card-text>
  
            <v-card-actions v-if="isAdmin">
              <v-btn
                v-if="votingStatus && votingStatus.status === 'not_started'"
                color="primary"
                :loading="isStartingVoting"
                @click="startVoting"
              >
                {{ $t('voting.start_voting') }}
              </v-btn>
  
              <v-btn
                v-if="votingStatus && votingStatus.status === 'voting'"
                color="primary"
                :loading="isEndingVoting"
                @click="endVoting"
              >
                {{ $t('voting.end_voting') }}
              </v-btn>

              <v-btn
v-if="votingStatus && votingStatus.status === 'completed' && votingStatus.agreementPercentage < 70"
                color="secondary"
                :loading="isCreatingFollowUp"
                @click="createFollowUp"
              >
                {{ $t('voting.create_follow_up') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>
              <v-icon left>{{ mdiInformation }}</v-icon>
              {{ $t('voting.how_it_works') }}
            </v-card-title>
            <v-card-text>
              <ol class="mb-4">
                <li v-for="(step, index) in $t('voting.steps')" :key="index" class="mb-2">
                  {{ step }}
                </li>
              </ol>
              <v-divider class="my-4"></v-divider>
              <p>{{ $t('voting.description') }}</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { mdiCheckBold, mdiCloseThick, mdiInformation, mdiVote } from '@mdi/js'
  import { useContext, toRefs } from '@nuxtjs/composition-api';
  import { mapGetters } from 'vuex'
  import { GuidelineVotingItem } from '@/domain/models/voting/voting'
  import { useProjectItem } from '@/composables/useProjectItem'
  
  export default Vue.extend({
    layout: 'project',
    middleware: ['check-auth', 'auth', 'setCurrentProject'],
  
    data() {
      return {
        breadcrumbs: [
          { 
            text: this.$t('generic.projects'), 
            disabled: false,
            to: '/projects',
            exact: true
          },
          { 
            text: this.$route.params.id,
            disabled: true,
            to: `/projects/${this.$route.params.id}`
          },
          { 
            text: this.$t('voting.title'),
            disabled: true,
            to: `/projects/${this.$route.params.id}/voting`
          }
        ],
        votingStatus: null as GuidelineVotingItem | null,
        isLoading: false,
        isStartingVoting: false,
        isSubmittingVote: false,
        isEndingVoting: false,
        isCreatingFollowUp: false,
        errorMessage: '',
        successMessage: '',
        voteHeaders: [
          { text: this.$t('voting.vote'), value: 'agrees' },
          { text: this.$t('voting.voted_at'), value: 'votedAt' },
        ],
        mdiCheckBold,
        mdiCloseThick,
        mdiInformation,
        mdiVote,
        projectState: {} as ReturnType<typeof useProjectItem>['state']
      }
    },
  
    setup() {
      const { params } = useContext()
      const projectId = params.value.id
      const { state: projectState, getProjectById } = useProjectItem()

      getProjectById(projectId);

      return {
        ...toRefs(projectState),
      };
    },
  
    computed: {
      ...mapGetters({
        isAdmin: 'auth/isAdmin',
        userId: 'auth/getUserId'
      }),
  
      projectId(): string {
        return this.$route.params.id
      },
  
      project(): any {
        return this.projectState.project || {}
      },
  
      hasVoted(): boolean {
        return this.votingStatus?.votes?.some(v => v.userId === this.userId) || false
      },
  
      formattedStatus(): string {
        return this.votingStatus 
          ? String(this.$t(`voting.status.${this.votingStatus.status}`))
          : ''
      },
  
      statusColor(): string {
        switch (this.votingStatus?.status) {
          case 'not_started': return 'grey'
          case 'voting': return 'primary'
          case 'completed': return 'success'
          default: return ''
        }
      }
    },
  
    async mounted() {
      await this.loadVotingData()
    },
  
    methods: {
      async loadVotingData() {
          try {
              this.isLoading = true
              this.votingStatus = await this.$services.voting.getVotingStatus(this.projectId)
              console.log(this.votingStatus)
          } catch (error) {
              // this.handleError(error, 'Failed to load voting data')
              this.handleError(error, 'Database Unavailable. Please try again later.')
          } finally {
              this.isLoading = false
          }
      },
  
      async handleVotingAction(action: Function, successKey: string) {
        try {
          this.errorMessage = '';
          const result = await action();
          this.votingStatus = result;
          this.showSuccess(successKey);
        } catch (error) {
          // this.handleError(error, 'Operation failed');
          this.handleError(error, 'Database Unavailable. Please try again later.')
        }
      },
  
      async startVoting() {
        await this.handleVotingAction(
          () => this.$services.voting.startVoting(this.projectId),
          'voting.started_success'
        );
      },
  
      async submitVote(agrees: boolean) {
        try {
          this.isSubmittingVote = true;
          await this.$services.voting.submitVote(this.projectId, agrees);
          this.showSuccess('voting.vote_submitted');
          await this.loadVotingData();
        } catch (error) {
          // this.handleError(error, 'Failed to submit vote');
          this.handleError(error, 'Database Unavailable. Please try again later.')
        } finally {
          this.isSubmittingVote = false;
        }
      },
  
      async endVoting() {
        await this.handleVotingAction(
          () => this.$services.voting.endVoting(this.projectId),
          'voting.ended_success'
        );
      },
  
      async createFollowUp() {
        try {
          this.isCreatingFollowUp = true
          await this.$services.voting.createFollowUp(this.projectId)
          this.showSuccess('voting.follow_up_created')
          await this.loadVotingData()
        } catch (error) {
          // this.handleError(error, 'Failed to create follow-up voting')
          this.handleError(error, 'Database Unavailable. Please try again later.')
        } finally {
          this.isCreatingFollowUp = false
        }
      },

      formatDate(dateString: string) {
        return new Date(dateString).toLocaleString();
      },
  
      handleError(error: any, defaultMessage: string) {
        this.errorMessage = error.response?.data?.detail || error.message || defaultMessage;
      },
  
      showSuccess(messageKey: string) {
        this.successMessage = String(this.$t(messageKey));
        setTimeout(() => {this.successMessage = ''}, 3000);
      }
    },
  
  });
  </script>
  
  <style scoped>
  .guidelines-preview {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #f5f5f5;
  }
  
  ol {
    padding-left: 20px;
  }
  </style>