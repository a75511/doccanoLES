<template>
    <v-select
      :value="value"
      :items="descriptions"
      label="Filter by Descriptions"
      multiple
      chips
      item-text="description"
      item-value="value"
      clearable
      @input="$emit('input', $event)"
    />
  </template>
  
<script>
export default {
  props: {
    projectId: String,
    selectedAttributes: Array,
    value: Array
  },
  data() {
    return { descriptions: [] }
  },
  watch: {
    selectedAttributes: {
      immediate: true,
      handler: 'fetchDescriptions'
    }
  },
  methods: {
    async fetchDescriptions() {
      if (!this.selectedAttributes?.length) {
        this.descriptions = []
        return
      }
      
      try {
        const response = await this.$services.reporting.getAttributeDescriptions(
          this.projectId, 
          this.selectedAttributes
        )
        this.descriptions = response.map(d => ({
          description: d.description,
          value: d.description
        }))
      } catch (error) {
        console.error('Error loading descriptions:', error)
      }
    }
  }
}
</script>