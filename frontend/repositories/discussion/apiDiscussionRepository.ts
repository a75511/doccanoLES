import { Store } from 'vuex'
import { APIMemberRepository } from '../member/apiMemberRepository'
import { Page } from '@/domain/models/page'
import ApiService from '@/services/api.service'
import { DiscussionItem, DiscussionCommentItem } from "~/domain/models/discussion/discussion"
import { DiscussionCache } from "~/domain/models/discussion/discussionCache"
import { MemberItem } from '~/domain/models/member/member'

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
  private ws?: WebSocket
  private messageQueue: any[] = []
  private currentMember?: MemberItem
  private store: Store<any>

  constructor(
    private readonly request = ApiService,
    private readonly memberRepository: APIMemberRepository,
    store: Store<any>
  ) {
    this.store = store
    this.store.subscribe((mutation) => {
      if (mutation.type === 'setCurrent' || mutation.type === 'updateCurrentProjectPerspective') {
        this.reconnectWebSocket()
      }
    })
    this.reconnectWebSocket()
    this.loadCurrentMember()
  }

  private getProjectId(): string {
    return this.store.state.projects.current.id
  }

  private reconnectWebSocket() {
    if (this.ws) {
      this.ws.close()
    }
    const projectId = this.getProjectId()
    if (!projectId) {
      setTimeout(() => this.reconnectWebSocket(), 1000)
      return
    }

    this.initWebSocket(projectId)
    this.loadCurrentMember()
  }

  private initWebSocket(projectId: string) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    this.ws = new WebSocket(`${protocol}://${window.location.host}/ws/discussion/${projectId}/`)
    
    this.ws.onmessage = (event) => {
      const { action, data } = JSON.parse(event.data)
      this.handleMessage(action, data)
    }
  
    this.ws.onclose = () => {
      if (navigator.onLine) {
        setTimeout(() => this.initWebSocket(projectId), 5000)
      }
    }
  
    this.ws.onopen = () => {
      // Resend any queued messages
      while(this.messageQueue.length > 0) {
        const message = this.messageQueue.shift()
        this.ws?.send(JSON.stringify(message))
      }
      // Trigger cache sync
      DiscussionCache.processCache(projectId, this)
    }
  }

  private async loadCurrentMember() {
    const projectId = this.getProjectId()
    if (!projectId) return

    try {
      this.currentMember = await this.memberRepository.fetchMyRole(projectId)
    } catch (error) {
      console.error('Failed to load current member:', error)
    }
  }

  public sendSocketMessage(action: string, data: DiscussionCommentItem) {
      const message = JSON.stringify({ action, data: {
        ...data,
        temp_id: data.temp_id
      } 
    })
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(message)
    } else {
      this.messageQueue.push(message)
    }
  }

  public handleMessage(_action: string, _data: any) {
    // Override this in application service
  }

  async getActiveDiscussion(projectId: string): Promise<DiscussionItem> {
    try {
      const response = await this.request.get(`/projects/${projectId}/discussion`)
      return toDiscussionModel(response.data)
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('No active discussion found')
      }
      throw error
    }
  }

  async getComments(projectId: string): Promise<Page<DiscussionCommentItem>> {
    try {
      const response = await this.request.get(`/projects/${projectId}/discussion/comments`)
      const cached = await DiscussionCache.getCachedComments(projectId)
      return new Page(
        response.data.count + cached.length,
        response.data.next,
        response.data.previous,
        [...response.data.results.map(toCommentModel), ...cached]
      )
    } catch (error: any) {
      if (navigator.onLine) throw error
      const cached = await DiscussionCache.getCachedComments(projectId)
      return new Page(cached.length, null, null, cached)
    }
  }

  async addComment(projectId: string, text: string): Promise<DiscussionCommentItem> {
    if (!this.currentMember) {
      throw new Error('User not authenticated')
    }

    const tempComment = {
      id: -Date.now(), // Add negative temporary ID
      temp_id: Date.now(),
      text,
      member: this.currentMember.id,
      username: this.currentMember.username,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    if (navigator.onLine) {
      try {
        const response = await this.request.post(`/projects/${projectId}/discussion/comments`, { text })
        const comment = toCommentModel(response.data)
        this.sendSocketMessage('create', { 
          ...comment,
          temp_id: tempComment.temp_id
        })
        return comment
      } catch (error: any) {
        if (error.response?.status === 500) {
          throw error; // Prevent caching on DB errors
        }
        await DiscussionCache.cacheComment(projectId, tempComment)
        throw error
      }
    } else {
      await DiscussionCache.cacheComment(projectId, tempComment)
      return { ...tempComment, id: -Math.abs(tempComment.id) } as DiscussionCommentItem
    }
  }

  async updateComment(projectId: string, commentId: number, text: string):
   Promise<DiscussionCommentItem> {
    if (navigator.onLine) {
      try {
        const response = await this.request.put(`/projects/${projectId}/discussion/comments/${commentId}`, { text })
        return toCommentModel(response.data)
      } catch (error: any) {
        if (error.response?.status === 500) {
          throw error;
        }
        await DiscussionCache.cacheUpdate(projectId, { id: commentId, text })
        throw error
      }
    } else {
      const update = { id: commentId, text }
      await DiscussionCache.cacheUpdate(projectId, update)
      return { 
        id: commentId,
        text,
        member: this.currentMember?.id || 0,
        username: this.currentMember?.username || '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      } as DiscussionCommentItem
    }
  }
  
  async deleteComment(projectId: string, commentId: number): Promise<void> {
    if (navigator.onLine) {
      try {
        await this.request.delete(`/projects/${projectId}/discussion/comments/${commentId}`)
      } catch (error: any) {
        if (error.response?.status === 500) {
          throw error;
        }
        await DiscussionCache.cacheDeletion(projectId, commentId)
        throw error
      }
    } else {
      await DiscussionCache.cacheDeletion(projectId, commentId)
    }
  }
}