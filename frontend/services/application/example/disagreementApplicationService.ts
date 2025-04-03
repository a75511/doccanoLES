// ~/services/application/analysis/analysisApplicationService.ts
import { APIAnalysisRepository } from '~/repositories/analysis/apiAnalysisRepository'
import { DisagreementAnalysisSummary } from '~/domain/models/example/disagreement'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

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