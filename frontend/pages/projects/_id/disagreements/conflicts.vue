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
              {{ conflictCount }} conflicts found ({{ examples.length }} total)
            </v-chip>
          </v-toolbar>
          
          <v-card-text>
            <v-alert v-if="error" type="error">
              {{ error }}
            </v-alert>

            <v-progress-linear v-if="loading" indeterminate></v-progress-linear>

            <template v-if="!loading && !error">
              <v-row>
                <v-col cols="12" md="3" class="pr-0">
                  <v-card outlined>
                    <v-card-title class="subtitle-1">
                      Examples List
                    </v-card-title>
                    <v-card-text class="pa-0">
                      <v-list dense>
                        <v-list-item-group v-model="selectedExampleIndex" color="primary">
                          <v-list-item
                            v-for="(example) in examples"
                            :key="example.id"
                            :class="{
                              'highlight-conflict': hasConflict(example.id),
                              'mb-1': true
                            }"
                          >
                            <v-list-item-content>
                              <v-list-item-title>
                                Example #{{ example.id }}
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
import AnnotationDiff from '~/components/example/AnnotationDiff.vue'
import { AnnotationComparison, ComparisonResponse } from '~/domain/models/disagreement/disagreement'
import { ExampleItem } from '~/domain/models/example/example'

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
      selectedExampleIndex: 0,
      member1Name: '',
      member2Name: '',
      conflictCount: 0,
      loading: false,
      error: null as string | null
    }
  },

  computed: {
    currentExample(): ExampleItem | null {
      return this.examples[this.selectedExampleIndex] || null
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
          Number(member2Id)
        ) as ComparisonResponse;

        this.member1Name = response.member1.username;
        this.member2Name = response.member2.username;
        this.conflictCount = response.conflict_count;

        this.comparisons = response.conflicts;
        this.examples = response.examples || [];
        
        if (this.examples.length === 0) {
          this.error = 'No examples found for comparison'
        }
      } else {
        this.error = 'Please select two members to compare'
      }
    } catch (error: any) {
      this.error = error.message || 'Failed to load comparison data'
    } finally {
      this.loading = false
    }
  },

  methods: {
    hasConflict(exampleId: number): boolean {
      return this.comparisons.some(c => c.example.id === exampleId && c.differences.length > 0)
    },

    truncateText(text: string, length: number): string {
      return text.length > length ? text.substring(0, length) + '...' : text
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
</style>