<template>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-toolbar flat>
          <v-toolbar-title>Label Disagreement Analysis</v-toolbar-title>
          
          <v-spacer></v-spacer>
          
          <!-- Label Filter Dropdown -->
          <v-select
            v-model="labelFilter"
            :items="labelFilterOptions"
            label="Filter by Label"
            clearable
            style="max-width: 200px; margin-right: 20px"
          ></v-select>
          
          <!-- Order By -->
          <v-select
            v-model="orderBy"
            :items="orderOptions"
            label="Order By"
            style="max-width: 150px; margin-right: 20px"
          ></v-select>
          
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
                <v-card-title>Agreement Threshold</v-card-title>
                <v-card-text class="text-h4">
                  {{ Math.round(summary.threshold * 100) }}%
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Disagreements List -->
          <v-card>
            <v-card-title>
              Examples with Label Disagreements
              <v-spacer></v-spacer>
              <v-chip color="warning" outlined>
                No label reached {{ Math.round(summary.threshold * 100) }}% agreement
              </v-chip>
            </v-card-title>
            <v-card-text>
              <template v-if="summary.disagreements.length === 0">
                <v-alert type="success">
🎉 No disagreements found! All examples have at least one label with {{ Math.round(
  summary.threshold * 100) }}% or higher agreement.
                </v-alert>
              </template>
              
              <template v-else>
                <v-expansion-panels>
                  <v-expansion-panel
                    v-for="(disagreement, index) in summary.disagreements"
                    :key="index"
                  >
                    <v-expansion-panel-header>
                      <div>
                        <strong>Example {{ index + 1 }}</strong>
                        <v-chip 
                          small 
                          color="error" 
                          class="ml-2"
                        >
                          Max: {{ disagreement.max_agreement || 'N/A' }}%
                        </v-chip>
                        <br>
                        <span class="text-caption">
                          {{ truncateText(disagreement.example_text) }}
                        </span>
                        <br>
                        <span class="text-caption text--secondary">
                          {{ disagreement.total_annotators }} annotators
                        </span>
                      </div>
                    </v-expansion-panel-header>
                    
                    <v-expansion-panel-content>
                      <v-row>
                        <v-col cols="12">
                          <h4>Label Agreement Percentages:</h4>
                          <v-row>
                            <v-col
                              v-for="labelStat in disagreement.label_percentages"
                              :key="labelStat.label"
                              cols="12"
                              sm="6"
                              md="4"
                            >
                              <v-card outlined>
                                <v-card-text>
                                  <div class="d-flex justify-space-between align-center">
                                    <span class="font-weight-bold">{{ labelStat.label }}</span>
                                    <v-chip
                                      :color="getPercentageColor(labelStat.agreement_percentage)"
                                      dark
                                      small
                                    >
                                      {{ labelStat.agreement_percentage }}%
                                    </v-chip>
                                  </div>
                                  <div class="text-caption mt-1">
{{ labelStat.annotator_count }}/{{ labelStat.total_annotators }} annotators
                                  </div>
                                  <v-progress-linear
                                    :value="labelStat.agreement_percentage"
                                    :color="getPercentageColor(labelStat.agreement_percentage)"
                                    height="6"
                                    class="mt-2"
                                  ></v-progress-linear>
                                </v-card-text>
                              </v-card>
                            </v-col>
                          </v-row>
                        </v-col>
                      </v-row>
                      
                      <v-row v-if="disagreement.example_text">
                        <v-col cols="12">
                          <h4>Full Text:</h4>
                          <p class="text-body-2">{{ disagreement.example_text }}</p>
                        </v-col>
                      </v-row>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </template>
            </v-card-text>
          </v-card>
        </template>
      </v-card-text>
    </v-card>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { DisagreementAnalysisSummary } from '~/domain/models/disagreement/disagreement'
  
  export default Vue.extend({
    layout: 'project',
    data() {
      return {
        isLoading: false,
        error: '',
        summary: null as DisagreementAnalysisSummary | null,
        labelFilter: '',
        orderBy: 'percentage',
        availableLabels: [] as string[],
        orderOptions: [
          { text: 'By Percentage', value: 'percentage' },
          { text: 'By Label Name', value: 'label' }
        ]
      }
    },

    computed: {
      labelFilterOptions() {
        return [
          { text: 'All Labels', value: '' },
          ...this.availableLabels.map(label => ({ text: label, value: label }))
        ]
      }
    },

    mounted() {
      this.analyze()
    },

    methods: {
      async analyze() {
        this.isLoading = true
        this.error = ''
        
        try {
          this.summary = await this.$services.analysis.getDisagreementAnalysis(
            this.$route.params.id,
            this.labelFilter,
            this.orderBy
          )
          
          // Update available labels for dropdown
          if (this.summary && this.summary.available_labels) {
            this.availableLabels = this.summary.available_labels
          }
          
          console.log('Disagreement Analysis Summary:', this.summary)
        } catch (error) {
          this.error = error.message || 'Database Unavailable. Please try again'
          console.error('Analysis error:', error)
        } finally {
          this.isLoading = false
        }
      },

      getPercentageColor(percentage: number): string {
        if (percentage >= 80) return 'green'
        if (percentage >= 60) return 'orange'
        return 'red'
      },

      getDisagreementColor(rate: number): string {
        if (rate <= 10) return 'green'
        if (rate <= 30) return 'orange'
        return 'red'
      },

      truncateText(text: string | null): string {
        if (!text) return 'No text available'
        return text.length > 100 ? text.substring(0, 100) + '...' : text
      }
    }
  })
  </script>