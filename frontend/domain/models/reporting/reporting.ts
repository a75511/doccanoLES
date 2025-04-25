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