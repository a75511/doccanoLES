<template>
  <action-menu
    :items="menuItems"
    :text="$t('dataset.actions')"
    @create="$emit('create')"
    @upload="$emit('upload')"
    @download="$emit('download')"
    @assign="$emit('assign')"
    @reset="$emit('reset')"
    @conflicts="$emit('conflicts')"
    @lock="$emit('lock')"
    @unlock="$emit('unlock')"
  />
</template>

<script lang="ts">
import Vue from 'vue'
import { 
  mdiAccountCheck, 
  mdiUpload, 
  mdiDownload, 
  mdiUpdate,
  mdiAlertCircleOutline,
  mdiLock,
  mdiLockOpen 
} from '@mdi/js'
import ActionMenu from '~/components/utils/ActionMenu.vue'

export default Vue.extend({
  components: {
    ActionMenu
  },

  props: {
    isLocked: {
      type: Boolean,
      default: false
    }
  },

  computed: {
    menuItems() {
      const baseItems = [
        {
          title: this.$t('dataset.importDataset'),
          icon: mdiUpload,
          event: 'upload',
          disabled: this.isLocked
        },
        {
          title: this.$t('dataset.exportDataset'),
          icon: mdiDownload,
          event: 'download'
        },
        {
          title: 'Assign to member',
          icon: mdiAccountCheck,
          event: 'assign',
          disabled: this.isLocked
        },
        {
          title: 'Reset Assignment',
          icon: mdiUpdate,
          event: 'reset',
          disabled: this.isLocked
        },
        {
          title: 'Check conflicts',
          icon: mdiAlertCircleOutline,
          event: 'conflicts'
        }
      ]

      const lockItem = this.isLocked
        ? {
            title: 'Unlock Project',
            icon: mdiLockOpen,
            event: 'unlock'
          }
        : {
            title: 'Lock Project',
            icon: mdiLock,
            event: 'lock'
          }

      return [...baseItems, lockItem]
    }
  }
})
</script>