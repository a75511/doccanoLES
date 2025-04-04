<template>
    <v-text-field
      v-model="lastName"
      label="Last Name"
      outlined
      required
    />
  </template>
  
  <script lang="ts">
  import Vue from "vue";
  
  export default Vue.extend({
    props: {
      value: {
        type: String,
        required: true,
      },
    },
    computed: {
      lastName: {
        get(): string {
          return this.value;
        },
        set(newValue: string): void {
          this.$emit("input", newValue);
        },
      },
    },
  });
  </script>