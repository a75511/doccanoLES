import { APIReportingRepository } from '~/repositories/reporting/apiReportingRepository'
import { DisagreementStatistics } from '~/domain/models/reporting/reporting'

export class ReportingApplicationService {
  constructor(private readonly repository: APIReportingRepository) {}

  async getDisagreementStatistics(
    projectId: string,
    filters: {
      attributes?: string[],
      labelDescriptions?: string[],
      view?: string
    } = {}
  ): Promise<DisagreementStatistics> {
    try {
      return await this.repository.getDisagreementStatistics(projectId, filters)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(`Failed to get statistics: ${e.message}`)
    }
  }

  async getAttributeDescriptions(
    projectId: string,
    attributes: string[],
  ): Promise<{ [key: string]: number }> {
    try {
      return await this.repository.getAttributeDescriptions(projectId, attributes)
    } catch (e: any) {
      if (e.response?.status === 500) {
        throw e
      }
      throw new Error(`Failed to get attribute descriptions: ${e.message}`)
    }
  }
}