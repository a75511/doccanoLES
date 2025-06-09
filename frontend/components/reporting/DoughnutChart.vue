<template>
  <div class="doughnut-chart-container" :data-example-id="dataExampleId">
    <div class="chart-container">
      <canvas ref="canvas"></canvas>
      <div v-if="exampleName" class="example-name">{{ exampleName }}</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    exampleName: String,
    distributionData: {
      type: Array,
      default: () => [],
      validator: (value) => Array.isArray(value) && value.every(item => 'value' in item && 'percentage' in item)
    },
    title: {
      type: String,
      default: ''
    },
    dataExampleId: {
      type: [Number, String],
      default: null
    }
  },

  data() {
    return {
      chart: null,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutoutPercentage: 60,
        legend: {
          position: 'right'
        },
        title: {
          display: true,
          text: this.title
        },
        tooltips: {
          callbacks: {
            label: (tooltipItem, data) => {
              const label = data.labels[tooltipItem.index] || ''
              const value = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index]
              const count = this.distributionData[tooltipItem.index].count
              return `${label}: ${value.toFixed(1)}% (${count} annotations)`
            }
          }
        },
        animation: {
          onComplete: () => {
            if (!this.chart) return
            
            const ctx = this.chart.ctx
            ctx.font = '14px Roboto'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = '#333'

            this.chart.data.datasets.forEach((_dataset, i) => {
              const meta = this.chart.getDatasetMeta(i)
              meta.data.forEach((segment, index) => {
                const { x, y } = segment.tooltipPosition()
                const percentage = this.distributionData[index].percentage.toFixed(0) + '%'
                ctx.fillText(percentage, x, y)
              })
            })
          }
        }
      }
    }
  },

  watch: {
    distributionData: {
      handler() {
        this.renderDistributionChart()
      },
      deep: true
    },
    title() {
      this.options.title.text = this.title
      if (this.chart) {
        this.chart.options.title.text = this.title
        this.chart.update()
      }
    }
  },

  mounted() {
    this.renderDistributionChart()
  },

  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy()
    }
  },

  methods: {
    renderDistributionChart() {
      if (this.chart) {
        this.chart.destroy()
      }

      if (!this.distributionData || this.distributionData.length === 0) {
        return
      }

      const ctx = this.$refs.canvas.getContext('2d')
      
      // Access Chart.js through the injected chart
      const Chart = this.$chart
      
      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.distributionData.map(d => d.value),
          datasets: [{
            data: this.distributionData.map(d => parseFloat(d.percentage)),
            backgroundColor: [
              '#4CAF50', '#2196F3', '#FF9800', '#E91E63',
              '#9C27B0', '#00BCD4', '#CDDC39', '#607D8B',
              '#795548'
            ],
            borderWidth: 2,
            hoverOffset: 10
          }]
        },
        options: this.options
      })
    }
  }
}
</script>

<style scoped>
.doughnut-chart-container {
  width: 100%;
}

.chart-container {
  position: relative;
  height: 400px;
  padding: 16px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.example-name {
  margin-top: 16px;
  font-style: italic;
  text-align: center;
  color: #666;
}
</style>