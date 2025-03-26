<template>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>
                Annotation Conflicts: {{ member1Name }} vs {{ member2Name }}
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-chip color="secondary">
                {{ conflictCount }} conflicts found
              </v-chip>
            </v-toolbar>
            
            <v-card-text>
              <v-alert v-if="error" type="error">
                {{ error }}
              </v-alert>
  
              <v-progress-linear v-if="loading" indeterminate></v-progress-linear>
  
              <template v-if="!loading && !error">
                <v-tabs v-model="tab" show-arrows>
                  <v-tab v-for="(conflict, index) in conflicts" :key="index">
                    Example #{{ conflict.example.id }}
                    <v-chip v-if="conflict.differences.length"
                     x-small color="red" text-color="white" class="ml-1">
                      {{ conflict.differences.length }}
                    </v-chip>
                  </v-tab>
                </v-tabs>
  
                <v-tabs-items v-model="tab">
                  <v-tab-item v-for="(conflict, index) in conflicts" :key="index">
                    <v-card flat>
                      <v-card-text>
                        <h3 class="mb-4">Original Text:</h3>
                        <p class="text-body-1">{{ conflict.example.text }}</p>
                        
                        <v-row class="mt-6">
                          <v-col cols="12" md="6">
                            <h3 class="mb-4">
                              {{ member1Name }}'s Annotations
                              <v-chip small color="primary" class="ml-2">
                                {{ conflict.member1.annotations.length }} labels
                              </v-chip>
                            </h3>
                            <annotation-diff 
                              :original="conflict.example.text"
                              :annotations="conflict.member1.annotations"
                              :differences="conflict.differences"
                              user-type="member1"
                            />
                          </v-col>
                          <v-col cols="12" md="6">
                            <h3 class="mb-4">
                              {{ member2Name }}'s Annotations
                              <v-chip small color="primary" class="ml-2">
                                {{ conflict.member2.annotations.length }} labels
                              </v-chip>
                            </h3>
                            <annotation-diff 
                              :original="conflict.example.text"
                              :annotations="conflict.member2.annotations"
                              :differences="conflict.differences"
                              user-type="member2"
                            />
                          </v-col>
                        </v-row>
  
                        <v-alert v-if="conflict.differences.length" type="info" class="mt-4">
                          <h4>Differences Found:</h4>
                          <ul>
                            <li v-for="(diff, diffIndex) in conflict.differences" :key="diffIndex">
                              {{ diff.details }}
                            </li>
                          </ul>
                        </v-alert>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>
                </v-tabs-items>
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
  
  export default Vue.extend({
    components: {
      AnnotationDiff
    },

    layout: 'project',
    middleware: ['check-auth', 'auth', 'setCurrentProject'],
  
    data() {
      return {
        tab: null,
        conflicts: [] as any[],
        member1Name: '',
        member2Name: '',
        conflictCount: 0,
        loading: false,
        error: null as string | null
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
          )


          if (response.conflicts.length === 0) {
            console.warn('No conflicts found')
            this.error = 'No annotation differences found between these users'
        }
          
          this.conflicts = response.conflicts
          this.member1Name = response.member1.username
          this.member2Name = response.member2.username
          this.conflictCount = response.conflict_count
        } else {
            this.error = 'Please select two members to compare'
            }
        } catch (error: any) {
            this.error = error.message || 'Failed to load comparison data'
        } finally {
            this.loading = false
        }
        }
  })
  </script>