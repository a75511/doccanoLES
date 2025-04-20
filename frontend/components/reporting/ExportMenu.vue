<template>
    <v-menu offset-y>
      <template #activator="{ on, attrs }">
        <v-btn
          color="primary"
          dark
          v-bind="attrs"
          v-on="on"
        >
          <v-icon left>mdi-download</v-icon>
          Export
        </v-btn>
      </template>
  
      <v-list>
        <v-list-item @click="$emit('csv')">
          <v-list-item-icon>
            <v-icon>mdi-file-excel</v-icon>
          </v-list-item-icon>
          <v-list-item-title>CSV</v-list-item-title>
        </v-list-item>
  
        <v-list-item @click="$emit('pdf')">
          <v-list-item-icon>
            <v-icon>mdi-file-pdf</v-icon>
          </v-list-item-icon>
          <v-list-item-title>PDF</v-list-item-title>
        </v-list-item>
  
        <v-list-item @click="$emit('preview')">
          <v-list-item-icon>
            <v-icon>mdi-printer</v-icon>
          </v-list-item-icon>
          <v-list-item-title>Preview</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </template>
  
  <script>
  export default {
    name: 'ExportMenu',
    emits: ['csv', 'pdf', 'preview']
  }
  </script>
  
  <style scoped>
  .v-menu__content {
    z-index: 1000;
  }
  </style>