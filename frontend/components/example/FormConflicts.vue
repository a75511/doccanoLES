<template>
    <v-dialog v-model="dialog" max-width="800" persistent>
      <v-card>
        <v-toolbar color="primary" dark flat>
          <v-toolbar-title>Compare Annotations</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="close">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedMember1"
                  :items="members"
                  item-text="username"
                  item-value="id"
                  label="First Annotator"
                  outlined
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedMember2"
                  :items="members"
                  item-text="username"
                  item-value="id"
                  label="Second Annotator"
                  outlined
                ></v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="close">Cancel</v-btn>
          <v-btn 
            color="primary" 
            :disabled="!canCompare"
            @click="compare"
          >
            Compare
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { MemberItem } from '~/domain/models/member/member'
  
  export default Vue.extend({
    props: {
      value: {
        type: Boolean,
        required: true
      },
      members: {
        type: Array as () => MemberItem[],
        required: true
      }
    },
  
    data() {
      return {
        selectedMember1: null as number | null,
        selectedMember2: null as number | null
      }
    },
  
    computed: {
      filteredMembers(): MemberItem[] {
        return this.members.filter(m => !m.isProjectAdmin)
      },
  
      dialog: {
        get(): boolean {
          return this.value
        },
        set(value: boolean) {
          this.$emit('input', value)
        }
      },
  
      canCompare(): boolean {
        return !!this.selectedMember1 && 
               !!this.selectedMember2 && 
               this.selectedMember1 !== this.selectedMember2
      }
    },
  
    methods: {
      compare() {
        if (this.canCompare) {
          this.$emit('compare', this.selectedMember1, this.selectedMember2)
        }
      },
  
      close() {
        this.dialog = false
      }
    }
  })
  </script>