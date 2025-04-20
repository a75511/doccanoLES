import { Page } from '@/domain/models/page'
import ApiService from '@/services/api.service'
import { DiscussionItem, DiscussionCommentItem } from "~/domain/models/discussion/discussion"

function toDiscussionModel(item: any): DiscussionItem {
  return new DiscussionItem(
    item.id,
    item.project,
    item.title,
    item.description,
    item.is_active,
    item.created_at,
    item.comments?.map(toCommentModel) || []
  )
}

function toCommentModel(item: any): DiscussionCommentItem {
  return new DiscussionCommentItem(
    item.id,
    item.text,
    item.member,
    item.username,
    item.created_at,
    item.updated_at
  )
}

export class APIDiscussionRepository {
  constructor(private readonly request = ApiService) {}

  async getActiveDiscussion(projectId: string): Promise<DiscussionItem> {
    const url = `/projects/${projectId}/discussion`
    const response = await this.request.get(url)
    return toDiscussionModel(response.data)
  }

  async getComments(projectId: string): Promise<Page<DiscussionCommentItem>> {
    const url = `/projects/${projectId}/discussion/comments`
    const response = await this.request.get(url)
    return new Page(
      response.data.count,
      response.data.next,
      response.data.previous,
      response.data.results.map(toCommentModel)
    )
  }

  async addComment(projectId: string, text: string): Promise<DiscussionCommentItem> {
    const url = `/projects/${projectId}/discussion/comments`
    const response = await this.request.post(url, { text })
    return toCommentModel(response.data)
  }

  async updateComment(projectId: string, commentId: number,
     text: string): Promise<DiscussionCommentItem> {
    const url = `/projects/${projectId}/discussion/comments/${commentId}`
    const response = await this.request.put(url, { text })
    return toCommentModel(response.data)
  }
  
  async deleteComment(projectId: string, commentId: number): Promise<void> {
    const url = `/projects/${projectId}/discussion/comments/${commentId}`
    await this.request.delete(url)
  }
}