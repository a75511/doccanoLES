<template>
  <v-list dense>
    <v-btn color="primary"
    class="ms-4 my-1 mb-2 text-capitalize" 
    :disabled="project.locked" nuxt @click="toLabeling">
      <v-icon left>
        {{ mdiPlayCircleOutline }}
      </v-icon>
      {{ $t('home.startAnnotation') }}
    </v-btn>
    <v-list-item-group v-model="selected" mandatory>
      <v-list-item
        v-for="(item, i) in filteredItems"
        :key="i"
        @click="$router.push(localePath(`/projects/${$route.params.id}/${item.link}`))"
      >
        <v-list-item-action>
          <v-icon>
            {{ item.icon }}
          </v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>
            {{ item.text }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list-item-group>
  </v-list>
</template>

<script>
import { mapGetters } from 'vuex'
import {
  mdiAccount,
  mdiBookOpenOutline,
  mdiChartBar,
  mdiCog,
  mdiCommentAccountOutline,
  mdiDatabase,
  mdiHome,
  mdiLabel,
  mdiPlayCircleOutline,
  mdiEyeSettings,
  mdiSetLeft,
  mdiForum,
  mdiFileChart,
  mdiVote,
} from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'

export default {
  props: {
    currentRole: {
      type: String,
      default: null,
      required: false
    },
    project: {
      type: Object,
      default: () => ({}),
      required: true
    }
  },

  middleware: ['discussion'],

  data() {
    return {
      selected: 0,
      mdiPlayCircleOutline
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    isProjectAdmin() {
      return this.currentRole === 'project_admin'
    },
    isApprover() {
      return this.currentRole === 'annotation_approver'
    },
    isAnnotator() {
      return this.currentRole === 'annotator'
    },
    hasActiveSession() {
      console.log('Checking for active session:', this.$store.state.discussion.activeSession)
      console.log('Has active session:', this.$store.getters['discussion/hasActiveSession'])
      return this.$store.getters['discussion/hasActiveSession']
    },
    hasJoinedSession() {
      return this.$store.state.discussion.hasJoined
    },
    discussionLink() {
      if (this.isProjectAdmin) {
        return this.hasActiveSession ? 'discussions' : 'discussions/sessions'
      }
      
      return this.hasJoinedSession ? 'discussions' : 'discussions/sessions'
    },
    showDiscussionsTab() {
      return this.project.locked && (this.isProjectAdmin || this.hasActiveSession)
    },

    filteredItems() {
      const items = [
        {
          icon: mdiHome,
          text: this.$t('projectHome.home'),
          link: '',
          isVisible: true
        },
        {
          icon: mdiDatabase,
          text: this.$t('dataset.dataset'),
          link: 'dataset',
          isVisible: true
        },
        {
          icon: mdiLabel,
          text: this.$t('labels.labels'),
          link: 'labels',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineLabel
        },
        {
          icon: mdiLabel,
          text: 'Relations',
          link: 'links',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineRelation
        },
        {
          icon: mdiAccount,
          text: this.$t('members.members'),
          link: 'members',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCommentAccountOutline,
          text: 'Comments',
          link: 'comments',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiBookOpenOutline,
          text: this.$t('guideline.guideline'),
          link: 'guideline',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: this.$t('statistics.statistics'),
          link: 'metrics',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCog,
          text: this.$t('settings.title'),
          link: 'settings',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiEyeSettings,
          text: this.$t('perspectives.perspectives'),
          link: 'perspectives',
          isVisible: this.isProjectAdmin || this.isApprover
        },
        {
          icon: mdiFileChart,
          text: 'Reporting',
          link: 'reporting',
          isVisible: this.isProjectAdmin || this.isApprover
        },
        {
          icon: mdiSetLeft,
          text: "Disagreements",
          link: 'disagreements',
          isVisible: (this.isProjectAdmin || this.isApprover) && this.project.projectType !== 'text' && this.project.locked
        },
        {
          icon: mdiForum,
          text: 'Discussions',
          link: this.discussionLink,
          isVisible: this.showDiscussionsTab
        },
        {
          icon: mdiVote,
          text: 'Voting',
          link: 'voting',
          isVisible: this.project.locked
        }
      ]
      return items.filter((item) => item.isVisible)
    }
  },

  methods: {
    toLabeling() {
      const query = this.$services.option.findOption(this.$route.params.id)
      const link = getLinkToAnnotationPage(this.$route.params.id, this.project.projectType)
      this.$router.push({
        path: this.localePath(link),
        query
      })
    }
  }
}
</script>