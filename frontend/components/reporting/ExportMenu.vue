<template>
  <v-menu offset-y>
    <template #activator="{ on, attrs }">
      <v-btn
        color="primary"
        dark
        v-bind="attrs"
        v-on="on"
      >
        <v-icon left>{{ icons.download }}</v-icon>
        Export
      </v-btn>
    </template>

    <v-list>
      <v-list-item @click.stop="toggleExport('csv')">
        <v-list-item-action>
          <v-checkbox
            v-model="selectedFormats"
            value="csv"
            hide-details
          ></v-checkbox>
        </v-list-item-action>
        <v-list-item-icon>
          <v-icon>{{ icons.excel }}</v-icon>
        </v-list-item-icon>
        <v-list-item-title>CSV</v-list-item-title>
      </v-list-item>

      <v-list-item @click.stop="toggleExport('pdf')">
        <v-list-item-action>
          <v-checkbox
            v-model="selectedFormats"
            value="pdf"
            hide-details
          ></v-checkbox>
        </v-list-item-action>
        <v-list-item-icon>
          <v-icon>{{ icons.pdf }}</v-icon>
        </v-list-item-icon>
        <v-list-item-title>PDF</v-list-item-title>
      </v-list-item>

      <v-list-item @click.stop="toggleExport('preview')">
        <v-list-item-action>
          <v-checkbox
            v-model="selectedFormats"
            value="preview"
            hide-details
          ></v-checkbox>
        </v-list-item-action>
        <v-list-item-icon>
          <v-icon>{{ icons.printer }}</v-icon>
        </v-list-item-icon>
        <v-list-item-title>Preview</v-list-item-title>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-item @click="exportSelected">
        <v-list-item-icon>
          <v-icon color="primary">{{ icons.download }}</v-icon>
        </v-list-item-icon>
        <v-list-item-title>Export Selected</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { mdiDownload, mdiFileExcel, mdiFilePdfBox, mdiPrinter } from '@mdi/js'

export default {
  name: 'ExportMenu',
  data() {
    return {
      selectedFormats: [],
      icons: {
        download: mdiDownload,
        excel: mdiFileExcel,
        pdf: mdiFilePdfBox,
        printer: mdiPrinter
      }
    }
  },
  methods: {
    toggleExport(format) {
      const index = this.selectedFormats.indexOf(format)
      if (index === -1) {
        this.selectedFormats.push(format)
      } else {
        this.selectedFormats.splice(index, 1)
      }
    },
    exportSelected() {
      if (this.selectedFormats.length === 0) {
        this.$emit('error', 'Please select at least one format')
        return
      }
      this.$emit('export', this.selectedFormats)
      this.selectedFormats = []
    }
  }
}
</script>

<style scoped>
.v-menu__content {
  z-index: 1000;
}
</style>