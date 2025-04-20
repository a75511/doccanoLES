export class DiscussionItem {
    constructor(
        readonly id: number,
        readonly project: number,
        readonly title: string,
        readonly description: string,
        readonly isActive: boolean,
        readonly createdAt: string,
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
      readonly updatedAt: string
    ) {}
  }