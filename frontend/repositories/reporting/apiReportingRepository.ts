import ApiService from '@/services/api.service'
import { DisagreementStatistics } from '@/domain/models/reporting/reporting'

export class APIReportingRepository {
  constructor(private readonly request = ApiService) {}

  async getDisagreementStatistics(
    projectId: string,
    filters: {
      attributes?: string[],
      descriptions?: string[],
      view?: string
    } = {}
  ): Promise<DisagreementStatistics> {
    const params = new URLSearchParams()
    
    if (filters.attributes?.length) {
      filters.attributes.forEach(attr => params.append('attributes', attr))
    }

    if (filters.descriptions?.length) {
      filters.descriptions.forEach(d => params.append('descriptions', d))
    }

    if (filters.view) {
      params.append('view', filters.view)
    }

    const response = await this.request.get(`/projects/${projectId}/reporting/disagreements?${params}`) as {
      data: DisagreementStatistics
    }
    return response.data
  }

  async getAttributeDescriptions(
    projectId: string,
    attributes: string[]
  ) {
    const params = new URLSearchParams();
    attributes.forEach(a => params.append('attributes', a));
    
    const response = await this.request.get(
      `/projects/${projectId}/attribute-descriptions`,
      { params }
    );
    return response.data.attribute_descriptions;
  }
}