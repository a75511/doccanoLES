import { Page } from '@/domain/models/page'
import { PerspectiveItem } from '@/domain/models/perspective/perspective'
import { Project } from '@/domain/models/project/project'
import { APIPerspectiveRepository, SearchQuery } from '@/repositories/perspective/apiPerspectiveRepository'

export interface SearchQueryData {
  limit: string
  offset: string
  q?: string
  sortBy?: string
  sortDesc?: string
}

export class PerspectiveApplicationService {
  constructor(private readonly repository: APIPerspectiveRepository) {}

  public async list(projectId: string, query: SearchQueryData): Promise<Page<PerspectiveItem>> {
    try {
      const searchQuery = 
      new SearchQuery(query.limit, query.offset, query.q, query.sortBy, query.sortDesc)
      return await this.repository.list(projectId, searchQuery)
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to fetch perspectives.')
    }
  }

  public async assignToProject(projectId: string, perspectiveId: number):
   Promise<{ data: { project: Project } }> {
    try {
        const response = await this.repository.assignToProject(projectId, perspectiveId);
        return response;
    } catch (e: any) {
        throw new Error(e.response?.data?.detail || 'Failed to assign perspective to project.');
    }
  }
  
  public async create(
    projectId: string,
    name: string,
    description: string,
    attributes: { name: string; type: string; options?: { value: string }[] }[]
  ): Promise<PerspectiveItem> {
    return await this.repository.create(projectId, name, description, attributes);
  }
}
