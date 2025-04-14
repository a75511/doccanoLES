import ApiService from '@/services/api.service'
import { ComparisonResponse } from '@/domain/models/disagreement/disagreement'
import { ExampleItem } from '~/domain/models/example/example'
import { MemberItem } from '~/domain/models/member/member'

export class APIDisagreementRepository {
  constructor(private readonly request = ApiService) {}

  async compare(
    projectId: string,
    member1Id: number,
    member2Id: number,
    searchQuery?: string
  ): Promise<ComparisonResponse> {
    const url = `/projects/${projectId}/disagreements/compare`
    const params: any = { member1: member1Id, member2: member2Id }
    
    if (searchQuery) params.q = searchQuery
    
    const response = await this.request.get(url, { params })

    const examples = response.data.conflicts.map((conflict: any) => 
      new ExampleItem(
        conflict.example.id,
        conflict.example.text,
        conflict.example.meta,
        conflict.example.annotation_approver,
        conflict.example.comment_count,
        conflict.example.file_url,
        conflict.example.is_confirmed,
        conflict.example.filename,
        conflict.example.assignments || []
      )
    )

    return {
      project_id: response.data.project_id,
      project_name: response.data.project_name,
      member1: new MemberItem(
        response.data.member1.id,
        response.data.member1.user_id,
        response.data.member1.role_id,
        response.data.member1.username,
        response.data.member1.rolename
      ),
      member2: new MemberItem(
        response.data.member2.id,
        response.data.member2.user_id,
        response.data.member2.role_id,
        response.data.member2.username,
        response.data.member2.rolename
      ),
      total_compared: response.data.total_compared,
      conflicts: response.data.conflicts.map((conflict: any) => ({
        example: new ExampleItem(
          conflict.example.id,
          conflict.example.text,
          conflict.example.meta,
          conflict.example.annotation_approver,
          conflict.example.comment_count,
          conflict.example.file_url,
          conflict.example.is_confirmed,
          conflict.example.filename,
          conflict.example.assignments || []
        ),
        member1: { annotations: conflict.member1.annotations || [] },
        member2: { annotations: conflict.member2.annotations || [] },
        hasConflict: conflict.hasConflict
      })),
      examples,
      conflict_count: response.data.conflict_count
    }
  }
}