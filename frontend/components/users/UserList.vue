<template>
    <v-data-table
      :value="value"
      :headers="headers"
      :items="items"
      :options.sync="options"
      :server-items-length="total"
      :search="search"
      :loading="isLoading"
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
        <nuxt-link :to="localePath(`/users/${item.id}`)">
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
          })
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
          payload.query.sortDesc = true
        }
        this.$emit('update:query', payload)
      },
      
      editItem(item: UserItem) {
        // Emit an event to parent component to handle editing
        this.$emit('edit', item)
        // Or navigate directly:
        // this.$router.push(`/users/${item.id}/edit`)
      }
    }
  })
  </script>