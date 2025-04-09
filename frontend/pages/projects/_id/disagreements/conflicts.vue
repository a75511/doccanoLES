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
                />
              </v-col>
              
              <v-col cols="12" md="4" class="px-md-2">
                <v-select
                  v-model="filterOption"
                  :items="filterOptions"
                  label="Filter by"
                  outlined
                  dense
                  hide-details
                />
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="sortOrder"
                  :items="sortOptions"
                  label="Sort by"
                  outlined
                  dense
                  hide-details
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-text>
            <v-alert v-if="error" type="error">
              {{ error }}
            </v-alert>

            <v-progress-linear v-if="loading" indeterminate/>

            <template v-if="!loading && !error">
              <v-row>
                <v-col cols="12">
                  <v-data-table
                    :headers="dynamicHeaders"
                    :items="processedExamples"
                    :search="searchText"
                    :items-per-page="10"
                    class="elevation-1"
                    @click:row="selectExample"
                  >
                    <template #[`item.id`]="{ item }">
                      <v-chip small>
                        #{{ item.id }}
                      </v-chip>
                    </template>

                    <template #[`item.text`]="{ item }">
                      <div class="text-truncate" style="max-width: 300px">
                        {{ item.text }}
                      </div>
                    </template>

                    <template #[`item.member1_annotations`]="{ item }">
                      <div v-if="getComparison(item.id)">
                        <v-chip
                          v-for="(annotation, idx) in getComparison(item.id)?.member1.annotations"
                          :key="idx"
                          small
                          :color="getLabelColor(annotation, item.id, 'member1')"
                          class="mr-1 mb-1"
                        >
                          {{ annotation.label }}
                        </v-chip>
                      </div>
                    </template>

                    <template #[`item.member2_annotations`]="{ item }">
                      <div v-if="getComparison(item.id)">
                        <v-chip
                          v-for="(annotation, idx) in getComparison(item.id)?.member2.annotations"
                          :key="idx"
                          small
                          :color="getLabelColor(annotation, item.id, 'member2')"
                          class="mr-1 mb-1"
                        >
                          {{ annotation.label }}
                        </v-chip>
                      </div>
                    </template>

                    <template #[`item.conflict_status`]="{ item }">
                      <v-chip
                        small
                        :color="hasConflict(item.id) ? 'error' : 'success'"
                        dark
                      >
                        {{ hasConflict(item.id) ? 'Conflict' : 'Agreement' }}
                      </v-chip>
                    </template>
                  </v-data-table>
                </v-col>
              </v-row>

              <v-row v-if="selectedExample" class="mt-4">
                <v-col cols="12">
                  <v-card outlined>
                    <v-card-title class="subtitle-1">
                      Detailed View for Example #{{ selectedExample.id }}
                    </v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <h3 class="mb-2">
                            {{ member1Name }}'s Annotations
                            <v-chip small color="primary" class="ml-2">
                              {{ selectedAnnotations.member1.annotations.length }} labels
                            </v-chip>
                          </h3>
                          <v-card outlined>
                            <v-card-text>
                              <div class="text-content">
                                {{ selectedExample.text }}
                              </div>
                              <div class="mt-3">
                                <v-chip
                                  v-for="(annotation, idx) 
                                  in selectedAnnotations.member1.annotations"
                                  :key="`m1-${idx}`"
                                  small
                                  :color="getLabelColor(annotation, selectedExample.id, 'member1')"
                                  class="mr-1 mb-1"
                                >
                                  {{ annotation.label }}
                                </v-chip>
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="12" md="6">
                          <h3 class="mb-2">
                            {{ member2Name }}'s Annotations
                            <v-chip small color="primary" class="ml-2">
                              {{ selectedAnnotations.member2.annotations.length }} labels
                            </v-chip>
                          </h3>
                          <v-card outlined>
                            <v-card-text>
                              <div class="text-content">
                                {{ selectedExample.text }}
                              </div>
                              <div class="mt-3">
                                <v-chip
                                  v-for="(annotation, idx) 
                                  in selectedAnnotations.member2.annotations"
                                  :key="`m2-${idx}`"
                                  small
                                  :color="getLabelColor(annotation, selectedExample.id, 'member2')"
                                  class="mr-1 mb-1"
                                >
                                  {{ annotation.label }}
                                </v-chip>
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>

                      <v-alert 
                        v-if="selectedAnnotations.differences.length" 
                        type="error" 
                        class="mt-4"
                      >
                        <h4>Differences Found:</h4>
                        <ul>
                          <li 
                            v-for="(diff, diffIndex) in selectedAnnotations.differences" 
                            :key="diffIndex"
                          >
                            {{ diff.details }}
                          </li>
                        </ul>
                      </v-alert>
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
      selectedExample: null as ExampleItem | null,
      mdiMagnify,
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
          this.selectedExample = this.processedExamples[0] || null
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
  },

  computed: {
    processedExamples(): ExampleItem[] {
      return this.examples
        .filter(example => {
          const matchesSearch = this.searchText 
            ? example.text.toLowerCase().includes(this.searchText.toLowerCase())
            : true
          
          const hasConflict = this.hasConflict(example.id)
          if (this.filterOption === 'conflict') return matchesSearch && hasConflict
          if (this.filterOption === 'noConflict') return matchesSearch && !hasConflict
          return matchesSearch
        })
        .sort((a, b) => {
          return this.sortOrder === 'asc' ? a.id - b.id : b.id - a.id
        })
    },

    selectedAnnotations(): AnnotationComparison {
      if (!this.selectedExample) {
        return {
          example: new ExampleItem(0, '', {}, null, 0, '', false, '', []),
          member1: { annotations: [] },
          member2: { annotations: [] },
          differences: []
        }
      }
      
      const comparison = this.comparisons.find(c => c.example.id === this.selectedExample?.id)
      return comparison || {
        example: this.selectedExample,
        member1: { annotations: [] },
        member2: { annotations: [] },
        differences: []
      }
    },

    dynamicHeaders(): Array<{ text: string; value: string; width?: string }> {
    return [
      { text: 'ID', value: 'id', width: '100px' },
      { text: 'Text', value: 'text' },
      { 
        text: this.member1Name || 'Member 1', 
        value: 'member1_annotations',
      },
      { 
        text: this.member2Name || 'Member 2', 
        value: 'member2_annotations',
      },
      { text: 'Status', value: 'conflict_status', width: '120px' }
    ]
  }
  },

  methods: {
    selectExample(example: ExampleItem) {
      this.selectedExample = example
    },

    getComparison(exampleId: number): AnnotationComparison | null {
      return this.comparisons.find(c => c.example.id === exampleId) || null
    },

    hasConflict(exampleId: number): boolean {
      return this.comparisons.some(c => c.example.id === exampleId && c.differences.length > 0)
    },

    getLabelColor(
      annotation: any, 
      exampleId: number, 
      userType: 'member1' | 'member2'
    ): string {
      const comparison = this.getComparison(exampleId)
      if (!comparison) return 'primary'
      
      const isDifferent = comparison.differences.some(diff => 
        diff.label === annotation.label && 
        (diff.type.includes(
          userType === 'member1' ? 'missing_in_member2' : 'missing_in_member1'
        ))
      )
      
      if (isDifferent) {
        return userType === 'member1' ? 'error' : 'success'
      }
      return 'primary'
    }
  }
})
</script>

<style scoped>
.text-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.v-data-table >>> tbody tr :hover {
  cursor: pointer;
  background-color: #f5f5f5;
}
</style>