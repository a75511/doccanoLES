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

export interface ConflictPair {
  user1: string
  user2: string
  details: Array<{
    type: string
    label?: string
    details: string
  }>
}

export interface ExampleDisagreement {
  example_id: number
  example_text: string | null
  total_annotators: number
  conflicting_pairs: number
  total_pairs: number
  disagreement_percentage: number
  conflicts: ConflictPair[]
  threshold_used: number
}

export class DisagreementAnalysisSummary {
  constructor(
    readonly project_id: number,
    readonly project_name: string,
    readonly total_examples_analyzed: number,
    readonly examples_with_disagreements: number,
    readonly threshold: number,
    readonly disagreements: ExampleDisagreement[]
  ) {}

  getDisagreementRate(): number {
    if (this.total_examples_analyzed === 0) return 0
    return (this.examples_with_disagreements / this.total_examples_analyzed) * 100
  }

  getMostControversialExamples(): ExampleDisagreement[] {
    return [...this.disagreements]
      .sort((a, b) => b.disagreement_percentage - a.disagreement_percentage)
      .slice(0, 5)
  }

  getUserParticipationStats(): { [username: string]: number } {
    const userCounts: { [username: string]: number } = {}

    this.disagreements.forEach(disagreement => {
      disagreement.conflicts.forEach(conflict => {
        userCounts[conflict.user1] = (userCounts[conflict.user1] || 0) + 1
        userCounts[conflict.user2] = (userCounts[conflict.user2] || 0) + 1
      })
    })

    return userCounts
  }
  
}