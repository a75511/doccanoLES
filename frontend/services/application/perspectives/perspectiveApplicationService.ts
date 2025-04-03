import { Page } from '~/domain/models/page'
import { PerspectiveItem } from '~/domain/models/perspective/perspective'
import { Project } from '~/domain/models/project/project'
import { APIPerspectiveRepository, SearchQuery } from '~/repositories/perspective/apiPerspectiveRepository'

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
      if (e.response?.status === 500) {
        throw e // Let the middleware handle database errors
      }
      throw new Error(e.response?.data?.detail || 'Failed to fetch perspectives.')
    }
  }

  public async assignToProject(projectId: string, perspectiveId: number):
   Promise<{ data: { project: Project } }> {
    try {
        const response = await this.repository.assignToProject(projectId, perspectiveId);
        return response;
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e // Let the middleware handle database errors
      }
      throw new Error(e.response?.data?.detail || 'Failed to fetch perspectives.')
    }
}

public async getPerspective(perspectiveId: number): Promise<{ data: PerspectiveItem }> {
  try {
    return await this.repository.getPerspective(perspectiveId)
  } catch (e: any) {
    throw new Error(e.response?.data?.detail || 'Failed to fetch perspective details.')
  }
}

public async getAttributesForPerspective(perspectiveId: number): Promise<{ data: any[] }> {
  try {
    return await this.repository.getAttributesForPerspective(perspectiveId)
  } catch (e: any) {
    throw new Error(e.response?.data?.detail || 'Failed to fetch perspective attributes.')
  }
}
}