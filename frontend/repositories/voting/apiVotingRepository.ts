import { GuidelineVotingItem, MemberVoteItem } from '@/domain/models/voting/voting';
import ApiService from '@/services/api.service';

export class APIVotingRepository {
  constructor(private readonly request = ApiService) {}

  async getVotingStatus(projectId: string): Promise<GuidelineVotingItem> {
    const url = `/projects/${projectId}/voting`;
    const response = await this.request.get(url);
    return this.toModel(response.data);
  }

  async startVoting(projectId: string): Promise<GuidelineVotingItem> {
    const url = `/projects/${projectId}/start-voting`;
    const response = await this.request.patch(url);  // Changed from post to patch
    return this.toModel(response.data);
}

  async submitVote(projectId: string, agrees: boolean): Promise<MemberVoteItem> {
    const url = `/projects/${projectId}/vote`;
    const response = await this.request.post(url, { agrees });
    return this.toVoteModel(response.data);
  }

  async endVoting(projectId: string): Promise<GuidelineVotingItem> {
    const url = `/projects/${projectId}/end-voting`;
    const response = await this.request.patch(url);  // Changed from post to patch
    return this.toModel(response.data);
}

  async createFollowUp(projectId: string): Promise<GuidelineVotingItem> {
    const url = `/projects/${projectId}/create-follow-up`;
    const response = await this.request.post(url);
    return this.toModel(response.data);
  }

  private toModel(item: any): GuidelineVotingItem {
    return GuidelineVotingItem.create(
      item.id,
      item.project,
      item.status,
      item.guidelines_snapshot,
      item.current_discussion,
      item.agree_count,
      item.disagree_count,
      item.agreement_percentage,
      item.votes ? item.votes.map((vote: any) => this.toVoteModel(vote)) : [],
      item.previous_voting // Add previous voting reference if needed
    );
  }

  private toVoteModel(item: any): MemberVoteItem {
    return MemberVoteItem.create(
      item.id,
      item.voting_session,
      item.user.id, 
      item.username,
      item.agrees,
      item.voted_at
    );
}
}