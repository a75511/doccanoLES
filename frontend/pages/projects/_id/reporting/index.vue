<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Reporting Dashboard</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          :prepend-inner-icon="mdiMagnify"
          label="Search reports"
          single-line
          hide-details
          dark
        />
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="reports"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        @click:row="handleRowClick"
      >
        <template #[`item.reportType`]="{ item }">
          <v-chip :color="getReportColor(item.reportType)" dark>
            {{ item.reportType }}
          </v-chip>
        </template>

        <template #[`item.name`]="{ item }">
          <nuxt-link :to="localePath(`/projects/${$route.params.id}/reporting/${item.route}`)">
            {{ item.name }}
          </nuxt-link>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { mdiMagnify } from '@mdi/js'
import Vue from 'vue'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      search: '',
      mdiMagnify,
      headers: [
        { text: 'Report Name', value: 'name', sortable: true },
        { text: 'Description', value: 'description', sortable: false },
        { text: 'Type', value: 'reportType', sortable: true },
        { text: 'Last Generated', value: 'lastGenerated', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      reports: [
        {
          id: 1,
          name: 'Disagreement Statistics',
          description: 'Detailed comparison of annotator disagreements',
          reportType: 'disagreement',
          lastGenerated: '2024-03-15',
          route: 'disagreements' // Just the endpoint part
        },
        {
          id: 2,
          name: 'Disagreement Report',
          description: 'Report of annotator disagreements without charts',
          reportType: 'disagreement',
          lastGenerated: '2024-03-16',
          route: 'disagreements-report'
        },
      ]
    }
  },

  methods: {
    getReportColor(type: string) {
      const colors: { [key: string]: string } = {
        disagreement: 'red',
        annotation: 'blue',
        perspective: 'green'
      }
      return colors[type] || 'grey'
    },

    handleRowClick(item: any) {
      this.$router.push(
        this.localePath(`/projects/${this.$route.params.id}/reporting/${item.route}`)
      )
    },
  }
})
</script>

<style scoped>
.v-data-table >>> tbody tr:hover {
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.04);
}

.v-data-table >>> a {
  text-decoration: none;
  color: inherit;
}

.v-data-table >>> a:hover {
  text-decoration: underline;
}
</style>