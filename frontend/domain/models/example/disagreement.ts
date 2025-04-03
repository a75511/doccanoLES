// ~/domain/models/analysis/disagreement.ts
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
  
    // Change from getter to a regular method
    getDisagreementRate(): number {
      if (this.total_examples_analyzed === 0) return 0
      return (this.examples_with_disagreements / this.total_examples_analyzed) * 100
    }
  
    // Change from getter to a regular method
    getMostControversialExamples(): ExampleDisagreement[] {
      return [...this.disagreements]
        .sort((a, b) => b.disagreement_percentage - a.disagreement_percentage)
        .slice(0, 5)
    }
  
    // Change from getter to a regular method
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