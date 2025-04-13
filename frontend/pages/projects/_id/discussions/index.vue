<template>
    <div>
      <v-card>
        <v-card-title>
          {{ discussion.title }}
          <v-chip small color="green" class="ml-2">Active Discussion</v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-alert v-if="successMessage" type="success" class="mb-4">
            {{ successMessage }}
          </v-alert>
          <v-alert v-if="errorMessage" type="error" class="mb-4">
            {{ errorMessage }}
          </v-alert>
  
          <p>{{ discussion.description }}</p>
          
          <v-divider class="my-4"></v-divider>
          
          <h3 class="headline mb-4">Comments</h3>
          
          <v-list>
            <v-list-item
              v-for="comment in comments"
              :key="comment.id"
            >
              <v-list-item-avatar>
                <v-icon>mdi-account-circle</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ comment.username }}</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(comment.createdAt) }}</v-list-item-subtitle>
                <div class="comment-text">{{ comment.text }}</div>
              </v-list-item-content>
            </v-list-item>
          </v-list>
  
          <v-textarea
            v-model="newComment"
            label="Add your comment"
            outlined
            rows="2"
            class="mt-4"
          ></v-textarea>
          <v-btn 
            color="primary" 
            @click="addComment"
            :disabled="!newComment.trim()"
            :loading="isPosting"
          >
            Post Comment
          </v-btn>
        </v-card-text>
      </v-card>
    </div>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { DiscussionItem, DiscussionCommentItem } from '@/domain/models/discussion/discussion'
  
  export default Vue.extend({
    layout: 'project',
    middleware: ['check-auth', 'auth', 'set-project'],
  
    data() {
      return {
        discussion: {} as DiscussionItem,
        comments: [] as DiscussionCommentItem[],
        newComment: '',
        isPosting: false,
        pollInterval: null as NodeJS.Timeout | null,
        successMessage: '',
        errorMessage: ''
      }
    },
  
    async fetch() {
      await this.loadDiscussion()
      await this.loadComments()
    },
  
    mounted() {
      this.pollInterval = setInterval(this.loadComments, 5000)
    },
  
    beforeDestroy() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
      }
    },
  
    methods: {
      async loadDiscussion() {
        try {
          this.discussion =
           await this.$services.discussion.getActiveDiscussion(this.$route.params.id)
          this.errorMessage = ''
        } catch (error: any) {
          console.error('Error fetching discussion:', error)
          if (error.response?.data?.error) {
            this.errorMessage = error.response.data.error
          } else if (error.response?.data?.detail) {
            this.errorMessage = error.response.data.detail
          } else if (error instanceof Error) {
            this.errorMessage = error.message
          } else {
            this.errorMessage = 'Failed to load discussion. Please try again.'
          }
          
          setTimeout(() => {
            this.errorMessage = ''
          }, 3000)
        }
      },
  
      async loadComments() {
        try {
          const comments = await this.$services.discussion.getComments(this.$route.params.id)
          this.comments = comments
          this.errorMessage = ''
        } catch (error: any) {
          console.error('Error fetching comments:', error)
          if (error.response?.data?.error) {
            this.errorMessage = error.response.data.error
          } else if (error.response?.data?.detail) {
            this.errorMessage = error.response.data.detail
          } else if (error instanceof Error) {
            this.errorMessage = error.message
          } else {
            this.errorMessage = 'Failed to load comments. Please try again.'
          }
          
          setTimeout(() => {
            this.errorMessage = ''
          }, 3000)
        }
      },
  
      formatDate(dateString: string) {
        return new Date(dateString).toLocaleString()
      },
  
      async addComment() {
        if (!this.newComment.trim()) return
  
        this.isPosting = true
        try {
          const comment = await this.$services.discussion.addComment(
            this.$route.params.id,
            this.newComment
          )
          // Add the new comment to the beginning of the array
          this.comments.unshift(comment)
          this.newComment = ''
          this.successMessage = 'Comment posted successfully'
          this.errorMessage = ''
          
          setTimeout(() => {
            this.successMessage = ''
          }, 3000)
        } catch (error: any) {
          console.error('Error posting comment:', error)
          if (error.response?.data?.error) {
            this.errorMessage = error.response.data.error
          } else if (error.response?.data?.detail) {
            this.errorMessage = error.response.data.detail
          } else if (error instanceof Error) {
            this.errorMessage = error.message
          } else {
            this.errorMessage = 'Failed to post comment. Please try again.'
          }
        } finally {
          this.isPosting = false
          
          setTimeout(() => {
            this.errorMessage = ''
          }, 3000)
        }
      }
    }
  })
  </script>