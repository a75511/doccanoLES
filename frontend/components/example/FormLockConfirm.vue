<template>
    <confirm-form
      :title="isLocked ? $t('dataset.unlockTitle') : $t('dataser.lockTitle')"
      :message="isLocked ? $t('dataset.unlockMessage') : $t('dataset.lockMessage')"
      @ok="$emit('confirm')"
      @cancel="$emit('cancel')"
    />
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import ConfirmForm from '@/components/utils/ConfirmForm.vue'
  
  export default Vue.extend({
    components: {
      ConfirmForm
    },
  
    props: {
      isLocked: {
        type: Boolean,
        required: true
      }
    }
  })
  </script>