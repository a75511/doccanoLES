<script>
import { Pie } from 'vue-chartjs'

export default {
  extends: Pie,
  props: {
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
    renderDistributionChart() {
      this.renderChart(
        {
          labels: this.distributionData.map(d => d.value),
          datasets: [{
            data: this.distributionData.map(d => d.percentage),
            backgroundColor: [
              '#4CAF50', '#2196F3', '#FF9800', '#E91E63', 
              '#9C27B0', '#00BCD4', '#CDDC39', '#607D8B'
            ]
          }]
        },
        {
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
                return `${label}: ${value.toFixed(1)}% (${this.distributionData[tooltipItem.index].count} members)`
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
            backgroundColor: ['#4CAF50', '#F44336']
          }]
        },
        {
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