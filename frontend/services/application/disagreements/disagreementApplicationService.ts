import { APIDisagreementRepository } from '~/repositories/disagreement/apiDisagreementRepository'
import { DisagreementItemList } from '~/domain/models/disagreement/disagreement'
import { ExampleItem } from '~/domain/models/example/example'
import { MemberItem } from '~/domain/models/member/member'

interface AnnotationDifference {
  type: string
  label: string
  details: string
}

interface AnnotationComparison {
  example: ExampleItem
  member1: {
    annotations: any[]
  }
  member2: {
    annotations: any[]
  }
  differences: AnnotationDifference[]
}

export class DisagreementApplicationService {
  constructor(private readonly repository: APIDisagreementRepository) {}

  public async list(projectId: string): Promise<DisagreementItemList> {
    return await this.repository.list(projectId)
  }

  public async compare(
    projectId: string, 
    member1Id: number, 
    member2Id: number
  ): Promise<{
    project_id: number
    project_name: string
    member1: MemberItem
    member2: MemberItem
    total_compared: number
    conflicts: AnnotationComparison[]
    conflict_count: number
  }> {
    return await this.repository.compare(projectId, member1Id, member2Id)
  }

  public async resolve(projectId: string, disagreementId: number): Promise<void> {
    await this.repository.resolve(projectId, disagreementId)
  }
}