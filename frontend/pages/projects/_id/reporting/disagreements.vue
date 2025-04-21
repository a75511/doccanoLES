<template>
  <v-container>
    <v-card>
      <v-toolbar color="primary" dark flat>
        <v-toolbar-title>Disagreement Statistics</v-toolbar-title>
        <v-spacer></v-spacer>
        <export-menu 
          @export="handleExport"
          @error="showError"
        />
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
          <v-col cols="12" md="4" class="pl-md-2">
            <v-btn color="primary" @click="refreshData">
              <v-icon left>{{icons.refresh}}</v-icon>
              Refresh
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-text>
        <v-alert v-if="error" type="error">
          {{ error }}
        </v-alert>

        <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

        <template v-if="!loading && stats">
          <v-row justify="center">
            <v-col cols="12" md="6">
              <pie-chart
                v-if="stats.total_examples > 0"
                ref="pieChart"
                :conflict-data="pieData"
                title="Overall Agreement"
              />
            </v-col>
          </v-row>

          <template v-for="attr in attributeDistributions">
            <v-divider :key="`divider-${attr.attribute}`" class="my-4"></v-divider>
            <v-subheader 
              :key="`subheader-${attr.attribute}`" 
              class="text-h6"
            >
              {{ attr.attribute }} ({{ attr.total_members }} members)
            </v-subheader>
            
            <v-row :key="`row-${attr.attribute}`" justify="center">
              <v-col cols="12" md="6">
                <pie-chart
                  :ref="`attr-${attr.attribute}`"
                  :distribution-data="attr.data"
                  :title="`${attr.attribute} Distribution`"
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
import { mdiRefresh } from '@mdi/js'
import ExportMenu from '@/components/reporting/ExportMenu.vue'
import MemberSelector from '@/components/reporting/MemberSelector.vue'
import PerspectiveFilter from '@/components/reporting/PerspectiveFilter.vue'
import PieChart from '@/components/reporting/PieCharts.vue'

export default {
  components: {
    ExportMenu,
    MemberSelector,
    PerspectiveFilter,
    PieChart
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      stats: null,
      selectedMembers: [],
      selectedAttributes: [],
      loading: false,
      exportLoading: false,
      error: null,
      icons: {
        refresh: mdiRefresh
      }
    }
  },

  computed: {
    pieData() {
      if (!this.stats) return { agreement: 0, conflict: 0 }
      return {
        agreement: 100 - this.stats.conflict_percentage,
        conflict: this.stats.conflict_percentage
      }
    },
    attributeDistributions() {
      return this.stats?.attribute_distributions || []
    }
  },

  mounted() {
    this.loadData()
  },

  methods: {
    async loadData() {
      this.loading = true
      try {
        const response = await this.$services.reporting.getDisagreementStatistics(
          this.$route.params.id,
          {
            members: this.selectedMembers,
            attributes: this.selectedAttributes
          }
        )
        this.stats = response
      } catch (e) {
        this.error = e.message || 'Failed to load statistics'
      } finally {
        this.loading = false
      }
    },

    refreshData() {
      this.loadData()
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
            case 'preview':
              await this.previewReport()
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
          ['Category', 'Attribute', 'Value', 'Members Count', 'Percentage'],
          ['Overall Agreement', '', '', this.stats.total_examples, 
            `${(100 - this.stats.conflict_percentage).toFixed(2)}%`
          ],
          ...this.stats.attribute_distributions.flatMap(attr => 
            attr.data.map(item => [
              'Attribute Distribution',
              attr.attribute,
              item.value,
              item.count,
              `${item.percentage.toFixed(2)}%`
            ])
          )
        ]

        this.$export.exportCSV(csvContent, 'disagreement-statistics.csv')
        resolve()
      })
    },

    async exportPDF() {
      try {
        await this.$nextTick()
        const { jsPDF: JsPDF } = await import('jspdf')
        
        const pdfDoc = new JsPDF('landscape')
        const pageWidth = pdfDoc.internal.pageSize.getWidth()
        let yPosition = 20

        pdfDoc.setFontSize(18)
        pdfDoc.text('Disagreement Statistics', pageWidth/2, 15, { align: 'center' })

        const pieCanvas = await this.captureChart('pieChart')
        if (pieCanvas) {
          const imgWidth = pageWidth * 0.4
          const imgHeight = (pieCanvas.height * imgWidth) / pieCanvas.width
          pdfDoc.addImage(pieCanvas.toDataURL('image/png'), 'PNG', 
            (pageWidth - imgWidth) / 2, yPosition, imgWidth, imgHeight)
          yPosition += imgHeight + 20
        }

        pdfDoc.setFontSize(14)
        for (const attr of this.stats.attribute_distributions) {
          const chartId = `attr-${attr.attribute}`
          const canvas = await this.captureChart(chartId)

          if (canvas) {
            const imgWidth = pageWidth * 0.6
            const imgHeight = (canvas.height * imgWidth) / canvas.width
            
            if (yPosition + imgHeight > pdfDoc.internal.pageSize.getHeight() - 20) {
              pdfDoc.addPage()
              yPosition = 20
            }
            
            pdfDoc.addImage(canvas.toDataURL('image/png'), 'PNG', 
              (pageWidth - imgWidth) / 2, yPosition, imgWidth, imgHeight)
            yPosition += imgHeight + 20
          }
        }

        pdfDoc.save(`disagreement-statistics-${this.$route.params.id}.pdf`)
      } catch (e) {
        throw new Error('Error generating PDF')
      }
    },

    async previewReport() {
      if (!this.stats) {
        throw new Error('No data to preview')
      }

      try {
        const previewWindow = window.open('', '_blank')
        if (!previewWindow) return

        previewWindow.document.write('<!DOCTYPE html><html><head><title>Loading Preview...</title></head><body></body></html>')
        previewWindow.document.close()

        const container = previewWindow.document.createElement('div')
        container.innerHTML = `
          <style>
            body { padding: 20px; text-align: center; }
            .chart-container { 
              margin: 20px auto; 
              padding: 15px;
              border: 1px solid #ddd;
              max-width: 800px;
            }
            img { max-width: 100%; display: block; margin: 0 auto; }
            h1 { color: #2c3e50; font-family: Arial, sans-serif; }
            h2 { margin: 30px 0 10px; color: #34495e; }
          </style>
          <h1>Disagreement Statistics Preview</h1>
        `

        const charts = [
          { ref: 'pieChart', title: 'Overall Agreement' },
          ...this.stats.attribute_distributions.map(attr => ({
            ref: `attr-${attr.attribute}`,
            title: `${attr.attribute} Distribution`
          }))
        ]

        for (const chart of charts) {
          const canvas = await this.captureChart(chart.ref)
          if (canvas) {
            const img = previewWindow.document.createElement('img')
            img.src = canvas.toDataURL()
            
            const chartContainer = previewWindow.document.createElement('div')
            chartContainer.className = 'chart-container'
            chartContainer.appendChild(img)
            
            container.appendChild(chartContainer)
          }
        }

        previewWindow.document.body.innerHTML = container.innerHTML
        previewWindow.document.title = 'Statistics Preview'
      } catch (e) {
        throw new Error('Failed to generate preview')
      }
    },
    
    async captureChart(refName) {
      try {
        const html2canvas = await import('html2canvas')
        const chartRef = this.$refs[refName]
        if (!chartRef) return null
        
        const chartElement = Array.isArray(chartRef) 
          ? chartRef[0].$el 
          : chartRef.$el
        
        await new Promise(resolve => setTimeout(resolve, 100))
        
        return html2canvas.default(chartElement, { 
          scale: 1,
          logging: false,
          useCORS: true
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
</style>