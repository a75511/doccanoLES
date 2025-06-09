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

export interface LabelPercentage {
  label: string
  annotator_count: number
  total_annotators: number
  agreement_percentage: number
}

export interface ExampleDisagreement {
  example_text: string | null
  total_annotators: number
  label_percentages: LabelPercentage[]
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
      .sort((a, b) => {
        const minPercentageA = Math.min(...a.label_percentages.map(lp => lp.agreement_percentage))
        const minPercentageB = Math.min(...b.label_percentages.map(lp => lp.agreement_percentage))
        return minPercentageA - minPercentageB
      })
      .slice(0, 5)
  }

  getUniqueLabels(): string[] {
    const labels = new Set<string>()
    this.disagreements.forEach(disagreement => {
      disagreement.label_percentages.forEach(lp => {
        labels.add(lp.label)
      })
    })
    return Array.from(labels).sort()
  }

  getLabelStats(): { [label: string]: { totalExamples: number, avgPercentage: number } } {
    const labelStats: { [label: string]: { totalExamples: number, totalPercentage: number } } = {}

    this.disagreements.forEach(disagreement => {
      disagreement.label_percentages.forEach(lp => {
        if (!labelStats[lp.label]) {
          labelStats[lp.label] = { totalExamples: 0, totalPercentage: 0 }
        }
        labelStats[lp.label].totalExamples += 1
        labelStats[lp.label].totalPercentage += lp.agreement_percentage
      })
    })

    // Convert to average percentages
    const result: { [label: string]: { totalExamples: number, avgPercentage: number } } = {}
    Object.keys(labelStats).forEach(label => {
      result[label] = {
        totalExamples: labelStats[label].totalExamples,
        avgPercentage: labelStats[label].totalPercentage / labelStats[label].totalExamples
      }
    })

    return result
  }
}