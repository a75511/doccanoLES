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
        conflict_percentage: number,
        attribute_distributions: {
          [x: string]: any
          attribute: string,
          total_members: number,
          data: {
            value: string,
            count: number,
            percentage: number
          }[];
        };
      }
    }

    return {
      total_examples: response.data.total_examples,
      conflict_percentage: response.data.conflict_percentage,
      attribute_distributions: response.data.attribute_distributions.map((attr:
         { attribute: any; total_members: any; data: any[] }) => ({
        attribute: attr.attribute,
        total_members: attr.total_members,
        data: attr.data.map((item: { value: any; count: any; percentage: any }) => ({
          value: item.value,
          count: item.count,
          percentage: item.percentage
        }))
      }))
    }
  }
}