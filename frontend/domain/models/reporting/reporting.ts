export interface DisagreementStatistics {
  total_examples: number
  conflict_count: number
  attribute_distributions: {
    attribute: string
    total_members: number
    data: {
      value: string
      count: number
    }[]
  }[]
}