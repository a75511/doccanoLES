<template>
    <v-container>
      <v-card>
        <v-card-title class="d-flex align-center">
          <div>
            Attributes of Perspective <strong>{{ perspectiveName }}</strong>
          </div>
          <v-spacer></v-spacer>
        </v-card-title>
        <v-text-field
            v-model="search"
            :prepend-inner-icon="mdiMagnify"
            :label="$t('generic.search')"
            single-line
            hide-details
            filled
            class="search-field"
          />
        <v-data-table
          :headers="headers"
          :items="filteredAttributes"
          :search="search"
          :options.sync="options"
          :loading="isLoading"
          loading-text="Loading... Please wait"
          :footer-props="{
            showFirstLastPage: true,
            'items-per-page-options': [10, 50, 100],
            'items-per-page-text': $t('vuetify.itemsPerPageText'),
            'page-text': $t('dataset.pageText')
          }"
        >
          <template #[`item.name`]="{ item }">
            {{ item.name }}
          </template>
          <template #[`item.type`]="{ item }">
            {{ item.type }}
          </template>
          <template #[`item.options`]="{ item }">
            <v-chip v-for="(option, index) in item.listOptions" :key="index" class="mr-2" small>
              {{ option.value }}
            </v-chip>
          </template>
        </v-data-table>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue';
  import { Context } from '@nuxt/types'
  import { mdiMagnify } from '@mdi/js';
  
  export default Vue.extend({
    layout: 'project',
    
    async asyncData({ params, app }: Context) {
      try {
        const perspective = await app.$services.perspective.findById(
          params.id,
          parseInt(params.perspective_id)
        );
  
        console.log('Perspective:', perspective);
        
        const response = await app.$services.perspective.listAttributes(
          params.id,
          parseInt(params.perspective_id),
          {
            limit: '10',
            offset: '0',
            q: '',
            sortBy: 'name',
            sortDesc: 'false'
          });
  
        return { 
          attributes: response.items,
          isLoading: false,
          error: null,
          total: response.count,
          perspectiveName: perspective.name
        };
      } catch (error: any) {
        return {
          attributes: [],
          isLoading: false,
          error: error.message || 'Failed to load attributes',
          total: 0,
          perspectiveName: 'Unknown'
        };
      }
    },
  
    data() {
      return {
        search: '',
        options: {
          page: 1,
          itemsPerPage: 10,
          sortBy: ['name'],
          sortDesc: [false]
        },
        isLoading: true,
        attributes: [],
        error: null,
        total: 0,
        perspectiveName: '',
        headers: [
          { text: 'Name', value: 'name', sortable: true },
          { text: 'Type', value: 'type', sortable: true },
          { text: 'Options', value: 'options', sortable: false },
        ],
        mdiMagnify,
      };
    },
  
    computed: {
      filteredAttributes(): any[] {
        let attributes = [...this.attributes];
        
        if (this.search) {
          const searchTerm = this.search.toLowerCase();
          attributes = attributes.filter(attr => 
            attr.name.toLowerCase().includes(searchTerm));
        }
  
        if (this.options.sortBy.length) {
          const sortKey = this.options.sortBy[0];
          const sortOrder = this.options.sortDesc[0] ? -1 : 1;
          
          attributes.sort((a, b) => {
            if (a[sortKey] < b[sortKey]) return -1 * sortOrder;
            if (a[sortKey] > b[sortKey]) return 1 * sortOrder;
            return 0;
          });
        }
        
        return attributes;
      }
    },
  
    watch: {
      options: {
        async handler() {
          this.isLoading = true;
          try {
            const response = await this.$services.perspective.listAttributes(
              this.$route.params.id,
              parseInt(this.$route.params.perspective_id),
              {
                limit: this.options.itemsPerPage.toString(),
                offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
                q: this.search,
                sortBy: this.options.sortBy[0],
                sortDesc: this.options.sortDesc[0].toString()
              }
            );
            this.attributes = response.items;
            this.total = response.count;
          } catch (error) {
            console.error('Error fetching attributes:', error);
          }
          this.isLoading = false;
        },
        deep: true
      }
    }
  });
  </script>
  
  <style scoped>

  
  .v-card-title {
    align-items: center;
    padding: 16px;
  }
  </style>