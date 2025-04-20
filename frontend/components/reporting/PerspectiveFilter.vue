<template>
  <v-select
    :value="value"
    :items="attributes"
    label="Filter by Perspective Attributes"
    multiple
    chips
    item-text="name"
    item-value="value"
    clearable
    @input="$emit('input', $event)"
  />
</template>

<script>
export default {
  props: {
    projectId: {
      type: String,
      required: true
    },
    value: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      attributes: []
    }
  },
  async fetch() {
    try {
      const project = await this.$services.project.findById(this.projectId)
      if (project.perspective) {
        this.attributes = project.perspective.attributes.map(attr => ({
          name: attr.name,
          value: attr.name // Use name as value for filtering
        }))
      }
    } catch (error) {
      console.error('Error loading perspective attributes:', error)
    }
  }
}
</script>