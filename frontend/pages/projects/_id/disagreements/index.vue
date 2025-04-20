<template>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-toolbar flat>
          <v-toolbar-title>Disagreement Analysis</v-toolbar-title>
          
          <v-spacer></v-spacer>
          
          <v-slider
            v-model="threshold"
            :min="0"
            :max="100"
            :step="5"
            label="Threshold (%)"
            style="max-width: 300px; margin-right: 20px"
            thumb-label
          ></v-slider>
          
          <v-btn
            color="primary"
            :loading="isLoading"
            @click="analyze"
          >
            Analyze
          </v-btn>
        </v-toolbar>
      </v-card-title>
  
      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          class="mb-4"
        >
          {{ error }}
        </v-alert>
  
        <template v-if="summary">
          <!-- Summary Stats -->
          <v-row class="mb-6">
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Total Examples</v-card-title>
                <v-card-text class="text-h4">
                  {{ summary.total_examples_analyzed }}
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>With Disagreements</v-card-title>
                <v-card-text class="text-h4">
                  {{ summary.examples_with_disagreements }}
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Disagreement Rate</v-card-title>
                <v-card-text class="text-h4">
                  {{ summary.threshold*100 }}%
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
  
          <!-- Disagreements Table -->
          <v-data-table
            :headers="headers"
            :items="summary.disagreements"
            :loading="isLoading"
            class="elevation-1"
          >
            <template #[`item.disagreement_percentage`]="{ item }">
              <v-chip :color="getColor(item.disagreement_percentage)">
                {{ item.disagreement_percentage.toFixed(1) }}%
              </v-chip>
            </template>
            
            <template #[`item.actions`]="{ item }">
              <v-btn
                small
                color="primary"
                @click="showDetails(item)"
              >
                Details
              </v-btn>
            </template>
          </v-data-table>
        </template>
        
        <v-dialog v-model="detailDialog" max-width="800">
          <disagreement-details
            v-if="selectedExample"
            :example="selectedExample"
            @close="detailDialog = false"
          />
        </v-dialog>
      </v-card-text>
    </v-card>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { DisagreementAnalysisSummary, ExampleDisagreement } from '~/domain/models/disagreement/disagreement'
  
  
  export default Vue.extend({
  
    layout: 'project',
    data() {
      return {
        threshold: 40,
        isLoading: false,
        error: '',
        summary: null as DisagreementAnalysisSummary | null,
        detailDialog: false,
        selectedExample: null as any,
        headers: [
          { text: 'Example ID', value: 'example_id' },
          { text: 'Text Preview', value: 'example_text', sortable: false },
          { text: 'Annotators', value: 'total_annotators' },
          { text: 'Disagreement %', value: 'disagreement_percentage' },
          { text: 'Actions', value: 'actions', sortable: false }
        ]
      }
    },

    methods: {
      async analyze() {
        this.isLoading = true
        this.error = ''
        
        try {
          this.summary = await this.$services.analysis.getDisagreementAnalysis(
            this.$route.params.id,
            this.threshold / 100
          )
          console.log('Disagreement Analysis Summary:', this.summary)
        } catch (error) {
          this.error = error.message || 'Database Unavailable. Please try again'
          console.error('Analysis error:', error)
        } finally {
          this.isLoading = false
        }
      },
  
      showDetails(item: any) {
        this.selectedExample = item
        this.detailDialog = true
      },
  
      getColor(percentage: number): string {
      if (percentage > 70) return 'red'
      if (percentage > 40) return 'orange'
      return 'green'
    },
    
    // Add this method to get controversial examples
    getControversialExamples(): ExampleDisagreement[] {
      return this.summary ? this.summary.getMostControversialExamples() : []
    },
  
      truncateText(text: string | null): string {
        if (!text) return ''
        return text.length > 50 ? text.substring(0, 50) + '...' : text
      }
    }
  })
  </script>