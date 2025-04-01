import ApiService from '@/services/api.service'
import { ComparisonResponse, DisagreementItem, DisagreementItemList } from '@/domain/models/disagreement/disagreement'
import { ExampleItem } from '~/domain/models/example/example'
import { MemberItem } from '~/domain/models/member/member'

export class APIDisagreementRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: string): Promise<DisagreementItemList> {
    const url = `/projects/${projectId}/disagreements`
    const response = await this.request.get(url)
    return new DisagreementItemList(
      response.data.count,
      response.data.next,
      response.data.previous,
      response.data.results.map((item: any) => new DisagreementItem(
        item.id,
        new ExampleItem(
          item.example.id,
          item.example.text,
          item.example.meta,
          item.example.annotation_approver,
          item.example.comment_count,
          item.example.file_url,
          item.example.is_confirmed,
          item.example.filename,
          item.example.assignments
        ),
        item.members.map((member: any) => new MemberItem(
          member.id,
          member.user,
          member.role,
          member.username,
          member.rolename
        )),
        new Date(item.created_at),
        item.resolved
      ))
    )
  }

async compare(
  projectId: string, 
  member1Id: number, 
  member2Id: number
): Promise<ComparisonResponse> {
  const url = `/projects/${projectId}/disagreements/compare`
  const response = await this.request.get(url, {
    params: { 
      member1: member1Id, 
      member2: member2Id 
    }
  })
  
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
      member1: {
        annotations: conflict.member1.annotations || []
      },
      member2: {
        annotations: conflict.member2.annotations || []
      },
      differences: conflict.differences || []
    })),
    examples: response.data.examples.map((example: any) => new ExampleItem(
      example.id,
      example.text,
      example.meta,
      example.annotation_approver,
      example.comment_count,
      example.file_url,
      example.is_confirmed,
      example.filename,
      example.assignments || []
    )),
    conflict_count: response.data.conflict_count
  }
}

  async resolve(projectId: string, disagreementId: number): Promise<void> {
    const url = `/projects/${projectId}/disagreements/${disagreementId}`
    await this.request.patch(url, { resolved: true })
  }
}