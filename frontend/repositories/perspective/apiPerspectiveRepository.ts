import { Page } from '@/domain/models/page'
import { PerspectiveItem } from '@/domain/models/perspective/perspective'
import ApiService from '@/services/api.service'
import { PerspectiveAttributeItem } from '~/domain/models/perspective/perspectiveAttribute'
import { Project } from '@/domain/models/project/project'

const sortableFieldList = ['name', 'createdAt'] as const
type SortableFields = (typeof sortableFieldList)[number]

export class SearchQuery {
  readonly limit: number = 10
  readonly offset: number = 0
  readonly q: string = ''
  readonly sortBy: SortableFields = 'createdAt'
  readonly sortDesc: boolean = false

  constructor(_limit: string, _offset: string, _q?: string, _sortBy?: string, _sortDesc?: string) {
    this.limit = /^\d+$/.test(_limit) ? parseInt(_limit) : 10
    this.offset = /^\d+$/.test(_offset) ? parseInt(_offset) : 0
    this.q = _q || ''
    this.sortBy = (
      _sortBy && sortableFieldList.includes(_sortBy as SortableFields) ? _sortBy : 'createdAt'
    ) as SortableFields
    this.sortDesc = _sortDesc === 'true'
  }
}

function toModel(item: { [key: string]: any }): PerspectiveItem {
  return new PerspectiveItem(
    item.id,
    item.name,
    item.description,
    item.attributes.map((attr: any) =>
      PerspectiveAttributeItem.create(
        attr.id,
        attr.perspective_id,
        attr.name,
        attr.description
      )
    ),
    item.created_at,
  )
}

export class APIPerspectiveRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: string, query: SearchQuery): Promise<Page<PerspectiveItem>> {
    const fieldMapper = {
      name: 'name',
      createdAt: 'created_at',
    }
    const sortBy = fieldMapper[query.sortBy]
    const ordering = query.sortDesc ? `-${sortBy}` : `${sortBy}`
    const url = `/projects/${projectId}/perspectives?limit=${query.limit}&offset=${query.offset}&q=${query.q}&ordering=${ordering}`
    const response = await this.request.get(url)
    return new Page(
      response.data.count,
      response.data.next,
      response.data.previous,
      response.data.results.map((perspective: any) => toModel(perspective))
    )
  }

  async assignToProject(projectId: string, perspectiveId: number):
   Promise<{ data: { project: Project } }> {
    const url = `/projects/${projectId}/assign-perspective/${perspectiveId}`;
    return await this.request.post(url);
}
}