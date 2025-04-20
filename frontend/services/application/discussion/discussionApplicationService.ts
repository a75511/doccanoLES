import { DiscussionItem, DiscussionCommentItem } from '@/domain/models/discussion/discussion'
import { APIDiscussionRepository } from '@/repositories/discussion/apiDiscussionRepository'

export class DiscussionApplicationService {
  constructor(private readonly repository: APIDiscussionRepository) {}

  async getActiveDiscussion(projectId: string): Promise<DiscussionItem> {
    try {
      return await this.repository.getActiveDiscussion(projectId)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to fetch active discussion.')
    }
  }

  async getComments(projectId: string): Promise<DiscussionCommentItem[]> {
    try {
      const page = await this.repository.getComments(projectId)
      return page.items
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to fetch comments.')
    }
  }

  async addComment(projectId: string, text: string): Promise<DiscussionCommentItem> {
    try {
      return await this.repository.addComment(projectId, text)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to add comment.')
    }
  }

  async updateComment(projectId: string, commentId: number,
     text: string): Promise<DiscussionCommentItem> {
    try {
      return await this.repository.updateComment(projectId, commentId, text)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to update comment.')
    }
  }
  
  async deleteComment(projectId: string, commentId: number): Promise<void> {
    try {
      await this.repository.deleteComment(projectId, commentId)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(e.response?.data?.detail || 'Failed to delete comment.')
    }
  }
}