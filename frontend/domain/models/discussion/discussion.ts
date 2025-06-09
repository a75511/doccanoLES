export class DiscussionItem {
    constructor(
        readonly id: number,
        readonly project: number,
        readonly title: string,
        readonly description: string,
        readonly isActive: boolean,
        readonly createdAt: string,
        readonly started_at: string,
        readonly finished_at: string | null,
        readonly pending_closure: boolean,
        readonly comments: DiscussionCommentItem[] = []
    ) {}
}

export class DiscussionCommentItem {
    constructor(
      readonly id: number,
      readonly text: string,
      readonly member: number,
      readonly username: string,
      readonly createdAt: string,
      readonly updatedAt: string,
      readonly temp_id?: number
    ) {}
  }