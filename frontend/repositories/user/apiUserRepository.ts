import { UserItem } from '@/domain/models/user/user'
import ApiService from '@/services/api.service'

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(
    item.id,
    item.username,
    item.is_superuser,
    item.is_staff,
    item.email,
  )
}

export class APIUserRepository {
  constructor(private readonly request = ApiService) {}

  async getProfile(): Promise<UserItem> {
    const url = '/me'
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async list(query: string): Promise<UserItem[]> {
    const url = `/users?q=${query}`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async createUser(userData: { 
    username: string;
    email: string;
    is_staff?: boolean;
    is_superuser?: boolean;
  }): Promise<void> {
    const url = '/users/create';
    try {
      const response = await this.request.post(url, userData);
      return response.data;
    } catch (error) {
      console.error('Create User Error:', error);
      throw error;
    }
  }
}