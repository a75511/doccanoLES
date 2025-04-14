import { APIDisagreementRepository } from '~/repositories/disagreement/apiDisagreementRepository'
import { ComparisonResponse } from '~/domain/models/disagreement/disagreement'

export class DisagreementApplicationService {
  constructor(private readonly repository: APIDisagreementRepository) {}

  public async compare(
    projectId: string, 
    member1Id: number, 
    member2Id: number,
    searchQuery?: string
  ): Promise<ComparisonResponse> {
    try {
      return await this.repository.compare(
        projectId, 
        member1Id, 
        member2Id,
        searchQuery
      )
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e // Let the middleware handle database errors
      }
      throw new Error(e.response?.data?.detail || 'Failed to compare annotations.')
    }
  }
}