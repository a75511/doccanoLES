import { APIDisagreementRepository, APIAnalysisRepository } from '~/repositories/disagreement/apiDisagreementRepository'
import { ComparisonResponse, DisagreementAnalysisSummary } from '~/domain/models/disagreement/disagreement'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

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

export class AnalysisApplicationService {
  constructor(private readonly repository: APIAnalysisRepository) {}

  public async getDisagreementAnalysis(
    projectId: string,
    threshold: number,
    query?: SearchQueryData
  ): Promise<DisagreementAnalysisSummary> {
    try {
      return await this.repository.listDisagreements(
        projectId, 
        query || { limit: '100', offset: '0' },
        threshold
      );
    } catch (error: any) {
      throw new Error(error.message);
    }
  }
}