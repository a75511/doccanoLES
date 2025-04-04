<template>
  <div>
    <v-data-table
      :value="value"
      :headers="headers"
      :items="sortedItems"
      :options.sync="options"
      :server-items-length="total"
      :search="search"
      :loading="isLoading || isSorting"
      :loading-text="$t('generic.loading')"
      :no-data-text="$t('vuetify.noDataAvailable')"
      :footer-props="{
        showFirstLastPage: true,
        'items-per-page-options': [10, 50, 100],
        'items-per-page-text': $t('vuetify.itemsPerPageText'),
        'page-text': $t('dataset.pageText')
      }"
      item-key="id"
      show-select
      @input="$emit('input', $event)"
    >
      <template #top>
        <v-text-field
          v-model="search"
          :prepend-inner-icon="mdiMagnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
        />
      </template>
      <template #[`item.name`]="{ item }">
        <nuxt-link :to="perspectiveDetailLink(item.id)" class="text-decoration-none">
          <span>
            {{ item.name }}
            <v-chip v-if="item.isAssigned" small color="primary" class="ml-2">
              Assigned
            </v-chip>
          </span>
        </nuxt-link>
      </template>
      <template #[`item.description`]="{ item }">
        <span>{{ item.description }}</span>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { mdiMagnify } from '@mdi/js'
import type { PropType } from 'vue'
import Vue from 'vue'
import { DataOptions } from 'vuetify/types'
import { PerspectiveItem } from '~/domain/models/perspective/perspective'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<PerspectiveItem[]>,
      default: () => [],
      required: true
    },
    value: {
      type: Array as PropType<PerspectiveItem[]>,
      default: () => [],
      required: true
    },
    total: {
      type: Number,
      default: 0,
      required: true
    },
    currentProject: {
      type: Object as PropType<{ perspective: PerspectiveItem | null }>,
      default: () => ({ perspective: null })
    }
  },

  data() {
    return {
      search: this.$route.query.q,
      options: {} as DataOptions,
      mdiMagnify,
      isSorting: false
    }
  },

  computed: {
    headers() {
      return [
        { text: this.$t('generic.name'), value: 'name', sortable: true },
        { text: this.$t('generic.description'), value: 'description', sortable: false },
        { text: this.$t('generic.actions'), value: 'actions', sortable: false }
      ]
    },

    sortedItems(): PerspectiveItem[] {
      const assignedPerspectiveId = this.currentProject?.perspective?.id || null
      
      // Mark assigned items and create a single sorted array
      return this.items
        .map(item => ({
          ...item,
          isAssigned: item.id === assignedPerspectiveId
        }))
        .sort((a, b) => {
          // Always keep assigned item at the top
          if (a.isAssigned) return -1
          if (b.isAssigned) return 1
          
          // Apply sorting only if sort options are specified
          if (this.options.sortBy?.length) {
            const sortField = this.options.sortBy[0]
            const sortDirection = this.options.sortDesc?.[0] ? -1 : 1
            
            if (sortField === 'name') {
              return a.name.localeCompare(b.name) * sortDirection
            } else if (sortField === 'createdAt') {
              const dateA = new Date(a.createdAt).getTime()
              const dateB = new Date(b.createdAt).getTime()
              return (dateA - dateB) * sortDirection
            }
          }
          
          return 0
        })
    }
  },

  watch: {
    options: {
      handler() {
        this.updateQuery({
          query: {
            limit: this.options.itemsPerPage.toString(),
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
            q: this.search
          }
        });
      },
      deep: true
    },
    search() {
      this.updateQuery({
        query: {
          limit: this.options.itemsPerPage.toString(),
          offset: '0',
          q: this.search
        }
      })
      this.options.page = 1
    }
  },

  methods: {
    perspectiveDetailLink(id: number): string {
      return `/projects/${this.$route.params.id}/perspectives/${id}`;
    },

    updateQuery(payload: any) {
      const { sortBy, sortDesc } = this.options
      if (sortBy.length === 1 && sortDesc.length === 1) {
        payload.query.sortBy = sortBy[0]
        payload.query.sortDesc = sortDesc[0]
      } else {
        payload.query.sortBy = 'createdAt'
        payload.query.sortDesc = true
      }
      this.$emit('update:query', payload)
    }
  }
})
</script>