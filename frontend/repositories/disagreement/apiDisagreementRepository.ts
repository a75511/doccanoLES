import ApiService from '@/services/api.service'
import { DisagreementItem, DisagreementItemList } from '@/domain/models/disagreement/disagreement'
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
  ): Promise<{
    project_id: number
    project_name: string
    member1: MemberItem
    member2: MemberItem
    total_compared: number
    conflicts: Array<{
      example: ExampleItem
      member1: { annotations: any[] }
      member2: { annotations: any[] }
      differences: Array<{
        type: string
        label: string
        details: string
      }>
    }>
    conflict_count: number
  }> {
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
          null, // annotationApprover
          0,    // commentCount
          '',   // fileUrl
          false, // isConfirmed
          '',    // filename
          []     // assignments
        ),
        member1: {
          annotations: conflict.member1.annotations || []
        },
        member2: {
          annotations: conflict.member2.annotations || []
        },
        differences: conflict.differences || []
      })),
      conflict_count: response.data.conflict_count
    }
  }

  async resolve(projectId: string, disagreementId: number): Promise<void> {
    const url = `/projects/${projectId}/disagreements/${disagreementId}`
    await this.request.patch(url, { resolved: true })
  }
}