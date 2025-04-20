import { APIReportingRepository } from '~/repositories/reporting/apiReportingRepository'
import { DisagreementStatistics } from '~/domain/models/reporting/reporting'

export class ReportingApplicationService {
  constructor(private readonly repository: APIReportingRepository) {}

  async getDisagreementStatistics(
    projectId: string,
    filters: {
      members?: number[],
      attributes?: string[]
    } = {}
  ): Promise<DisagreementStatistics> {
    try {
      return await this.repository.getDisagreementStatistics(projectId, filters)
    } catch (e: any) {
      throw new Error(`Failed to get statistics: ${e.message}`)
    }
  }
}