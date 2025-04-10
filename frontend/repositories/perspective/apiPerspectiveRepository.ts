import { Page } from '@/domain/models/page'
import { PerspectiveItem } from '@/domain/models/perspective/perspective'
import ApiService from '@/services/api.service'
import { PerspectiveAttributeItem, PerspectiveAttributeListOptionItem } from '@/domain/models/perspective/perspectiveAttribute'
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
        attr.type,
        attr.options ? attr.options.map((option: any) => option.value) : []
      )
    ),
    item.created_at,
    item.created_by
  )
}

export class APIPerspectiveRepository {
  constructor(private readonly request = ApiService) {}

  async findById(projectId: string, perspectiveId: number): Promise<PerspectiveItem> {
    const url = `/projects/${projectId}/perspectives/${perspectiveId}`;
    const response = await this.request.get(url);
    console.log(response.data)
    return toModel(response.data);
  }

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

async listAttributes(projectId: string, perspectiveId: number, query: SearchQuery):
 Promise<Page<PerspectiveAttributeItem>> {
  const fieldMapper = {
    name: 'name',
    type: 'type',
  };
  const sortBy = fieldMapper[query.sortBy as keyof typeof fieldMapper] || 'name';
  const ordering = query.sortDesc ? `-${sortBy}` : `${sortBy}`;
  
  const url = `/projects/${projectId}/perspectives/${perspectiveId}/attributes?limit=${query.limit}&offset=${query.offset}&q=${query.q}&ordering=${ordering}`;
  const response = await this.request.get(url);
  
  return new Page(
    response.data.count,
    response.data.next,
    response.data.previous,
    response.data.results.map((attr: any) => 
      new PerspectiveAttributeItem(
        attr.id,
        attr.perspective_id,
        attr.name,
        attr.type,
        attr.options.map((option: any) => 
          new PerspectiveAttributeListOptionItem(option.id, attr.id, option.value)
        ) || [],
      )
    )
  );
}

  async assignToProject(projectId: string, perspectiveId: number):
   Promise<{ data: { project: Project } }> {
    const url = `/projects/${projectId}/assign-perspective/${perspectiveId}`;
    return await this.request.post(url);
}

async create(
  projectId: string,
  name: string,
  description: string,
  attributes: { name: string; type: string; options?: { value: string }[] }[]
): Promise<PerspectiveItem> {
  const url = `/projects/${projectId}/perspectives/create`;
  const payload = {
    name,
    description,
    attributes,
  };
  
  try {
    const response = await this.request.post(url, payload);
    return toModel(response.data.perspective);
  } catch (error: any) {
    if (error.response) {
      const { data, status } = error.response;
      
      if (status === 400 && data.code === 'perspective_exists') {
        throw new Error(data.message);
      } else if (status === 503 && data.code === 'database_error') {
        throw new Error('Database is currently unavailable. Please try again later.');
      } else if (status === 400 && data.code === 'integrity_error') {
        throw new Error('Invalid data provided. Please check your input.');
      } else if (status >= 500) {
        throw new Error('Database is currently unavailable. Please try again later.');
      } else {
        throw new Error(data.message || 'Failed to create perspective.');
      }
    } else if (error.request) {
      throw new Error('Network error. Please check your internet connection.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
}
}
