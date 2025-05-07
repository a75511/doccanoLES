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
      <template #[`item.username`]="{ item }">
        <nuxt-link :to="localePath(`/users/${item.id}`)" class="text-decoration-none">
          <span>{{ item.username }}</span>
        </nuxt-link>
      </template>
      <template #[`item.actions`]="{ item }">
        <v-btn
          icon
          small
          @click.stop="editItem(item)"
        >
          <v-icon small>mdi-pencil</v-icon>
        </v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { mdiMagnify } from '@mdi/js'
import Vue from 'vue'
import type { PropType } from 'vue'
import { DataOptions } from 'vuetify/types'
import { UserItem } from '~/domain/models/user/user'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      required: true
    },
    items: {
      type: Array as PropType<UserItem[]>,
      default: () => [],
      required: true
    },
    value: {
      type: Array as PropType<UserItem[]>,
      default: () => [],
      required: true
    },
    total: {
      type: Number,
      default: 0,
      required: true
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
        { text: 'Username', value: 'username', sortable: true },
        { text: 'Email', value: 'email', sortable: true },
        { 
          text: 'Actions', 
          value: 'actions', 
          sortable: false,
          align: 'center',
          width: '120px'
        }
      ]
    },

    sortedItems(): UserItem[] {
      // Apply sorting if sort options are specified
      if (this.options.sortBy?.length) {
        const sortField = this.options.sortBy[0]
        const sortDirection = this.options.sortDesc?.[0] ? -1 : 1
        
        if (sortField === 'username') {
          return [...this.items].sort((a, b) => 
            a.username.localeCompare(b.username) * sortDirection
          )
        } else if (sortField === 'email') {
          return [...this.items].sort((a, b) => 
            a.email.localeCompare(b.email) * sortDirection
          )
        }
      }
      
      // Default sorting (by username ascending)
      return [...this.items].sort((a, b) => 
        a.username.localeCompare(b.username)
      )
    }
  },

  watch: {
    options: {
      handler() {
        this.isSorting = true
        this.updateQuery({
          query: {
            limit: this.options.itemsPerPage.toString(),
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
            q: this.search
          }
        })
        setTimeout(() => {
          this.isSorting = false
        }, 300)
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
    updateQuery(payload: any) {
      const { sortBy, sortDesc } = this.options
      if (sortBy.length === 1 && sortDesc.length === 1) {
        payload.query.sortBy = sortBy[0]
        payload.query.sortDesc = sortDesc[0]
      } else {
        payload.query.sortBy = 'username'
        payload.query.sortDesc = false
      }
      this.$emit('update:query', payload)
    },
    
    editItem(item: UserItem) {
      this.$emit('edit', item)
    }
  }
})
</script>