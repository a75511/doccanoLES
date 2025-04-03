import ApiService from '@/services/api.service'
import { DisagreementAnalysisSummary } from '@/domain/models/example/disagreement'
import { SearchQueryData } from '~/services/application/project/projectApplicationService'

export class APIAnalysisRepository {
  constructor(private readonly request = ApiService) {}

  async listDisagreements(
    projectId: string,
    query: SearchQueryData,
    threshold: number
  ): Promise<DisagreementAnalysisSummary> { // Change return type
    const url = `/projects/${projectId}/disagreements/auto_analyze`;
    const params = {
      ...query,
      threshold
    };
    try {
      const response = await this.request.get(url, { params });
      return this.createDisagreementAnalysisFromResponse(response.data);
    } catch (error) {
      throw new Error(this.parseError(error));
    }
  }

  private parseError(error: any): string {
    if (error.response) {
      return error.response.data.detail || 'Failed to fetch disagreements'
    }
    return 'Network error occurred'
  }

  private createDisagreementAnalysisFromResponse(data: any): DisagreementAnalysisSummary {
    return new DisagreementAnalysisSummary(
      data.project_id,
      data.project_name,
      data.total_examples_analyzed,
      data.examples_with_disagreements,
      data.threshold,
      data.disagreements.map((d: any) => ({
        example_id: d.example_id,
        example_text: d.example_text,
        total_annotators: d.total_annotators,
        conflicting_pairs: d.conflicting_pairs,
        total_pairs: d.total_pairs,
        disagreement_percentage: d.disagreement_percentage * 100, // Convert to percentage if needed
        conflicts: d.conflicts,
        threshold_used: d.threshold_used
      }))
    );
  }
}