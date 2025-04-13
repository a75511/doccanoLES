import { DiscussionItem, DiscussionCommentItem } from '@/domain/models/discussion/discussion'
import { APIDiscussionRepository } from '@/repositories/discussion/apiDiscussionRepository'

export class DiscussionApplicationService {
  constructor(private readonly repository: APIDiscussionRepository) {}

  async getActiveDiscussion(projectId: string): Promise<DiscussionItem> {
    return await this.repository.getActiveDiscussion(projectId)
  }

  async getComments(projectId: string): Promise<DiscussionCommentItem[]> {
    const page = await this.repository.getComments(projectId)
    return page.items
  }

  async addComment(projectId: string, text: string): Promise<DiscussionCommentItem> {
    return await this.repository.addComment(projectId, text)
  }
}