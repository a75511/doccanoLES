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

  async startSession(projectId: string): Promise<DiscussionItem> {
    try {
        return await this.repository.startSession(projectId)
    } catch (error: any) {
        throw new Error(error.message || 'Failed to start session')
    }
  }

  async joinSession(projectId: string, sessionId: number): Promise<void> {
    try {
      await this.repository.joinSession(projectId, sessionId);
    } catch (error: any) {
      throw new Error(error.message || 'Failed to join session');
    }
  }

  async checkParticipation(projectId: string, sessionId: number): Promise<{ hasJoined: boolean }> {
    try {
      return await this.repository.checkParticipation(projectId, sessionId);
    } catch (error: any) {
      throw new Error(error.message || 'Failed to check participation');
    }
  }

  async closeSession(projectId: string, sessionId: number): Promise<any> {
    try {
      const response = await this.repository.closeSession(projectId, sessionId)
      
      // Handle pending closure response
      if (response.pending_closure) {
        return { pending_closure: true }
      }
      
      return response
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 400) {
        throw new Error('Session is already closed')
      } else if (error.response?.status === 500) {
        throw new Error('Failed to close session: ' + (error.response.data?.error || 'Internal server error'))
      }
      
      throw new Error(error.message || 'Failed to close session')
    }
  }

  async cancelClosure(projectId: string, sessionId: number): Promise<void> {
    try {
      await this.repository.cancelClosure(projectId, sessionId)
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error('No pending closure')
      } else if (error.response?.status === 500) {
        throw new Error('Failed to cancel closure: ' + (error.response.data?.error || 'Internal server error'))
      }
      
      throw new Error(error.message || 'Failed to cancel closure')
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