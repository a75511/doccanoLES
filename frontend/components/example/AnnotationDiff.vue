<template>
    <div class="annotation-diff">
      <div class="text-content" v-html="highlightedText"></div>
      
      <v-card v-if="hasAnnotations" class="mt-4">
        <v-card-title class="subtitle-1">Applied Labels</v-card-title>
        <v-card-text>
          <v-chip
            v-for="(annotation, index) in annotations"
            :key="index"
            small
            :color="getLabelColor(annotation)"
            class="mr-2 mb-2"
          >
            {{ annotation.label }}
            <v-icon v-if="isDifferentLabel(annotation)" small right>
              {{ userType === 'member1' ? 'mdi-arrow-left' : 'mdi-arrow-right' }}
            </v-icon>
          </v-chip>
        </v-card-text>
      </v-card>
    </div>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { AnnotationDifference } from '~/domain/models/disagreement/disagreement'
  
  interface Annotation {
    label: string
    text?: string
    [key: string]: any
  }
  
  export default Vue.extend({
    props: {
      original: {
        type: String,
        required: true
      },
      annotations: {
        type: Array as () => Annotation[],
        required: true
      },
      differences: {
        type: Array as () => AnnotationDifference[],
        default: () => []
      },
      userType: {
        type: String as () => 'member1' | 'member2',
        required: true
      }
    },
  
    computed: {
      hasAnnotations(): boolean {
        return this.annotations.length > 0
      },
  
      highlightedText(): string {
        let text = this.original
        
        // Highlight differences based on annotation spans
        this.annotations.forEach(annotation => {
          if (this.isDifferentLabel(annotation)) {
            const highlightClass = this.userType === 'member1' ? 'highlight-removed' : 'highlight-added'
            const annotationText = annotation.text || annotation.label
            text = text.replace(
              annotationText,
              `<span class="${highlightClass}">${annotationText}</span>`
            )
          }
        })
        
        return text || '<i>No text content</i>'
      }
    },
  
    methods: {
      getLabelColor(annotation: Annotation): string {
        if (this.isDifferentLabel(annotation)) {
          return this.userType === 'member1' ? 'error' : 'success'
        }
        return 'primary'
      },
  
      isDifferentLabel(annotation: Annotation): boolean {
        return this.differences.some(diff => 
          diff.label === annotation.label && 
          (diff.type.includes(this.userType === 'member1' ? 'missing_in_member2' : 'missing_in_member1'))
        )
      }
    }
  })
  </script>
  
  <style scoped>
  .text-content {
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
  }
  
  .highlight-added {
    background-color: rgba(76, 175, 80, 0.3);
    padding: 2px 0;
    border-bottom: 2px solid #4CAF50;
  }
  
  .highlight-removed {
    background-color: rgba(244, 67, 54, 0.3);
    padding: 2px 0;
    border-bottom: 2px dashed #F44336;
  }
  </style>