<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Disagreement Report</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>

      <v-card-text class="grey lighten-4 py-2">
        <v-row align="center" no-gutters>
          <v-col cols="12" md="3">
            <perspective-filter 
              v-model="selectedAttributes" 
              :project-id="$route.params.id" 
            />
          </v-col>
          <v-col cols="12" md="3" class="pl-md-2">
            <description-filter 
              v-model="selectedDescriptions"
              :project-id="$route.params.id"
              :selected-attributes="selectedAttributes"
            />
          </v-col>
          <v-col cols="12" md="3" class="pl-md-2">
            <view-type-filter 
              v-model="viewType"
            />
          </v-col>
          <v-col cols="12" md="3" class="pl-md-2">
            <export-filter v-model="selectedFormats" />
          </v-col>
        </v-row>
        
        <v-row class="mt-2">
          <v-col cols="12" md="3">
            <v-btn 
              color="primary" 
              :loading="loading"
              @click="applyFilters"
            >
              <v-icon left>{{ icons.refresh }}</v-icon>
              Apply Filters
            </v-btn>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn color="secondary" @click="resetFilters">
              <v-icon left>{{ icons.close }}</v-icon>
              Reset
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-text>
        <v-alert v-if="error" type="error">
          {{ error }}
        </v-alert>

        <v-progress-linear 
          v-if="loading" 
          indeterminate 
          color="primary"
        ></v-progress-linear>

        <!-- No data message when filters not selected or no results -->
        <v-alert
          v-if="!loading && showNoDataMessage"
          type="info"
          class="ma-4"
        >
          {{ noDataMessage }}
        </v-alert>

        <template v-if="shouldShowResults">
          <!-- Overall Statistics Section - Now filtered data only -->
          <v-card class="mb-6" outlined>
            <v-card-title class="primary--text">
              <v-icon left color="primary">{{ icons.chartBar }}</v-icon>
              Filtered Results Summary
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <v-card color="blue lighten-5" outlined>
                    <v-card-text class="text-center">
                      <div class="text-h4 blue--text">{{ filteredTotalExamples }}</div>
                      <div class="text-subtitle-1">Total Examples (Filtered)</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card color="red lighten-5" outlined>
                    <v-card-text class="text-center">
                      <div class="text-h4 red--text">{{ filteredDisagreements }}</div>
                      <div class="text-subtitle-1">Disagreements</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card color="green lighten-5" outlined>
                    <v-card-text class="text-center">
                      <div class="text-h4 green--text">{{ filteredAgreements }}</div>
                      <div class="text-subtitle-1">Agreements</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Label Distributions Section -->
          <div v-for="dist in labelDistributions" :key="getDistributionKey(dist)">
            <v-card class="mb-6" outlined>
              <v-card-title class="primary--text">
                <v-icon left color="primary">{{ icons.accountGroup }}</v-icon>
                Group: {{ formatGroupTitle(dist) }}
              </v-card-title>
              
              <v-card-subtitle>
                Total Members in Group: {{ dist.total_members }}
              </v-card-subtitle>

              <!-- Examples in this group -->
              <v-card-text>
                <template v-if="dist.examples && dist.examples.length > 0">
                  <v-row>
                    <v-col 
                      v-for="example in dist.examples" 
                      :key="example.example_id"
                      cols="12"
                      class="mb-4"
                    >
                      <v-card outlined elevation="2">
                        <v-card-title class="text-h6">
                          <v-icon left :color="getAgreementColor(example)">
                            {{ getAgreementIcon(example) }}
                          </v-icon>
                          Example #{{ example.example_id }}
                          <v-spacer></v-spacer>
                          <v-chip 
                            :color="getAgreementColor(example)" 
                            dark 
                            small
                          >
                            {{ getAgreementText(example) }}
                          </v-chip>
                        </v-card-title>
                        
                        <v-card-subtitle>
                          <strong>Text:</strong> {{ truncateText(example.example_text, 100) }}
                        </v-card-subtitle>
                        
                        <v-card-text>
                          <v-row>
                            <v-col cols="12" md="8">
                              <v-simple-table dense>
                                <template #default>
                                  <thead>
                                    <tr>
                                      <th class="text-left">Label</th>
                                      <th class="text-left">Count</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr v-for="label in example.labels" :key="label.label">
                                      <td>{{ label.label }}</td>
                                      <td>
                                        <v-chip small color="primary">
                                          {{ label.count }}
                                        </v-chip>
                                      </td>
                                    </tr>
                                  </tbody>
                                </template>
                              </v-simple-table>
                            </v-col>
                            <v-col cols="12" md="4">
                              <v-card color="grey lighten-5" flat>
                                <v-card-text>
                                  <div class="text-center">
                                    <div class="text-h6 primary--text">
                                      {{ example.total }}
                                    </div>
                                    <div class="text-caption">Total Annotators</div>
                                  </div>
                                  <v-divider class="my-2"></v-divider>
                                  <div class="text-center">
                                    <div class="text-h6 orange--text">
                                      {{ example.non_annotated }}
                                    </div>
                                    <div class="text-caption">Not Annotated</div>
                                  </div>
                                </v-card-text>
                              </v-card>
                            </v-col>
                          </v-row>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </template>
                <v-alert v-else type="info" outlined>
                  No examples found for this group with the current filters.
                </v-alert>
              </v-card-text>
            </v-card>
          </div>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { 
  mdiRefresh, 
  mdiClose, 
  mdiChartBar, 
  mdiAccountGroup, 
  mdiCheck, 
  mdiAlert 
} from '@mdi/js'
import ExportFilter from '@/components/reporting/ExportFilter.vue'
import PerspectiveFilter from '@/components/reporting/PerspectiveFilter.vue'
import DescriptionFilter from '@/components/reporting/DescriptionFilter.vue'
import ViewTypeFilter from '@/components/reporting/ViewTypeFilter.vue'

export default {
  components: {
    ExportFilter,
    PerspectiveFilter,
    DescriptionFilter,
    ViewTypeFilter,
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      stats: null,
      selectedAttributes: [],
      selectedDescriptions: [],
      viewType: 'all',
      selectedFormats: ['preview'],
      loading: false,
      error: null,
      showResults: false,
      icons: {
        refresh: mdiRefresh,
        close: mdiClose,
        chartBar: mdiChartBar,
        accountGroup: mdiAccountGroup,
        check: mdiCheck,
        alert: mdiAlert
      }
    }
  },

  computed: {
    labelDistributions() {
      return this.stats?.label_distributions || []
    },

    showNoDataMessage() {
      if (this.loading) return false
      
      // Show message if no filters are selected
      if (!this.selectedAttributes.length) {
        return true
      }
      
      // Show message if filters are selected but no results after applying
      if (this.showResults && (!this.stats || !this.stats.label_distributions.length)) {
        return true
      }
      
      return false
    },

    noDataMessage() {
      if (!this.selectedAttributes.length) {
        return 'Please select at least one perspective attribute to view the disagreement report.'
      }
      
      if (this.showResults && 
      (!this.stats || !this.stats.label_distributions.length) && !this.error) {
        return 'No data available for the selected filters. Try adjusting your filter criteria.'
      }
      
      return 'Click "Apply Filters" to load the disagreement report.'
    },

    shouldShowResults() {
      return !this.loading && 
             this.stats && 
             this.showResults && 
             this.selectedFormats.includes('preview') &&
             this.stats.label_distributions.length > 0
    },

    // Computed properties for filtered statistics
    filteredTotalExamples() {
      if (!this.stats || !this.stats.label_distributions.length) return 0
      
      const uniqueExamples = new Set()
      this.stats.label_distributions.forEach(dist => {
        dist.examples?.forEach(example => {
          uniqueExamples.add(example.example_id)
        })
      })
      
      return uniqueExamples.size
    },

    filteredAgreements() {
      if (!this.stats || !this.stats.label_distributions.length) return 0
      
      let agreements = 0
      this.stats.label_distributions.forEach(dist => {
        dist.examples?.forEach(example => {
          if (example.is_agreement) {
            agreements++
          }
        })
      })
      
      return agreements
    },

    filteredDisagreements() {
      if (!this.stats || !this.stats.label_distributions.length) return 0
      
      let disagreements = 0
      this.stats.label_distributions.forEach(dist => {
        dist.examples?.forEach(example => {
          if (!example.is_agreement) {
            disagreements++
          }
        })
      })
      
      return disagreements
    }
  },

  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        const response = await this.$services.reporting.getDisagreementStatistics(
          this.$route.params.id,
          {
            attributes: this.selectedAttributes,
            descriptions: this.selectedDescriptions,
            view: this.viewType
          }
        )
        this.stats = response
      } catch (e) {
        if (e.response && e.response.status===500) {
          this.error = 'Database Unavailable. Please try again later.'
        } else {
          this.error = e.response?.data?.error || e.message || 'Failed to load data'
          
        }
        this.stats = null
      } finally {
        this.loading = false
      }
    },

    async applyFilters() {
      // Validate that at least attributes are selected
      if (!this.selectedAttributes.length) {
        this.error = 'Please select at least one perspective attribute.'
        return
      }

      this.showResults = false
      await this.loadData()
      this.showResults = true

      // Handle exports if requested
      try {
        if (this.selectedFormats.includes('csv')) {
          await this.exportCSV()
        }
        if (this.selectedFormats.includes('pdf')) {
          await this.exportPDF()
        }
      } catch (e) {
        this.error = e.message || 'Export failed'
      }
    },

    resetFilters() {
      this.selectedAttributes = []
      this.selectedDescriptions = []
      this.viewType = 'all'
      this.selectedFormats = ['preview']
      this.stats = null
      this.showResults = false
      this.error = null
    },

    formatGroupTitle(dist) {
      const attrs = dist.attributes?.join(', ') || 'No Attributes'
      const descs = dist.descriptions?.length ? ` (${dist.descriptions.join(', ')})` : ''
      return `${attrs}${descs}`
    },

    getAgreementColor(example) {
      return example.is_agreement ? 'green' : 'red'
    },

    getAgreementIcon(example) {
      return example.is_agreement ? this.icons.check : this.icons.alert
    },

    getAgreementText(example) {
      return example.is_agreement ? 'Agreement' : 'Disagreement'
    },

    getDistributionKey(dist) {
      const attrs = dist.attributes?.join('-') || 'no-attrs'
      const descs = dist.descriptions?.join('-') || 'no-descs'
      return `dist-${attrs}-${descs}`
    },

    truncateText(text, length) {
      if (!text) return ''
      return text.length > length ? text.substr(0, length) + '...' : text
    },

    exportCSV() {
      if (!this.stats) {
        throw new Error('No data available for export')
      }

      const csvData = []
      
      // Add header information
      csvData.push(['Disagreement Report'])
      csvData.push([])
      csvData.push(['Filters Applied:'])
      csvData.push(['Attributes', this.selectedAttributes.join(', ') || 'None'])
      csvData.push(['Descriptions', this.selectedDescriptions.join(', ') || 'None'])
      csvData.push(['View Type', this.viewType])
      csvData.push([])
      
      // Add filtered statistics
      csvData.push(['Filtered Statistics'])
      csvData.push(['Total Examples (Filtered)', this.filteredTotalExamples])
      csvData.push(['Disagreements (Filtered)', this.filteredDisagreements])
      csvData.push(['Agreements (Filtered)', this.filteredAgreements])
      csvData.push([])
      
      // Add detailed data header
      csvData.push([
        'Group Attributes',
        'Group Descriptions', 
        'Group Total Members',
        'Example ID',
        'Example Text',
        'Agreement Status',
        'Total Annotators',
        'Non-Annotated',
        'Label',
        'Label Count'
      ])
      
      // Add detailed data
      for (const dist of this.labelDistributions) {
        const groupAttrs = dist.attributes?.join(', ') || ''
        const groupDescs = dist.descriptions?.join(', ') || ''
        
        for (const example of dist.examples || []) {
          // Add example summary row
          csvData.push([
            groupAttrs,
            groupDescs,
            dist.total_members,
            example.example_id,
            example.example_text,
            example.is_agreement ? 'Agreement' : 'Disagreement',
            example.total,
            example.non_annotated,
            'ALL LABELS',
            ''
          ])
          
          // Add individual label rows
          for (const label of example.labels || []) {
            csvData.push([
              '', '', '', '', '', '', '', '',
              label.label,
              label.count
            ])
          }
        }
      }

      // Convert to CSV format and download
      const csvContent = csvData.map(row => 
        row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(',')
      ).join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `disagreement-report-${this.$route.params.id}.csv`
      link.click()
    },

    async exportPDF() {
      if (!this.stats) {
        throw new Error('No data available for export')
      }

      try {
        const { jsPDF: JsPDF } = await import('jspdf')
        const pdf = new JsPDF()
        
        // Set document properties
        pdf.setProperties({
          title: 'Disagreement Report',
          subject: 'Annotation Disagreement Analysis',
          author: 'Doccano Reporting System'
        })

        let yPos = 20
        
        // Add title
        pdf.setFontSize(18)
        pdf.setTextColor(40)
        const pageWidth = pdf.internal.pageSize.getWidth()
        pdf.text('Disagreement Report', pageWidth / 2, yPos, { align: 'center' })
        yPos += 20
        
        // Add filter information
        pdf.setFontSize(12)
        pdf.setTextColor(0)
        pdf.text('Applied Filters:', 20, yPos)
        yPos += 8
        const attributesText = `• Attributes: ${this.selectedAttributes.join(', ') || 'None'}`
        pdf.text(attributesText, 25, yPos)
        yPos += 6
        const descriptionsText = `• Descriptions: ${this.selectedDescriptions.join(', ') || 'None'}`
        pdf.text(descriptionsText, 25, yPos)
        yPos += 6
        pdf.text(`• View Type: ${this.viewType}`, 25, yPos)
        yPos += 15
        
        // Add filtered statistics
        pdf.setFontSize(14)
        pdf.setTextColor(0, 0, 139)
        pdf.text('Filtered Global Results', 20, yPos)
        yPos += 10
        
        pdf.setFontSize(12)
        pdf.setTextColor(0)
        pdf.text(`• Total Examples (Filtered): ${this.filteredTotalExamples}`, 25, yPos)
        yPos += 6
        pdf.text(`• Disagreements: ${this.filteredDisagreements}`, 25, yPos)
        yPos += 6
        pdf.text(`• Agreements: ${this.filteredAgreements}`, 25, yPos)
        yPos += 20
        
        // Add detailed information
        for (const dist of this.labelDistributions) {
          // Check if we need a new page
          if (yPos > 250) {
            pdf.addPage()
            yPos = 20
          }
          
          pdf.setFontSize(14)
          pdf.setTextColor(0, 0, 139)
          pdf.text(`Group: ${this.formatGroupTitle(dist)}`, 20, yPos)
          yPos += 8
          
          pdf.setFontSize(10)
          pdf.setTextColor(0)
          pdf.text(`Total Members in Group: ${dist.total_members}`, 25, yPos)
          yPos += 12
          
          for (const example of dist.examples || []) {
            if (yPos > 260) {
              pdf.addPage()
              yPos = 20
            }
            
            pdf.setFontSize(11)
            pdf.text(`Example #${example.example_id}`, 30, yPos)
            yPos += 6
            
            const truncatedText = this.truncateText(example.example_text, 80)
            const textLines = pdf.splitTextToSize(truncatedText, 150)
            pdf.setFontSize(9)
            pdf.text(textLines, 35, yPos)
            yPos += textLines.length * 4 + 2
            
            const agreementText = example.is_agreement ? 'Agreement' : 'Disagreement'
            pdf.text(`Status: ${agreementText}`, 35, yPos)
            yPos += 6
            const annotatorInfo = `Annotators: ${example.total}, Non-Annotated: ${example.non_annotated}`
            pdf.text(annotatorInfo, 35, yPos)
            yPos += 8
            
            // Add labels
            for (const label of example.labels || []) {
              pdf.text(`  - ${label.label}: ${label.count}`, 40, yPos)
              yPos += 5
            }
            yPos += 5
          }
        }
        
        // Save the PDF
        pdf.save(`disagreement-report-${this.$route.params.id}.pdf`)
      } catch (e) {
        console.error('PDF export error:', e)
        throw new Error('Failed to generate PDF. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.v-card {
  margin-bottom: 20px;
}

.text-h4 {
  font-weight: bold;
}

.text-subtitle-1 {
  opacity: 0.8;
}
</style>