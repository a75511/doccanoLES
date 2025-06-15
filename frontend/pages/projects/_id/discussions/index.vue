<template>
  <div>
    <v-card class="discussion-card">
      <v-card-title>
        {{ discussion.title }}
        <v-chip small color="green" class="ml-2">Active Discussion</v-chip>
      
      <v-spacer></v-spacer>

      <v-btn 
          v-if="isAdmin"
          color="error"
          small
          @click="closeSession"
        >
          Close Session
        </v-btn>
      </v-card-title>
      
      <v-card-text class="card-content">
        <v-alert v-if="successMessage" type="success" class="mb-4">
          {{ successMessage }}
        </v-alert>
        <v-alert v-if="errorMessage" type="error" class="mb-4">
          {{ errorMessage }}
        </v-alert>

        <p>{{ discussion.description }}</p>
        
        <v-divider class="my-4"></v-divider>
        
        <h3 class="headline mb-4">Comments</h3>

        <v-dialog v-model="showDeleteDialog" max-width="400">
          <v-card>
            <v-card-title class="headline">Delete Comment</v-card-title>
            <v-card-text>
              Are you sure you want to delete this comment?
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey" text @click="showDeleteDialog = false">
                Cancel
              </v-btn>
              <v-btn color="error" text @click="confirmDelete">
                Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <div class="comments-container">
          <v-list class="comments-list">
            <v-list-item
              v-for="comment in sortedComments"
              :key="comment.id"
              class="comment-item"
            >
            <v-chip v-if="comment.temp_id" small color="grey" class="mr-2">
              Offline
            </v-chip>
            <v-list-item-avatar>
              <div 
                class="member-avatar"
                :style="{ 
                  backgroundColor: $generateColor(comment.username),
                  color: $contrastColor($generateColor(comment.username))
                }"
              >
                {{ comment.username.charAt(0).toUpperCase() }}
              </div>
            </v-list-item-avatar>
              <v-list-item-content class="py-2">
                <div class="d-flex align-center">
                  <span 
                    class="username font-weight-medium"
                    :style="{ color: $generateColor(comment.username) }"
                  >
                    {{ comment.username }}
                  </span>
                  <span class="timestamp mx-2">•</span>
                  <span class="timestamp text-caption">
                    {{ formatDate(comment.createdAt) }}
                    <span v-if="comment.createdAt !== comment.updatedAt" class="edited-label">
                      (edited)
                    </span>
                  </span>
                  <v-icon 
                    v-if="comment.createdAt !== comment.updatedAt" 
                    small 
                    class="ml-1"
                    :title="formatDate(comment.updatedAt)"
                  >
                    {{ mdiPencil }}
                  </v-icon>
                </div>
                
                <div class="comment-content">
                  <div 
                    v-if="editingCommentId !== comment.id" 
                    class="comment-text mt-1"
                  >
                    {{ comment.text }}
                  </div>
                  <v-textarea
                    v-else
                    v-model="editText"
                    outlined
                    rows="2"
                    auto-grow
                    class="mt-1"
                  ></v-textarea>
                </div>
              </v-list-item-content>
              <v-list-item-action v-if="isCommentAuthor(comment)" class="actions">
                <div class="d-flex align-center" style="gap: 4px">
                  <v-btn
                    v-if="editingCommentId !== comment.id"
                    icon
                    x-small
                    @click="startEdit(comment)"
                  >
                    <v-icon x-small>{{ mdiPencil }}</v-icon>
                  </v-btn>
                  <v-btn
                    v-else
                    icon
                    x-small
                    color="primary"
                    @click="saveEdit(comment)"
                  >
                    <v-icon x-small>{{ mdiCheck }}</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    x-small
                    @click="deleteComment(comment)"
                  >
                    <v-icon x-small>{{ mdiDelete }}</v-icon>
                  </v-btn>
                </div>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </div>

        <div class="comment-input">
          <v-textarea
            v-model="newComment"
            label="Add your comment"
            outlined
            rows="2"
            class="mt-4"
          ></v-textarea>
          <v-btn 
            color="primary" 
            :disabled="!newComment.trim()"
            :loading="isPosting"
            @click="addComment"
          >
            Post Comment
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiPencil, mdiDelete, mdiCheck } from '@mdi/js'
import { DiscussionItem, DiscussionCommentItem } from '@/domain/models/discussion/discussion'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'discussion'],

  data() {
    return {
      discussion: {} as DiscussionItem,
      comments: [] as DiscussionCommentItem[],
      newComment: '',
      currentMemberId: null as number | null,
      editingCommentId: null as number | null,
      editText: '',
      isPosting: false,
      showDeleteDialog: false,
      commentToDelete: null as DiscussionCommentItem | null,
      currentRole: '',
      successMessage: '',
      errorMessage: '',
      mdiPencil,
      mdiDelete,
      mdiCheck,
      isOffline: !navigator.onLine,
      networkCheckInterval: null as number|null,
      scrollPosition: 0,
    }
  },

  async fetch() {
    await this.loadDiscussion()
    await this.loadComments()
    await this.loadCurrentMember()
  },

  computed: {
    sortedComments(): DiscussionCommentItem[] {
      return [...this.comments].sort((a, b) => 
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      )
    },

    isAdmin() {
      return this.currentRole === 'project_admin';
    },
  },

  async created() {
    await this.loadCurrentRole();
  },

  mounted() {
    this.setupRealtimeListeners()
    window.addEventListener('online', this.handleOnlineStatus)
    this.networkCheckInterval = window.setInterval(() => {
      this.checkNetworkStatus()
    }, 1000) as unknown as number
  },

  beforeDestroy() {
    window.removeEventListener('online', this.handleOnlineStatus)
    this.$services.discussion.off('comment-created', this.handleNewComment)
    this.$services.discussion.off('comment-updated', this.handleUpdatedComment)
    this.$services.discussion.off('comment-deleted', this.handleDeletedComment)
    this.$services.discussion.off('cache-error', this.handleCacheError)
    if (this.networkCheckInterval) {
      clearInterval(this.networkCheckInterval)
    }
  },

  methods: {
    async loadCurrentRole() {
      try {
        const role = await this.$repositories.member.fetchMyRole(this.$route.params.id);
        this.currentRole = role.rolename;
      } catch (error) {
        console.error('Failed to load current role:', error);
      }
    },
    async closeSession() {
      try {
        const response = await this.$services.discussion.closeSession(
          this.$route.params.id,
          this.discussion.id
        )
        if (response.pending_closure) {
          this.$store.commit('discussion/setPendingClosure', true)
          this.successMessage = 'Session closure pending database connection'
        } else {
          this.$store.commit('discussion/SET_JOIN_STATUS', false)
          this.$store.commit('discussion/SET_ACTIVE_SESSION', null)
          this.$store.commit('discussion/SET_PENDING_CLOSURE', false)
          this.$store.commit('discussion/SET_VOTING_STATUS', true)
          this.successMessage = 'Session closed successfully'
          if(this.isAdmin)
          {
            setTimeout(() => {
              this.$router.push(`/projects/${this.$route.params.id}/voting`)
            }, 2000)
          } else {
            setTimeout(() => {
            this.$router.push(`/projects/${this.$route.params.id}`)
          }, 2000)
          }
        }
      } catch (error) {
        this.handleError(error, 'close session')
      }
    },
    checkNetworkStatus() {
      const wasOffline = this.isOffline
      this.isOffline = !navigator.onLine
      
      // Only show message on state change
      if (wasOffline !== this.isOffline) {
        if (!this.isOffline) {
          this.handleOnlineStatus()
        }
      }
    },

    setupRealtimeListeners() {
      this.$services.discussion.on('comment-created', this.handleNewComment)
      this.$services.discussion.on('comment-updated', this.handleUpdatedComment)
      this.$services.discussion.on('comment-deleted', this.handleDeletedComment)
      this.$services.discussion.on('cache-error', this.handleCacheError)
    },
    handleNewComment(comment: DiscussionCommentItem) {
      // Check if temp comment exists
      const tempIndex = this.comments.findIndex(c => c.temp_id === comment.temp_id)
      if (tempIndex >= 0) {
        // Replace temp comment with real one
        this.comments.splice(tempIndex, 1, comment)
      } else {
        // Add new comment
        this.comments = [comment, ...this.comments]
      }
    },

    handleUpdatedComment(updatedComment: DiscussionCommentItem) {
      const index = this.comments.findIndex(c => c.id === updatedComment.id)
      if (index >= 0) {
        this.comments.splice(index, 1, updatedComment)
      }
    },

    handleDeletedComment(commentId: number) {
      this.comments = this.comments.filter(c => c.id !== commentId)
    },

    handleCacheError(error: Error) {
      this.errorMessage = `Sync failed: ${error.message}`
      setTimeout(() => { this.errorMessage = '' }, 5000)
    },

    async handleOnlineStatus() {
      try {
        await this.$services.discussion.syncCache(this.$route.params.id)
        await this.loadComments()
        this.successMessage = 'Offline changes synced successfully'
        setTimeout(() => { this.successMessage = '' }, 3000)
      } catch (error) {
        this.handleError(error, 'sync comments')
      }
    },

    handleError(error: any, context: string) {
      if (error.message.includes('offline') || error.message.includes('locally')) {
        this.errorMessage = `${error.message}`
      } else if (error.response?.data?.error) {
        this.errorMessage = error.response.data.error
      } else if (error.response?.data?.detail) {
        this.errorMessage = error.response.data.detail
      } else if (error instanceof Error) {
        this.errorMessage = error.message
      } else {
        this.errorMessage = `Failed to ${context}. Please try again.`
      }
      setTimeout(() => { this.errorMessage = '' }, 5000)
    },
    async loadDiscussion() {
      try {
        this.discussion = await this.$services.discussion.getActiveDiscussion(this.$route.params.id)
        this.errorMessage = ''
      } catch (error: any) {
        this.handleError(error, 'discussion')
      }
    },

    async loadComments() {
      try {
        const comments = await this.$services.discussion.getComments(this.$route.params.id)
        this.comments = comments.reverse()
        this.errorMessage = ''
      } catch (error: any) {
        this.handleError(error, 'comments')
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

        this.comments.push(comment)
        this.newComment = ''
        this.successMessage = 'Comment posted successfully'
        setTimeout(() => { this.successMessage = '' }, 3000)
      
        this.$nextTick(() => {
          const container = this.$el.querySelector('.comments-container')
          if (container) {
            container.scrollTop = container.scrollHeight
          }
        })
      } catch (error: any) {
        this.handleError(error, 'post comment')
      } finally {
        this.isPosting = false
        setTimeout(() => { this.errorMessage = '' }, 3000)
      }
    },

    async loadCurrentMember() {
      const role = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      this.currentMemberId = role.id
    },

    isCommentAuthor(comment: DiscussionCommentItem): boolean {
      return this.currentMemberId === comment.member
    },

    startEdit(comment: DiscussionCommentItem) {
      this.editingCommentId = comment.id
      this.editText = comment.text
    },

    async saveEdit(comment: DiscussionCommentItem) {
      if (this.editText.trim() === comment.text) {
        this.editingCommentId = null;
        return;
      }
      try {
        const updated = await this.$services.discussion.updateComment(
          this.$route.params.id,
          comment.id,
          this.editText
        )
        const index = this.comments.findIndex(c => c.id === comment.id)
        this.comments.splice(index, 1, updated)
        this.editingCommentId = null
        this.successMessage = 'Comment edited successfully'
        setTimeout(() => { this.successMessage = '' }, 3000)
      } catch (error) {
        this.handleError(error, 'edit comment')
      }
    },

    deleteComment(comment: DiscussionCommentItem) {
      this.commentToDelete = comment
      this.showDeleteDialog = true
    },

    async confirmDelete() {
      if (!this.commentToDelete) return
      
      try {
        await this.$services.discussion.deleteComment(
          this.$route.params.id,
          this.commentToDelete.id
        )
        this.comments = this.comments.filter(c => c.id !== this.commentToDelete!.id)
        this.successMessage = 'Comment deleted successfully'
        setTimeout(() => { this.successMessage = '' }, 3000)
      } catch (error) {
        this.handleError(error, 'delete comment')
      } finally {
        this.showDeleteDialog = false
        this.commentToDelete = null
      }
    },
  }
})
</script>

<style scoped>
.discussion-card {
  max-width: 600px;
  width: 100%;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-bottom: 0;
  overflow: hidden;
}

.comments-container {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 16px;
  padding: 8px 16px;
}

.comments-list {
  background: transparent;
  padding: 0;
}

.comment-input {
  flex-shrink: 0;
  padding-bottom: 16px;
  background: white;
  z-index: 1;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.username {
  font-size: 0.875rem;
  line-height: 1.25rem;
  transition: color 0.2s;
}

.timestamp {
  color: #888;
  font-size: 0.75rem;
}

.edited-label {
  color: #666;
  font-size: 0.75rem;
}

.comment-text {
  font-size: 0.875rem;
  line-height: 1.4;
  color: #333;
}

.actions {
  margin-left: auto;
  opacity: 0;
  transition: opacity 0.2s;
  position: absolute;
  right: 16px;
  top: 16px;
}

.comment-item:hover .actions {
  opacity: 1;
}

.v-list-item__action {
  margin-top: 0;
  align-self: flex-start;
  padding-left: 16px;
}
</style>