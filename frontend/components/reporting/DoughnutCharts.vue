<script>
import { Doughnut } from 'vue-chartjs'

export default {
  extends: Doughnut,
  props: {
    exampleName: String,
    showAgreement: {
      type: Boolean,
      default: true
    },
    conflictData: {
      type: Object,
      default: () => ({ agreement: 0, conflict: 0 }),
      validator: (value) => 'agreement' in value && 'conflict' in value
    },
    distributionData: {
      type: Array,
      default: () => [],
      validator: (value) => Array.isArray(value) && value.every(item => 'value' in item && 'percentage' in item)
    },
    title: {
      type: String,
      default: ''
    },
  },
  computed: {
    agreementStatus() {
      const threshold = 60
      const hasAgreement = this.distributionData.some(d => d.percentage >= threshold)
      return hasAgreement ? 'agreement' : 'disagreement'
    },
    agreementText() {
      return this.agreementStatus === 'agreement' ? 
        'Consensus Reached' : 'Needs Review'
    },
    agreementPercentage() {
      const max = Math.max(...this.distributionData.map(d => d.percentage))
      return max.toFixed(1)
    }
  },

  mounted() {
    if (this.distributionData.length > 0) {
      this.renderDistributionChart()
    } else if (this.conflictData.agreement !== undefined) {
      this.renderConflictChart()
    }
  },

  methods: {
    setupChartContainer() {
      this.$el.innerHTML = `
        <div class="chart-container" style="position: relative; height: 400px">
          ${this.showAgreement ? `
            <div class="agreement-indicator ${this.agreementStatus}">
              ${this.agreementText} (${this.agreementPercentage}%)
            </div>` : ''}
          <canvas style="height: 350px; width: 100%"></canvas>
          ${this.exampleName ? `
            <div class="example-name">${this.exampleName}</div>` : ''}
        </div>
      `
    },

    mounted() {
      this.setupChartContainer()
      this.$nextTick(() => {
        if (this.distributionData.length > 0) {
          this.renderDistributionChart()
        } else if (this.conflictData.agreement !== undefined) {
          this.renderConflictChart()
        }
      })
    },
    renderDistributionChart() {
      this.renderChart(
        {
          labels: this.distributionData.map(d => d.value),
          datasets: [{
            data: this.distributionData.map(d => d.percentage),
            backgroundColor: [
              '#4CAF50', '#2196F3', '#FF9800', '#E91E63', 
              '#9C27B0', '#00BCD4', '#CDDC39', '#607D8B'
            ],
            borderWidth: 3,
            hoverOffset: 10
          }]
        },
        {
          cutoutPercentage: 60,
          responsive: true,
          maintainAspectRatio: false,
          title: {
            display: !!this.title,
            text: this.title
          },
          animation: {
            onComplete: () => {
              const ctx = this.$data._chart.ctx
              ctx.font = '16px Arial'
              ctx.textAlign = 'center'
              ctx.textBaseline = 'bottom'
              ctx.fillStyle = '#1d1f1f'
              
              this.$data._chart.data.datasets.forEach((_, i) => {
                const meta = this.$data._chart.getDatasetMeta(i)
                meta.data.forEach((segment, index) => {
                  const { x, y } = segment.tooltipPosition()
                  const percentage = this.distributionData[index].percentage.toFixed(0) + '%'
                  ctx.fillText(percentage, x, y)
                })
              })
            }
          },
          tooltips: {
            callbacks: {
              label: (tooltipItem, data) => {
                const label = data.labels[tooltipItem.index]
                const value = data.datasets[0].data[tooltipItem.index]
                const count = this.distributionData[tooltipItem.index].count
                return `${label}: ${value.toFixed(1)}% (${count} annotations)`
              }
            }
          }
        }
      )
    },

    renderConflictChart() {
      this.renderChart(
        {
          labels: ['Agreements', 'Conflicts'],
          datasets: [{
            data: [this.conflictData.agreement, this.conflictData.conflict],
            backgroundColor: ['#4CAF50', '#F44336'],
            borderWidth: 3,
          }]
        },
        {
          cutoutPercentage: 60,
          responsive: true,
          maintainAspectRatio: false,
          title: {
            display: !!this.title,
            text: this.title
          },
          animation: {
            onComplete: () => {
              const ctx = this.$data._chart.ctx
              ctx.font = '16px Arial'
              ctx.textAlign = 'center'
              ctx.textBaseline = 'bottom'
              ctx.fillStyle = '#1d1f1f'
              
              this.$data._chart.data.datasets.forEach((_, i) => {
                const meta = this.$data._chart.getDatasetMeta(i)
                meta.data.forEach((segment, index) => {
                  const { x, y } = segment.tooltipPosition()
                  const percentage = index === 0 
                    ? this.conflictData.agreement.toFixed(0)
                    : this.conflictData.conflict.toFixed(0)
                  ctx.fillText(percentage + '%', x, y)
                })
              })
            }
          },
          tooltips: {
            callbacks: {
              label: (tooltipItem, data) => {
                const label = data.labels[tooltipItem.index]
                const value = data.datasets[0].data[tooltipItem.index]
                return `${label}: ${value.toFixed(1)}%`
              }
            }
          }
        }
      )
    }
  }
}
</script>

<style scoped>
.agreement-indicator {
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-weight: bold;
  text-align: center;
}

.agreement-indicator.agreement {
  background-color: #4CAF50;
  color: white;
}

.agreement-indicator.disagreement {
  background-color: #F44336;
  color: white;
}

.example-name {
  margin-top: 16px;
  font-style: italic;
  text-align: center;
}
</style>