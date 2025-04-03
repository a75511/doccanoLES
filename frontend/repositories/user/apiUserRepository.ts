// ~/repositories/user/apiUserRepository.ts
import { Page } from '@/domain/models/page'
import { UserItem } from '@/domain/models/user/user'
import ApiService from '@/services/api.service'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

const userSortableFields = ['username', 'email'] as const
type UserSortableFields = (typeof userSortableFields)[number]

export class UserSearchQuery {
  readonly limit: number
  readonly offset: number
  readonly q: string
  readonly sortBy: UserSortableFields
  readonly sortDesc: boolean

  constructor(data: SearchQueryData) {
    this.limit = /^\d+$/.test(data.limit) ? parseInt(data.limit) : 10
    this.offset = /^\d+$/.test(data.offset) ? parseInt(data.offset) : 0
    this.q = data.q || ''
    this.sortDesc = data.sortDesc === 'true'
    
    this.sortBy = (
      data.sortBy && userSortableFields.includes(data.sortBy as UserSortableFields)
        ? data.sortBy : 'username'
    ) as UserSortableFields
  }
}

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(
    item.id,
    item.username,
    item.is_superuser,
    item.is_staff,
    item.email,
    item.sex,
    item.age
  )
}

// function toPayload(item: UserItem): { [key: string]: any } {
//   return {
//     username: item.username,
//     email: item.email,
//     is_staff: item.isStaff,
//     is_superuser: item.isSuperuser
//     // Add other fields as needed
//   }
// }

export class APIUserRepository {
  constructor(private readonly request = ApiService) {}

  async list(queryData: SearchQueryData): Promise<Page<UserItem>> {
    const query = new UserSearchQuery(queryData)
    const fieldMapper = {
      username: 'username',
      email: 'email'
    }
    const sortBy = fieldMapper[query.sortBy]
    const ordering = query.sortDesc ? `-${sortBy}` : sortBy
    const url = `/users?limit=${query.limit}&offset=${query.offset}&q=${query.q}&ordering=${ordering}`
    const response = await this.request.get(url)
    return new Page(
      response.data.count,
      response.data.next,
      response.data.previous,
      response.data.results.map(toModel)
    )
  }

  async findById(id: string): Promise<UserItem> {
    const url = `/users/${id}`
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async getProfile(): Promise<UserItem> {
    const url = '/me'
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  // async create(item: UserItem): Promise<UserItem> {
  //   const url = '/users'
  //   const payload = toPayload(item)
  //   const response = await this.request.post(url, payload)
  //   return toModel(response.data)
  // }

  // async update(item: UserItem): Promise<void> {
  //   const url = `/users/${item.id}`
  //   const payload = toPayload(item)
  //   await this.request.patch(url, payload)
  // }

  // async bulkDelete(userIds: number[]): Promise<void> {
  //   const url = '/users'
  //   await this.request.delete(url, { ids: userIds })
  // }

  // async updateRoles(userId: number, roles: string[]): Promise<void> {
  //   const url = `/users/${userId}/roles`
  //   await this.request.patch(url, { roles })
  // }
}