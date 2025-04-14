import { ExampleItem } from '../example/example'
import { MemberItem } from '../member/member'

export interface AnnotationComparison {
  example: ExampleItem
  member1: {
    annotations: any[]
  }
  member2: {
    annotations: any[]
  }
  hasConflict: boolean
}

export interface ComparisonResponse {
  project_id: number
  project_name: string
  member1: MemberItem
  member2: MemberItem
  total_compared: number
  conflicts: AnnotationComparison[]
  examples: ExampleItem[]
  conflict_count: number
}