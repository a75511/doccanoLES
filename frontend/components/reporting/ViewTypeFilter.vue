<template>
  <v-select
    :value="value"
    :items="viewTypes"
    label="Agreement/Disagreement Filter"
    item-text="text"
    item-value="value"
    clearable
    @input="$emit('input', $event)"
  />
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      default: 'all'
    }
  },
  data() {
    return {
      viewTypes: [
        { text: 'All Examples', value: 'all' },
        { text: 'Agreements Only', value: 'agreement' },
        { text: 'Disagreements Only', value: 'disagreement' }
      ]
    }
  }
}
</script>