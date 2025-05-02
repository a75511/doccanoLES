export interface DisagreementStatistics {
  total_examples: number
  conflict_count: number
  label_distributions: {
    attribute: string
    descriptions: {
      description: string
      labels: {
        label: string
        count: number
      }[]
    }[]
  }[]
}