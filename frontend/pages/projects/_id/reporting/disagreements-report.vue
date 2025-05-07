<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Disagreement Report</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>

      <v-card-text class="grey lighten-4 py-2">
        <v-row align="center" no-gutters>
          <v-col cols="12" md="4">
            <member-selector 
              v-model="selectedMembers" 
              :project-id="$route.params.id" 
            />
          </v-col>
          <v-col cols="12" md="4" class="pl-md-2">
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
            <label-filter 
              v-model="selectedLabels"
              :project-id="$route.params.id"
            />
          </v-col>
          <v-col cols="12" md="3" class="pl-md-2">
            <export-filter v-model="selectedFormats" />
          </v-col>
          <v-col cols="12" md="4" class="pl-md-2">
            <v-btn color="primary" @click="applyFilters">
              <v-icon left>{{ icons.refresh }}</v-icon>
              Apply Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-text>
        <v-alert v-if="error" type="error">
          {{ error }}
        </v-alert>

        <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

        <template v-if="!loading && stats && selectedFormats.includes('preview')">
          <!-- Overall Statistics Section -->
          <v-card class="mb-6" outlined>
            <v-card-title class="primary--text">Global Results</v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Total Examples</td>
                      <td>{{ stats.total_examples }}</td>
                    </tr>
                    <tr>
                      <td>Conflict Count</td>
                      <td>{{ stats.conflict_count }}</td>
                    </tr>
                    <tr>
                      <td>Agreement Count</td>
                      <td>{{ stats.total_examples - stats.conflict_count }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>

          <!-- Label Distributions Section -->
          <v-card 
            v-for="dist in labelDistributions" 
            :key="`dist-${dist.attribute}-${dist.description}`" 
            class="mb-6" 
            outlined
          >
            <v-card-title class="primary--text">
              {{ dist.attribute }} - {{ dist.description }}
            </v-card-title>
            
            <v-card-text v-for="example in dist.examples" :key="example.example_id">
              <v-card class="mb-4" outlined>
                <v-card-title>Example Text: {{ example.example_text }}</v-card-title>
                <v-card-subtitle>Total Annotations: {{ exampleTotal(example) }}</v-card-subtitle>
                <v-card-text>
                  <v-simple-table>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Label</th>
                          <th>Count</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="label in example.labels" :key="label.label">
                          <td>{{ label.label }}</td>
                          <td>{{ label.count }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </v-card-text>
              </v-card>
            </v-card-text>
          </v-card>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { mdiRefresh } from '@mdi/js'
import ExportFilter from '@/components/reporting/ExportFilter.vue'
import MemberSelector from '@/components/reporting/MemberSelector.vue'
import PerspectiveFilter from '@/components/reporting/PerspectiveFilter.vue'
import DescriptionFilter from '@/components/reporting/DescriptionFilter.vue'
import LabelFilter from '@/components/reporting/LabelFilter.vue'

export default {
  components: {
    ExportFilter,
    MemberSelector,
    PerspectiveFilter,
    LabelFilter,
    DescriptionFilter,
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      stats: null,
      selectedMembers: [],
      selectedAttributes: [],
      selectedDescriptions: [],
      selectedLabels: [],
      selectedFormats: ['preview'],
      loading: false,
      exportLoading: false,
      error: null,
      icons: {
        refresh: mdiRefresh
      }
    }
  },

  computed: {
    labelDistributions() {
      if (!this.stats?.label_distributions) return []
      return this.stats.label_distributions
    }
  },

  methods: {
    async loadData() {
      this.loading = true
      try {
        const response = await this.$services.reporting.getDisagreementStatistics(
          this.$route.params.id,
          {
            members: this.selectedMembers,
            attributes: this.selectedAttributes,
            descriptions: this.selectedDescriptions,
            labels: this.selectedLabels
          }
        )
        this.stats = response
      } catch (e) {
        this.error = e.message || 'Failed to load data'
      } finally {
        this.loading = false
      }
    },

    async applyFilters() {
      this.loading = true
      const timeout = 5000; // 10 seconds timeout
      let timeoutReached = false;

      const timeoutPromise = new Promise((resolve, reject) => {
        // Use resolve to comply with the naming rule
        resolve('Timeout initialized');
      setTimeout(() => {
        timeoutReached = true;
        reject(new Error('Database Unavailable. Please try again later.'));
      }, timeout);
      });

      try {
      await Promise.race([
        (async () => {
        await this.loadData();
        if (this.selectedFormats.includes('csv')) {
          await this.exportCSV();
        }
        if (this.selectedFormats.includes('pdf')) {
          await this.exportPDF();
        }
        })(),
        timeoutPromise
      ]);
      } catch (e) {
      if (timeoutReached) {
        this.error = 'Database Unavailable. Please try again later.';
      } else {
        this.error = e.message || 'Failed to apply filters';
      }
      } finally {
      this.loading = false;
      }
    },

    exampleTotal(example) {
      return example.labels.reduce((sum, item) => sum + item.count, 0)
    },

    async handleExport(formats) {
      if (!this.stats) {
        this.showError('No data to export')
        return
      }

      this.exportLoading = true
      try {
        for (const format of formats) {
          switch(format) {
            case 'csv':
              await this.exportCSV()
              break
            case 'pdf':
              await this.exportPDF()
              break
          }
        }
        this.$store.dispatch('showSnackbar', {
          text: `Exported ${formats.length} format(s) successfully`,
          color: 'success'
        })
      } catch (e) {
        this.showError('Export failed: ' + (e.message || 'Unknown error'))
      } finally {
        this.exportLoading = false
      }
    },

    showError(message) {
      this.error = message
      setTimeout(() => {
        this.error = null
      }, 5000)
    },

    exportCSV() {
      return new Promise((resolve) => {
        const csvContent = [
          ['Category', 'Attribute', 'Description', 'Example', 'Label', 'Count'],
          ['Overall', '', '', '', 'Total Examples', this.stats.total_examples],
          ['Overall', '', '', '', 'Conflict Count', this.stats.conflict_count],
          ['Overall', '', '', '', 'Agreement Count', this.stats.total_examples - this.stats.conflict_count],
          ...this.labelDistributions.flatMap(dist => 
            dist.examples.flatMap(example => 
              example.labels.map(label => [
                'Label Distribution',
                dist.attribute,
                dist.description,
                example.example_text,
                label.label,
                label.count
              ])
            )
          )
        ]

        this.$export.exportCSV(csvContent, 'disagreement-report.csv')
        resolve()
      })
    },

    async exportPDF() {
    try {
      const { jsPDF: JsPDF } = await import('jspdf');
      const pdfDoc = new JsPDF();
      
      // Set document properties
      pdfDoc.setProperties({
        title: 'Disagreement Report',
        subject: 'Annotation Statistics',
        author: 'Your Application Name',
      });

      // Add title
      pdfDoc.setFontSize(18);
      pdfDoc.setTextColor(40);
      pdfDoc.text('Disagreement Report', pdfDoc.internal.pageSize.getWidth() / 2, 15, { align: 'center' });
      
      let yPosition = 30;
      
      // Add overall statistics section
      pdfDoc.setFontSize(14);
      pdfDoc.setTextColor(0, 0, 139); // Dark blue color
      pdfDoc.text('Overall Results', 14, yPosition);
      yPosition += 10;
      
      pdfDoc.setFontSize(12);
      pdfDoc.setTextColor(0); // Black color
      pdfDoc.text(`• Total Examples: ${this.stats.total_examples}`, 20, yPosition);
      yPosition += 8;
      pdfDoc.text(`• Conflict Count: ${this.stats.conflict_count}`, 20, yPosition);
      yPosition += 8;
      pdfDoc.text(`• Agreement Count: ${this.stats.total_examples - this.stats.conflict_count}`, 20, yPosition);
      yPosition += 15;
      
      // Add label distributions
      pdfDoc.setFontSize(14);
      pdfDoc.setTextColor(0, 0, 139); // Dark blue color
      
      for (const dist of this.labelDistributions) {
        // Check if we need a new page
        if (yPosition > 260) {
          pdfDoc.addPage();
          yPosition = 20;
        }
        
        pdfDoc.text(`${dist.attribute} - ${dist.description}`, 14, yPosition);
        yPosition += 10;
        
        for (const example of dist.examples) {
          // Check if we need a new page before adding example
          if (yPosition > 260) {
            pdfDoc.addPage();
            yPosition = 20;
          }
          
          pdfDoc.setFontSize(12);
          pdfDoc.setTextColor(0); // Black color
          
          // Add example text (truncated)
          const exampleText = this.truncateText(example.example_text, 100);
          const exampleLines = pdfDoc.splitTextToSize(`Example: ${exampleText}`, 170);
          pdfDoc.text(exampleLines, 20, yPosition);
          yPosition += 8 * exampleLines.length;
          
          pdfDoc.text(`• Total Annotations: ${this.exampleTotal(example)}`, 20, yPosition);
          yPosition += 8;
          
          // Add labels
          pdfDoc.setFontSize(10);
          for (const label of example.labels) {
            // Check if we need a new page before adding label
            if (yPosition > 270) {
              pdfDoc.addPage();
              yPosition = 20;
            }
            
            pdfDoc.text(`- ${label.label}: ${label.count}`, 25, yPosition);
            yPosition += 7;
          }
          yPosition += 10;
        }
        yPosition += 5;
      }
      
      // Save the PDF
      pdfDoc.save(`disagreement-report-${this.$route.params.id}.pdf`);
    } catch (e) {
      console.error('PDF export error:', e);
      this.showError('Failed to generate PDF. Please try again.');
      throw new Error('Error generating PDF');
    }
  },

    truncateText(text, length) {
      return text?.length > length ? text.substr(0, length) + '...' : text
    }
  },

  mounted() {
    this.loadData()
  }
}
</script>

<style scoped>
.v-card {
  margin-bottom: 20px;
}
</style>