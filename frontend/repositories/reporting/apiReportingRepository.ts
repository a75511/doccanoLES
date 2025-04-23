import ApiService from '@/services/api.service'
import { DisagreementStatistics } from '@/domain/models/reporting/reporting'

export class APIReportingRepository {
  constructor(private readonly request = ApiService) {}

  async getDisagreementStatistics(
    projectId: string,
    filters: {
      members?: number[],
      attributes?: string[]
    } = {}
  ): Promise<DisagreementStatistics> {
    const params = new URLSearchParams()
    
    if (filters.members?.length) {
      filters.members.forEach(member => 
        params.append('members', member.toString()))
    }
    
    if (filters.attributes?.length) {
      filters.attributes.forEach(attr => 
        params.append('attributes', attr))
    }

    const response = await this.request.get(`/projects/${projectId}/reporting/disagreements-statistics?${params}`) as {
      data: {
        total_examples: number,
        conflict_count: number,
        attribute_distributions: {
          attribute: string,
          total_members: number,
          data: {
            value: string,
            count: number
          }[];
        }[];
      }
    }

    return response.data
  }
}