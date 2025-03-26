import { ExampleItem } from '../example/example'
import { MemberItem } from '../member/member'

export class DisagreementItem {
  constructor(
    readonly id: number,
    readonly example: ExampleItem,
    readonly members: MemberItem[],
    readonly created_at: Date,
    readonly resolved: boolean
  ) {}

  get memberNames(): string[] {
    return this.members.map(member => member.username)
  }
}

export class DisagreementItemList {
  constructor(
    readonly count: number,
    readonly next: string | null,
    readonly prev: string | null,
    readonly items: DisagreementItem[]
  ) {}
}

export interface AnnotationDifference {
  type: string
  label: string
  details: string
}

export interface AnnotationComparison {
  example: ExampleItem
  member1: {
    annotations: any[]
  }
  member2: {
    annotations: any[]
  }
  differences: AnnotationDifference[]
}