<template>
    <v-select
      :value="value"
      :items="labels"
      label="Filter by Labels"
      multiple
      chips
      item-text="text"
      item-value="value"
      clearable
      @input="$emit('input', $event)"
    />
  </template>
  
  <script>
  export default {
    props: {
      projectId: String,
      value: Array
    },
    data() {
      return { labels: [] }
    },
    async fetch() {
      try {
        const response = await this.$services.categoryType.list(this.projectId)
        this.labels = response.map(l => ({
          text: l.text,
          value: l.text
        }))
      } catch (error) {
        console.error('Error loading labels:', error)
      }
    }
  }
  </script>