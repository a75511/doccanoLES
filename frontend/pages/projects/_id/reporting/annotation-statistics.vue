<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Annotation Statistics</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>

      <v-card-text class="grey lighten-4 py-2">
        <v-row align="center" no-gutters>
          <v-col cols="12" md="4">
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
            <v-select
              v-model="viewType"
              :items="viewTypes"
              label="View Type"
              clearable
            />
          </v-col>
          <v-col cols="12" md="3" class="pl-md-2">
            <export-filter v-model="selectedFormats" />
          </v-col>
          <v-col cols="12" md="4" class="pl-md-1 d-flex align-center">
            <v-btn color="primary" @click="applyFilters" :loading="loading" class="mr-2">
              <v-icon left>{{icons.refresh}}</v-icon>
              Apply
            </v-btn>
            <v-btn color="secondary" @click="resetFilters">
              <v-icon left>{{icons.close}}</v-icon>
              Reset
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-text>
        <v-alert v-if="error" type="error">
          {{ error }}
        </v-alert>

        <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

        <!-- Only show charts if data has been loaded AND Apply was clicked -->
        <div>
          <template v-if="!loading && stats && showResults && selectedFormats.includes('preview')">
            <template v-for="(dist, index) in labelDistributions">
              <v-divider :key="`div-${index}`" class="my-6"></v-divider>
              <v-subheader :key="`subheader-${index}`" class="text-h4 primary--text">
                {{ dist.attributes.join(', ') }} - {{ dist.descriptions.join(', ') }}
              </v-subheader>
              
              <v-row v-for="(example, exIndex) in dist.examples"
                :key="`example-${index}-${exIndex}`">
                <v-col cols="12" md="3">
                  <v-card outlined>
                    <v-card-title>Text: {{ truncate(example.example_text, 50) }}</v-card-title>
                    <v-card-text>
                      <div>Total Annotators: {{ example.total }} / {{ dist.total_members }}</div>
                      <div :class="agreementClass(example)">
                        {{ example.is_agreement ? 'Agreement' : 'Disagreement' }}:
                         {{ example.agreement_rate.toFixed(1) }}%
                        <v-icon small>{{ agreementIcon(example) }}</v-icon>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="9">
                  <doughnut-chart
                    :distribution-data="formatChartData(example, dist.total_members)"
                    :title="`${dist.attributes.join(', ')} Distribution`"
                    :data-example-id="example.example_id"
                  />
                </v-col>
              </v-row>
            </template>
          </template>

          <!-- Hidden charts container for PDF generation -->
          <div class="hidden-charts-container" ref="hiddenChartsContainer">
            <template v-if="stats && generateHiddenCharts">
              <template v-for="(dist, index) in labelDistributions">
                <div v-for="(example, exIndex) in dist.examples"
                  :key="`hidden-example-${index}-${exIndex}`"
                  class="hidden-chart-wrapper">
                  <div class="chart-info">
                    <h3>Example #{{ example.example_id }}</h3>
                    <p>{{ truncate(example.example_text, 100) }}</p>
                    <p :style="{ color: example.is_agreement ? '#4CAF50' : '#F44336' }">
                      Agreement Rate: {{ example.agreement_rate.toFixed(1) }}% 
                      ({{ example.is_agreement ? 'Agreement' : 'Disagreement' }})
                    </p>
                  </div>
                  <doughnut-chart
                    :distribution-data="formatChartData(example, dist.total_members)"
                    :title="`${dist.attributes.join(', ')} Distribution`"
                    :data-example-id="example.example_id"
                  />
                </div>
              </template>
            </template>
          </div>

          <v-alert
            v-if="!loading && showResults && (!stats || !stats.label_distributions.length)"
            type="info"
            class="ma-4"
          >
            No data available for the current filters
          </v-alert>

          <v-alert
            v-else-if="!loading && !showResults"
            type="info"
            class="ma-4"
          >
            Please select at least one Attribute and Click "Apply" to load and display statistics
          </v-alert>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { mdiRefresh, mdiClose, mdiCheck, mdiAlert } from '@mdi/js'
import ExportFilter from '@/components/reporting/ExportFilter.vue'
import PerspectiveFilter from '@/components/reporting/PerspectiveFilter.vue'
import DescriptionFilter from '@/components/reporting/DescriptionFilter.vue'
import DoughnutChart from '~/components/reporting/DoughnutChart.vue'

export default {
  components: {
    ExportFilter,
    PerspectiveFilter,
    DoughnutChart,
    DescriptionFilter,
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      stats: null,
      selectedAttributes: [],
      selectedDescriptions: [],
      viewType: 'all',
      viewTypes: [
        { text: 'All', value: 'all' },
        { text: 'Only Agreements', value: 'agreement' },
        { text: 'Only Disagreements', value: 'disagreement' }
      ],
      selectedFormats: ['preview'],
      loading: false,
      error: null,
      showResults: false,
      generateHiddenCharts: false,
      icons: {
        refresh: mdiRefresh,
        close: mdiClose,
        check: mdiCheck,
        alert: mdiAlert
      }
    }
  },

  computed: {
    labelDistributions() {
      return this.stats?.label_distributions || []
    }
  },

  methods: {
    async loadData() {
      this.loading = true
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
      } catch (error) {
        this.error = error.response?.data?.error || error.message
      } finally {
        this.loading = false
      }
    },

    formatChartData(example, totalMembers) {
      const chartData = [
        ...example.labels.map(item => ({
          value: `${item.label} (${item.count})`,
          count: item.count,
          percentage: (item.count / totalMembers * 100)
        }))
      ]

      // Add non-annotated entry
      if (example.non_annotated > 0) {
        chartData.push({
          value: `Not Annotated (${example.non_annotated})`,
          count: example.non_annotated,
          percentage: (example.non_annotated / totalMembers * 100)
        })
      }

      return chartData
    },

    truncate(text, length) {
      return text?.length > length ? text.substr(0, length) + '...' : text
    },

    async applyFilters() {
      this.loading = true;
      this.stats = null;
      this.error = null;
      this.showResults = false;
      
      try {
        // First load the data
        await this.loadData();
        
        // Set showResults to true so charts can render
        const hasData = this.stats && 
                       this.stats.label_distributions && 
                       this.stats.label_distributions.length > 0;
        
        this.showResults = hasData;

        if (!hasData) {
          this.error = 'No data available for the selected filters';
          return;
        }
        
        // Wait for DOM to update and charts to render
        await this.$nextTick();
        
        // If PDF is requested, generate hidden charts and wait for them to render
        if (this.selectedFormats.includes('pdf')) {
          this.generateHiddenCharts = true;
          await this.$nextTick();
          // Additional wait to ensure charts are fully rendered
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // Handle exports after charts are ready
        if (this.selectedFormats.includes('csv')) {
          await this.exportCSV();
        }
        
        if (this.selectedFormats.includes('pdf')) {
          await this.exportPDF().catch(e => {
            throw new Error(`PDF export failed: ${e.message}`);
          });
          // Clean up hidden charts after PDF generation
          this.generateHiddenCharts = false;
        }
        
      } catch (e) {
        this.error = e.message || 'Failed to apply filters';
        this.showResults = false;
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.selectedAttributes = []
      this.selectedDescriptions = []
      this.selectedFormats = ['preview']
      this.stats = null;
      this.showResults = false;
      this.generateHiddenCharts = false;
    },

    agreementClass(example) {
      return example.is_agreement ? 'green--text' : 'red--text';
    },

    agreementIcon(example) {
      return example.is_agreement ? this.icons.check : this.icons.alert;
    },

    showError(message) {
      this.error = message
      setTimeout(() => {
        this.error = null
      }, 5000)
    },

    exportCSV() {
      if (!this.stats) return;
      
      const rows = [];
      
      // 1. Report header
      rows.push({ '': 'Annotation Statistics' });
      rows.push({});
      
      // 2. Filters section
      rows.push({ '': 'Values' });
      rows.push({ '': 'Attributes', ' ': this.selectedAttributes.join(', ') || 'None' });
      rows.push({ '': 'Descriptions', ' ': this.selectedDescriptions.join(', ') || 'None' });
      rows.push({ '': 'View Type', ' ': this.viewType || 'all' });
      rows.push({});
      
      // 3. Overall statistics
      rows.push({ '': 'Overall Statistics' });
      rows.push({ '': 'Total Examples', ' ': this.stats.total_examples });
      rows.push({ '': 'Conflict Count', ' ': this.stats.conflict_count });
      // Get the maximum total annotators across examples
      let count = 0;
      for (const dist of this.labelDistributions) {
        count++;
        // Add group header with annotator info for each example group
        rows.push({
          ' ': `Total Annotators: ${dist.total_members}`
        });
        if(count===1) break;
      }
      rows.push({});

      
      // 4. Table header
      rows.push({
        'Group Attributes': 'Group Attributes',
        'Group Descriptions': 'Group Descriptions',
        'Example ID': 'Example ID',
        'Example Text': 'Example Text',
        'Label': 'Label',
        'Count': 'Count',
        'Percentage': 'Percentage',
        'Total Annotators': 'Total Annotators',
        'Non-Annotated': 'Non-Annotated',
        'Agreement Rate': 'Agreement Rate',
        'Is Agreement': 'Is Agreement'
      });
      
      // 5. Table data
      for (const dist of this.labelDistributions) {
        for (const example of dist.examples) {
          // Main example row
          rows.push({
            'Group Attributes': dist.attributes.join(', '),
            'Group Descriptions': dist.descriptions.join(', '),
            'Example ID': example.example_id,
            'Example Text': example.example_text,
            'Label': 'ALL LABELS',
            'Count': '',
            'Percentage': '',
            'Total Annotators': example.total,
            'Non-Annotated': example.non_annotated,
            'Agreement Rate': this.formatPercentage(example.agreement_rate, 1),
            'Is Agreement': example.is_agreement ? 'Yes' : 'No'
          });

          // Label rows
          for (const label of example.labels) {
            rows.push({
              'Group Attributes': '',
              'Group Descriptions': '',
              'Example ID': '',
              'Example Text': '',
              'Label': label.label,
              'Count': label.count,
              'Percentage': this.formatPercentage((label.count / dist.total_members) * 100, 1),
              'Total Annotators': '',
              'Non-Annotated': '',
              'Agreement Rate': '',
              'Is Agreement': ''
            });
          }
        }
      }

      this.$export.exportCSV(rows, `disagreement-statistics-${this.$route.params.id}.csv`);
    },

    formatPercentage(value, decimals = 1) {
      if (typeof value !== 'number') return value;
      return value.toFixed(decimals).replace('.', ',') + '%';
    },

    async exportPDF() {
      if (!this.stats || 
          !this.labelDistributions || 
          this.labelDistributions.length === 0) {
        return;
      }
      try {
        const { jsPDF: JsPDF } = await import('jspdf');
        const pdfDoc = new JsPDF('landscape');
        const pageWidth = pdfDoc.internal.pageSize.getWidth();
        let yPosition = 20;

        // Add report title
        pdfDoc.setFontSize(18);
        pdfDoc.text('Annotation Statistics', pageWidth / 2, yPosition, { align: 'center' });
        yPosition += 15;

        // Add filter information
        pdfDoc.setFontSize(12);
        pdfDoc.text(`Filters Applied:`, 20, yPosition);
        yPosition += 8;
        pdfDoc.text(`• Attributes: ${this.selectedAttributes.join(', ') || 'None'}`, 25, yPosition);
        yPosition += 8;
        pdfDoc.text(`• Descriptions: ${this.selectedDescriptions.join(', ') || 'None'}`, 25, yPosition);
        yPosition += 8;
        pdfDoc.text(`• View Type: ${this.viewType}`, 25, yPosition);
        yPosition += 15;

        // Add overall statistics
        pdfDoc.text(`Overall Statistics:`, 20, yPosition);
        yPosition += 8;
        pdfDoc.text(`• Total Examples: ${this.stats.total_examples}`, 25, yPosition);
        yPosition += 8;
        pdfDoc.text(`• Conflict Count: ${this.stats.conflict_count}`, 25, yPosition);
        yPosition += 8;
        pdfDoc.text(`• Total Annotators: ${this.stats.total_members}`, 25, yPosition);
        yPosition += 15;

        // Use hidden charts container for PDF generation
        const chartsContainer = this.$refs.hiddenChartsContainer;
        const chartWrappers = chartsContainer.querySelectorAll('.hidden-chart-wrapper');
        const html2canvas = (await import('html2canvas')).default;
        
        for (const wrapper of chartWrappers) {
          // Check if we need a new page
          if (yPosition > pdfDoc.internal.pageSize.getHeight() - 200) {
            pdfDoc.addPage('landscape');
            yPosition = 20;
          }
          
          // Capture the entire wrapper (including text info and chart)
          const canvas = await html2canvas(wrapper, {
            scale: 2,
            backgroundColor: '#FFFFFF',
            logging: false,
            useCORS: true,
            allowTaint: true
          });
          
          // Add image to PDF
          const imgData = canvas.toDataURL('image/png');
          const imgWidth = 260;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          
          pdfDoc.addImage(
            imgData,
            'PNG',
            (pageWidth - imgWidth) / 2,
            yPosition,
            imgWidth,
            imgHeight
          );
          
          yPosition += imgHeight + 20;
        }
        
        pdfDoc.save(`disagreement-statistics-${this.$route.params.id}.pdf`);
      } catch (e) {
        console.error('PDF Export Error:', e);
        this.error = 'Failed to generate PDF. Please try again.';
      }
    },

    async captureChartElement(element) {
      try {
        const html2canvas = await import('html2canvas')
        return await html2canvas.default(element, {
          scale: 1,
          logging: true,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#FFFFFF'
        })
      } catch (e) {
        console.error('Capture error:', e)
        return null
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.hidden-charts-container {
  position: absolute;
  left: -9999px;
  top: -9999px;
  width: 1200px; /* Sufficient width for landscape PDF */
}

.hidden-chart-wrapper {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-info {
  margin-bottom: 15px;
}

.chart-info h3 {
  margin: 0 0 10px 0;
  color: #1976D2;
}

.chart-info p {
  margin: 5px 0;
  font-size: 14px;
}
</style>