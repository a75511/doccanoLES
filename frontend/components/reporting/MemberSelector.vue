<template>
  <v-select
    :value="value"
    :items="members"
    label="Select Members"
    multiple
    chips
    item-text="username"
    item-value="id"
    @input="$emit('input', $event)"
  />
</template>

<script>
export default {
  props: {
    projectId: { type: String, required: true },
    value: { type: Array, required: true } // v-model binds here
  },
  data() {
    return { members: [] }
  },
  async fetch() {
    this.members = await this.$repositories.member.list(this.projectId)
  }
}
</script>