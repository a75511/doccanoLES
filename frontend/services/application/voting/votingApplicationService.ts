import { GuidelineVotingItem, MemberVoteItem } from '@/domain/models/voting/voting';
import { APIVotingRepository } from '@/repositories/voting/apiVotingRepository';

export class VotingApplicationService {
  constructor(private readonly repository: APIVotingRepository) {}

  public async getVotingStatus(projectId: string): Promise<GuidelineVotingItem> {
    try {
      return await this.repository.getVotingStatus(projectId);
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to fetch voting status.');
    }
  }

  public async startVoting(projectId: string): Promise<GuidelineVotingItem> {
    try {
      return await this.repository.startVoting(projectId);
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to start voting session.');
    }
  }

  public async submitVote(projectId: string, agrees: boolean): Promise<MemberVoteItem> {
    try {
      return await this.repository.submitVote(projectId, agrees);
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to submit vote.');
    }
  }

  public async endVoting(projectId: string): Promise<GuidelineVotingItem> {
    try {
      return await this.repository.endVoting(projectId);
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to end voting session.');
    }
  }

  public async createFollowUp(projectId: string): Promise<GuidelineVotingItem> {
    try {
      return await this.repository.createFollowUp(projectId);
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Failed to create follow-up voting session.');
    }
  }
}