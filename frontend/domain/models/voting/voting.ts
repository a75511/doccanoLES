export class GuidelineVotingItem {
    constructor(
      readonly id: number,
      readonly projectId: number,
      readonly status: 'not_started' | 'voting' | 'completed',
      readonly guidelinesSnapshot: string,
      readonly currentDiscussionId: number | null,
      readonly agreeCount: number,
      readonly disagreeCount: number,
      readonly agreementPercentage: number,
      readonly votes: MemberVoteItem[] = []
    ) {}
  
    static create(
      id: number,
      projectId: number,
      status: 'not_started' | 'voting' | 'completed',
      guidelinesSnapshot: string,
      currentDiscussionId: number | null,
      agreeCount: number,
      disagreeCount: number,
      agreementPercentage: number,
      votes: MemberVoteItem[] = []
    ): GuidelineVotingItem {
      return new GuidelineVotingItem(
        id,
        projectId,
        status,
        guidelinesSnapshot,
        currentDiscussionId,
        agreeCount,
        disagreeCount,
        agreementPercentage,
        votes
      );
    }
  }
  
  export class MemberVoteItem {
    constructor(
      readonly id: number,
      readonly votingSessionId: number,
      readonly userId: number, 
      readonly username: string,
      readonly agrees: boolean,
      readonly votedAt: string
    ) {}
  
    static create(
      id: number,
      votingSessionId: number,
      userId: number, 
      username: string,
      agrees: boolean,
      votedAt: string
    ): MemberVoteItem {
      return new MemberVoteItem(
        id,
        votingSessionId,
        userId,
        username,
        agrees,
        votedAt
      );
    }
}