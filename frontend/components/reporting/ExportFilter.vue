<template>
  <v-select
    :value="value"
    :items="formats"
    label="Export Formats"
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
    value: Array,
  },
  data() {
    return {
      formats: [
        { text: 'CSV', value: 'csv' },
        { text: 'PDF', value: 'pdf' },
        { text: 'Preview', value: 'preview' },
      ],
    };
  },
};
</script>