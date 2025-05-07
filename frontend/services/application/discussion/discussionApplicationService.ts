import { DiscussionItem, DiscussionCommentItem } from '@/domain/models/discussion/discussion'
import { APIDiscussionRepository } from '@/repositories/discussion/apiDiscussionRepository'
import { DiscussionCache } from "~/domain/models/discussion/discussionCache"

export class DiscussionApplicationService {
  private realTimeCallbacks: { [key: string]: Function[] } = {}

  constructor(
    private readonly repository: APIDiscussionRepository
  ) {
    this.repository.handleMessage = this.handleSocketMessage.bind(this)
  }

  on(event: string, callback: Function) {
    this.realTimeCallbacks[event] = this.realTimeCallbacks[event] || []
    this.realTimeCallbacks[event].push(callback)
  }

  off(event: string, callback: Function) {
    if (!this.realTimeCallbacks[event]) return
    this.realTimeCallbacks[event] = this.realTimeCallbacks[event]
      .filter(fn => fn !== callback)
  }

  private emit(event: string, data: any) {
    (this.realTimeCallbacks[event] || []).forEach(callback => callback(data))
  }

  private handleSocketMessage(action: string, data: any) {
    switch(action) {
      case 'create':
        this.emit('comment-created', data)
        break
      case 'update':
        this.emit('comment-updated', data)
        break
      case 'delete':
        this.emit('comment-deleted', data.id)
        break
    }
  }

  async getActiveDiscussion(projectId: string): Promise<DiscussionItem> {
    try {
      return await this.repository.getActiveDiscussion(projectId)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to fetch active discussion.');
    }
  }

  async getComments(projectId: string): Promise<DiscussionCommentItem[]> {
    try {
      const page = await this.repository.getComments(projectId)
      return page.items
    } catch (error: any) {
      if (error.response?.status === 500) {
        throw error
      } else if (navigator.onLine) {
        throw new Error('Failed to load comments. Please try again.')
      } else {
        return DiscussionCache.getCachedComments(projectId)
      }
    }
  }

  async addComment(projectId: string, text: string): Promise<DiscussionCommentItem> {
    try {
      const comment = await this.repository.addComment(projectId, text)
      this.repository.sendSocketMessage('create', comment)
      return comment
    } catch (error: any) {
      if (error.response?.status === 500) {
        throw error
      } else if (navigator.onLine) {
        throw new Error(error.response?.data?.detail || 'Failed to post comment')
      } else {
        throw new Error('Comment saved locally and will sync when online')
      }
    }
  }

  async updateComment(projectId: string, commentId: number, text: string):
   Promise<DiscussionCommentItem> {
    try {
      const comment = await this.repository.updateComment(projectId, commentId, text)
      this.repository.sendSocketMessage('update', comment)
      return comment
    } catch (error: any) {
      if (error.response?.status === 500) {
        throw error
      } else if (navigator.onLine) {
        throw new Error(error.response?.data?.detail || 'Failed to update comment')
      } else {
        throw new Error('Update saved locally and will sync when online')
      }
    }
  }
  
  async deleteComment(projectId: string, commentId: number): Promise<void> {
    try {
      await this.repository.deleteComment(projectId, commentId)
      this.repository.sendSocketMessage('delete',
         { id: commentId, text: '', member: 0, username: '', createdAt: '', updatedAt: '' });
    } catch (error: any) {
      if (error.response?.status === 500) {
        throw error
      } else if (navigator.onLine) {
        throw new Error(error.response?.data?.detail || 'Failed to delete comment')
      } else {
        throw new Error('Deletion saved locally and will sync when online')
      }
    }
  }

  async syncCache(projectId: string): Promise<void> {
    try {
      await DiscussionCache.processCache(projectId, this.repository)
    } catch (error) {
      throw new Error('Failed to sync offline changes')
    }
  }
}