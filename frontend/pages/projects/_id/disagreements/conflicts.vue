<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>
              Annotation Comparison: {{ member1Name }} vs {{ member2Name }}
            </v-toolbar-title>
            <v-spacer></v-spacer>
            <v-chip color="secondary">
              {{ conflictCount }} conflicts ({{ processedExamples.length }} shown)
            </v-chip>
          </v-toolbar>
          <v-card-text class="py-2 px-4 grey lighten-4">
            <v-row align="center" no-gutters>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchText"
                  :prepend-inner-icon="mdiMagnify"
                  label="Search annotations"
                  single-line
                  hide-details
                  outlined
                  dense
                  clearable
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4" class="px-md-2">
                <v-select
                  v-model="filterOption"
                  :items="filterOptions"
                  label="Filter by"
                  outlined
                  dense
                  hide-details
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="sortOrder"
                  :items="sortOptions"
                  label="Sort by"
                  outlined
                  dense
                  hide-details
                ></v-select>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-text>
            <v-alert v-if="error" type="error">
              {{ error }}
            </v-alert>

            <v-progress-linear v-if="loading" indeterminate></v-progress-linear>

            <template v-if="!loading && !error">
              <v-row>
                <v-col cols="12" md="3" class="pr-0">
                  <v-card outlined>
                    <v-card-text class="pa-0">
                      <div :style="{ maxHeight:
                         $vuetify.breakpoint.mobile ? '30vh' : '30vh', overflowY: 'auto' }">
                        <v-list dense>
                          <v-list-item-group v-model="selectedExampleId" color="primary">
                            <v-list-item
                              v-for="example in processedExamples"
                              :key="example.id"
                              :value="example.id"
                              :class="{
                                'highlight-conflict': hasConflict(example.id),
                                'mb-1': true
                              }"
                            >
                              <v-list-item-content>
                                <v-list-item-title>
                                  #{{ example.id }}
                                  <v-chip
                                    v-if="hasConflict(example.id)"
                                    x-small
                                    color="error"
                                    class="ml-1"
                                  >
                                    Conflict
                                  </v-chip>
                                </v-list-item-title>
                                <v-list-item-subtitle class="text-truncate">
                                  {{ truncateText(example.text, 50) }}
                                </v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                          </v-list-item-group>
                        </v-list>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>

                <v-col cols="12" md="9" class="pl-0">
                  <v-card v-if="currentExample" outlined>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <h3 class="mb-4">
                            {{ member1Name }}'s Annotations
                            <v-chip small color="primary" class="ml-2">
                              {{ currentAnnotations.member1.annotations.length }} labels
                            </v-chip>
                          </h3>
                          <annotation-diff 
                            :original="currentExample.text"
                            :annotations="currentAnnotations.member1.annotations"
                            :differences="currentAnnotations.differences"
                            user-type="member1"
                          />
                        </v-col>
                        <v-col cols="12" md="6">
                          <h3 class="mb-4">
                            {{ member2Name }}'s Annotations
                            <v-chip small color="primary" class="ml-2">
                              {{ currentAnnotations.member2.annotations.length }} labels
                            </v-chip>
                          </h3>
                          <annotation-diff 
                            :original="currentExample.text"
                            :annotations="currentAnnotations.member2.annotations"
                            :differences="currentAnnotations.differences"
                            user-type="member2"
                          />
                        </v-col>
                      </v-row>

                      <v-alert 
                        v-if="currentAnnotations.differences.length" 
                        type="error" 
                        class="mt-4"
                      >
                        <h4>Differences Found:</h4>
                        <ul>
                          <li v-for="(diff, diffIndex) in currentAnnotations.differences" 
                          :key="diffIndex">
                            {{ diff.details }}
                          </li>
                        </ul>
                      </v-alert>
                    </v-card-text>
                  </v-card>
                  <v-card v-else outlined>
                    <v-card-text class="text-center grey--text">
                      Select an example to view annotations
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMagnify } from '@mdi/js'
import AnnotationDiff from '~/components/example/AnnotationDiff.vue'
import { AnnotationComparison, ComparisonResponse } from '~/domain/models/disagreement/disagreement'
import { ExampleItem } from '~/domain/models/example/example'

type FilterOption = 'all' | 'conflict' | 'noConflict'
type SortOrder = 'asc' | 'desc'

interface FilterOptionItem {
  text: string
  value: FilterOption
}

interface SortOptionItem {
  text: string
  value: SortOrder
}

export default Vue.extend({
  components: {
    AnnotationDiff
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  
  data() {
    return {
      examples: [] as ExampleItem[],
      comparisons: [] as AnnotationComparison[],
      member1Name: '',
      member2Name: '',
      conflictCount: 0,
      loading: false,
      error: null as string | null,
      searchText: '',
      filterOption: 'all' as FilterOption,
      sortOrder: 'asc' as SortOrder,
      filterOptions: [
        { text: 'All Annotations', value: 'all' },
        { text: 'With Conflicts Only', value: 'conflict' },
        { text: 'Without Conflicts', value: 'noConflict' }
      ] as FilterOptionItem[],
      sortOptions: [
        { text: 'ID (Ascending)', value: 'asc' },
        { text: 'ID (Descending)', value: 'desc' }
      ] as SortOptionItem[],
      selectedExampleId: null as number | null,
      mdiMagnify
    }
  },

  computed: {
    processedExamples(): ExampleItem[] {
      return this.examples
        .filter(example => {
          // Search filter
          const matchesSearch = this.searchText 
            ? example.text.toLowerCase().includes(this.searchText.toLowerCase())
            : true
          
          // Conflict filter
          const hasConflict = this.hasConflict(example.id)
          if (this.filterOption === 'conflict') return matchesSearch && hasConflict
          if (this.filterOption === 'noConflict') return matchesSearch && !hasConflict
          return matchesSearch
        })
        .sort((a, b) => {
          // ID sorting
          return this.sortOrder === 'asc' ? a.id - b.id : b.id - a.id
        })
    },

    currentExample(): ExampleItem | null {
      return this.processedExamples.find(e => e.id === this.selectedExampleId) || null
    },

    currentAnnotations(): AnnotationComparison {
      const exampleId = this.currentExample?.id
      const comparison = this.comparisons.find(c => c.example.id === exampleId)
      
      return comparison || {
        example: this.currentExample || new ExampleItem(
          0, '', {}, null, 0, '', false, '', []
        ),
        member1: { annotations: [] },
        member2: { annotations: [] },
        differences: []
      }
    }
  },

  watch: {
    processedExamples(newVal) {
      if (newVal.length === 0) {
        this.selectedExampleId = null
        return
      }
      if (!newVal.some((e: { id: number | null }) => e.id === this.selectedExampleId)) {
        this.selectedExampleId = newVal[0]?.id || null
      }
    }
  },

  methods: {
    hasConflict(exampleId: number): boolean {
      return this.comparisons.some(c => c.example.id === exampleId && c.differences.length > 0)
    },

    truncateText(text: string, length: number): string {
      return text.length > length ? text.substring(0, length) + '...' : text
    }
  },

  async fetch() {
    this.loading = true
    this.error = null
    
    try {
      const member1Id = this.$route.query.member1
      const member2Id = this.$route.query.member2
      const projectId = this.$route.params.id

      if (member1Id && member2Id) {
        const response = await this.$services.disagreement.compare(
          projectId,
          Number(member1Id),
          Number(member2Id),
          this.searchText
        ) as ComparisonResponse;

        if (response.examples.length === 0) {
          this.error = 'No common annotations found between these members'
          this.examples = []
          this.comparisons = []
          this.conflictCount = 0
          return
        }

        this.member1Name = response.member1.username;
        this.member2Name = response.member2.username;
        this.conflictCount = response.conflict_count;

        this.comparisons = response.conflicts;
        this.examples = response.examples || [];
        
        if (this.examples.length > 0) {
          this.selectedExampleId = this.processedExamples[0]?.id || null
        }
      } else {
        this.error = 'Please select two members to compare'
      }
    } catch (error: any) {
      if (error.response?.data?.error) {
        this.error = error.response.data.error
      } else if (error.response?.data?.detail) {
        this.error = error.response.data.detail
      } else if (error instanceof Error) {
        this.error = error.message
      } else {
        this.error = 'Failed to load comparison data'
      }
    } finally {
      this.loading = false
    }
  }
})
</script>

<style scoped>
.highlight-conflict {
  border-left: 4px solid #ff5252;
  background-color: rgba(255, 82, 82, 0.1);
}

.v-list-item--active {
  background-color: #e3f2fd;
}

/* Improved controls styling */
.v-card__text.controls {
  border-bottom: 1px solid #e0e0e0;
}

/* Better spacing for mobile */
@media (max-width: 959px) {
  .v-col {
    padding-top: 6px;
    padding-bottom: 6px;
  }
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
}
::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>