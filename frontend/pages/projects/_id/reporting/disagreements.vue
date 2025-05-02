<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Disagreement Statistics</v-toolbar-title>
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
              <v-icon left>{{icons.refresh}}</v-icon>
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
          <v-row justify="center">
            <v-col cols="12" md="6">
              <doughnut-chart
                v-if="stats.total_examples > 0"
                ref="pieChart"
                :conflict-data="doughnutData"
                title="Overall Agreement"
              />
            </v-col>
          </v-row>

          <template v-for="dist in labelDistributions">
            <v-divider 
            :key="`div-${dist.attribute}-${dist.description}-${dist.examples[0]?.example_id}`"
             class="my-6"></v-divider>
            <v-subheader :key="`subheader-${dist.attribute}`"  class="text-h4 primary--text">
              {{ dist.attribute }} - {{ dist.description }}
            </v-subheader>
            
            <v-row v-for="example in dist.examples"
             :key="`${dist.attribute}-${dist.description}-${example.example_id}`">
              <v-col cols="12" md="3">
                <v-card outlined>
                  <v-card-title>Text: {{ truncate(example.example_text, 50) }}</v-card-title>
                  <v-card-text>
                    Total Annotations: {{ exampleTotal(example) }}
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="9">
                <doughnut-chart
                  :distribution-data="formatChartData(example)"
                  :example-name="example.example_text"
                  :title="`${dist.attribute} Distribution`"
                  :ref="`chart-${example.example_id}`"
                />
              </v-col>
            </v-row>
          </template>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import Vue from 'vue';
import { mdiRefresh } from '@mdi/js'
import ExportFilter from '@/components/reporting/ExportFilter.vue'
import MemberSelector from '@/components/reporting/MemberSelector.vue'
import PerspectiveFilter from '@/components/reporting/PerspectiveFilter.vue'
import DescriptionFilter from '@/components/reporting/DescriptionFilter.vue'
import LabelFilter from '@/components/reporting/LabelFilter.vue'
import DoughnutChart from '~/components/reporting/DoughnutChart.vue'

export default {
  components: {
    ExportFilter,
    MemberSelector,
    PerspectiveFilter,
    DoughnutChart,
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
      selectedFormats: [],
      loading: false,
      error: null,
      icons: {
        refresh: mdiRefresh
      }
    }
  },

  computed: {
    doughnutData() {
      if (!this.stats) return { agreement: 0, conflict: 0 }
      const total = this.stats.total_examples || 1
      const conflictPercentage = (this.stats.conflict_count / total) * 100
      return {
        agreement: 100 - conflictPercentage,
        conflict: conflictPercentage
      }
    },
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
        this.error = e.message || 'Failed to load statistics'
      } finally {
        this.loading = false
      }
    },

    formatChartData(example) {
      const total = example.labels.reduce((sum, item) => sum + item.count, 0)
      return example.labels.map(item => ({
        value: item.label,
        count: item.count,
        percentage: total > 0 ? (item.count / total * 100) : 0
      }))
    },
    exampleTotal(example) {
      return example.labels.reduce((sum, item) => sum + item.count, 0)
    },
    truncate(text, length) {
      return text?.length > length ? text.substr(0, length) + '...' : text
    },

    async applyFilters() {
      this.loading = true;
      try {
        await this.loadData();
        if (this.selectedFormats.includes('csv')) {
          await this.exportCSV().catch(e => {
        throw new Error(`CSV export failed: ${e.message}`);
      });
        }
        if (this.selectedFormats.includes('pdf')) {
          await this.exportPDF().catch(e => {
        throw new Error(`PDF export failed: ${e.message}`);
      });
        }
      } catch (e) {
        this.error = e.message || 'Failed to apply filters';
      } finally {
        this.loading = false;
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
        const conflictPercentage = (this.stats.conflict_count / this.stats.total_examples) * 100
        const csvContent = [
          ['Category', 'Attribute', 'Example Text', 'Label', 'Count', 'Percentage'],
          ['Overall Agreement', '', '', this.stats.total_examples, '', 
            `${(100 - conflictPercentage).toFixed(2)}%`
          ],
          ...this.labelDistributions.flatMap(dist => 
            dist.examples.flatMap(example => 
              example.labels.map(label => [
                'Label Distribution',
                dist.attribute,
                example.example_text,
                label.label,
                label.count,
                `${((label.count / this.exampleTotal(example)) * 100 || 0).toFixed(2)}%`
              ])
            )
          )
        ]
        this.$export.exportCSV(csvContent, 'disagreement-statistics.csv')
        resolve()
      })
    },

    async exportPDF() {
      try {
        const { jsPDF: JsPDF } = await import('jspdf');
        const pdfDoc = new JsPDF('landscape');
        const pageWidth = pdfDoc.internal.pageSize.getWidth();
        let yPosition = 20;

        const tempDiv = document.createElement('div');
        tempDiv.style.position = 'fixed';
        tempDiv.style.left = '-9999px';
        tempDiv.style.width = `${pageWidth}px`;
        document.body.appendChild(tempDiv);

        const DoughnutChartConstructor = this.$options.components.DoughnutChart;
        const DoughnutChart = Vue.extend(DoughnutChartConstructor);
        const doughnutInstance = new DoughnutChart({
          propsData: {
            conflictData: this.doughnutData,
            title: 'Overall Agreement',
          },
        });
        const doughnutWrapper = document.createElement('div');
        tempDiv.appendChild(doughnutWrapper);
        doughnutInstance.$mount(doughnutWrapper);

        const chartInstances = [];
        for (const distribution of this.labelDistributions) {
          for (const example of distribution.examples) {
            const ChartComponent = Vue.extend(DoughnutChartConstructor);
            const instance = new ChartComponent({
              propsData: {
                distributionData: this.formatChartData(example),
                title: `${distribution.attribute} Distribution`,
              },
            });
            const wrapper = document.createElement('div');
            tempDiv.appendChild(wrapper);
            instance.$mount(wrapper);
            chartInstances.push(instance);
          }
        }

        await new Promise((resolve) => {
          setTimeout(async () => {
            const doughnutCanvas = await this.captureChartElement(doughnutInstance.$el);
            if (doughnutCanvas) {
              const imgWidth = pageWidth * 0.2;
              const imgHeight = (doughnutCanvas.height * imgWidth) / doughnutCanvas.width;
              pdfDoc.addImage(doughnutCanvas, 'PNG', (pageWidth - imgWidth) / 2, yPosition, imgWidth, imgHeight);
              yPosition += imgHeight + 10;
            }

            for (const instance of chartInstances) {
              const canvas = await this.captureChartElement(instance.$el);
              if (canvas) {
                const imgWidth = pageWidth * 0.2;
                const imgHeight = (canvas.height * imgWidth) / canvas.width;

                if (yPosition + imgHeight > pdfDoc.internal.pageSize.getHeight() - 20) {
                  pdfDoc.addPage();
                  yPosition = 20;
                }

                pdfDoc.addImage(canvas, 'PNG', (pageWidth - imgWidth) / 2, yPosition, imgWidth, imgHeight);
                yPosition += imgHeight + 10;
              }
            }

            // Cleanup
            tempDiv.remove();
            doughnutInstance.$destroy();
            chartInstances.forEach((instance) => instance.$destroy());
            resolve();
          }, 2000); // Allow time for chart rendering
        });

        pdfDoc.save(`disagreement-statistics-${this.$route.params.id}.pdf`);
      } catch (e) {
        console.error('PDF Export Error:', e);
        this.error = 'Failed to generate PDF. Please try again.';
        throw e;
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
  },
}
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>