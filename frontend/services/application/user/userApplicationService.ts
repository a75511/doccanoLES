import { APIUserRepository } from '~/repositories/user/apiUserRepository'
import { UserItem } from '~/domain/models/user/user'
import { Page } from '~/domain/models/page'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

export class UserApplicationService {
  constructor(private readonly repository: APIUserRepository) {}

  public async list(query: SearchQueryData): Promise<Page<UserItem>> {
    try {
      return await this.repository.list(query)
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to fetch users')
    }
  }

  public async searchUsers(username: string): Promise<UserItem[]> {
    try {
      const result = await this.repository.list({
        limit: '10',
        offset: '0',
        q: username
      })
      return result.items
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to search users')
    }
  }

  public async findById(id: string): Promise<UserItem> {
    try {
      return await this.repository.findById(id)
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'User not found')
    }
  }

  public async getProfile(): Promise<UserItem> {
    try {
      return await this.repository.getProfile()
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to fetch profile')
    }
  }
}