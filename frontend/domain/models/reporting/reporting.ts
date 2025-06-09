export interface DisagreementStatistics {
  total_examples: number
  conflict_count: number
  total_members: number
  label_distributions: {
    attribute: string
    descriptions: string[]
    total_members: number
    examples: Array<{
      example_id: number
      example_text: string
      labels: Array<{ label: string; count: number }>
      total: number
      non_annotated: number
    }>
  }[]
}