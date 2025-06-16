<template>
    <v-container>
      <v-card>
        <v-card-title class="d-flex align-center">
          <div>
            Attributes of Perspective <strong>{{ perspectiveName }}</strong>
          </div>
          <v-spacer></v-spacer>
        </v-card-title>
        <v-alert v-if="errorMessage" type="error" class="mt-4">
          {{ errorMessage }}
        </v-alert>
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
          errorMessage: '',
          total: response.count,
          perspectiveName: perspective.name
        };
      } catch (error: any) {
        return {
          attributes: [],
          isLoading: false,
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
          sortDesc: [false],
          multiSort: false,
          mustSort: true
        },
        isLoading: true,
        attributes: [],
        errorMessage: '',
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
  
        if (this.options.sortBy && this.options.sortBy.length) {
          const sortKey = this.options.sortBy[0];
          const sortOrder =
           (this.options.sortDesc && this.options.sortDesc.length
            > 0 && this.options.sortDesc[0]) ? -1 : 1;
          
          attributes.sort((a, b) => {
            const valA = String(a[sortKey] || '').toLowerCase();
            const valB = String(b[sortKey] || '').toLowerCase();
            
            return valA.localeCompare(valB) * sortOrder;
          });
        }
        
        return attributes;
      }
    },

    watch: {
      '$route.query': {
        handler() {
          this.options = {
            ...this.options,
            page: parseInt(this.$route.query.page as string) || 1,
            itemsPerPage: parseInt(this.$route.query.limit as string) || 10,
            sortBy: this.$route.query.sortBy ? [this.$route.query.sortBy as string] : ['name'],
            sortDesc: this.$route.query.sortDesc ? [this.$route.query.sortDesc === 'true'] : [false]
          };
        },
        immediate: true
      },
  
      options: {
        async handler() {
          this.isLoading = true;
          try {
            this.errorMessage = '';
            
            const sortBy = (this.options.sortBy && this.options.sortBy.length > 0) 
              ? this.options.sortBy[0] 
              : 'name';
            
            const sortDesc = (this.options.sortDesc && this.options.sortDesc.length > 0) 
              ? this.options.sortDesc[0] 
              : false;
            
            const response = await this.$services.perspective.listAttributes(
              this.$route.params.id,
              parseInt(this.$route.params.perspective_id),
              {
                limit: this.options.itemsPerPage.toString(),
                offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
                q: this.search,
                sortBy,
                sortDesc: sortDesc.toString()
              }
            );
            this.attributes = response.items;
            this.total = response.count;

            const query: Record<string, string> = {
              page: this.options.page.toString(),
              limit: this.options.itemsPerPage.toString(),
              sortBy,
              sortDesc: sortDesc.toString()
            };

            if (this.search) {
              query.q = this.search;
            }

            const currentQuery = this.$route.query;
            const queryChanged = Object.keys(query).some(key => 
              currentQuery[key] !== query[key]
            ) || Object.keys(currentQuery).some(key => 
              !query[key] && currentQuery[key]
            );

            if (queryChanged) {
              await this.$router.replace({ 
                path: this.$route.path, 
                query 
              });
            }

          } catch (error: any) {
            if (error.response?.data?.error) {
                this.errorMessage = error.response.data.error
              } else if (error.response?.data?.detail) {
                this.errorMessage = error.response.data.detail
              } else if (error instanceof Error) {
                this.errorMessage = error.message
              } else {
                this.errorMessage = 'Failed to fetch attributes. Please try again.'
            }
          }
          this.isLoading = false;
        },
        deep: true
      },

      search: {
        handler() {
          if (this.options.page !== 1) {
            this.options = {
              ...this.options,
              page: 1
            };
          }
        }
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