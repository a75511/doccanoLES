export const state = () => ({
  activeSession: null,
  pendingClosure: false,
  hasJoined: false,
  votingStatus: false,
})

export const getters = {
  hasActiveSession: (state) => !!state.activeSession,
  isVoting: (state) => state.votingStatus,
}

export const mutations = {
  SET_ACTIVE_SESSION(state, session) {
    state.activeSession = session
  },
  SET_PENDING_CLOSURE(state, status) {
    state.pendingClosure = status
  },
  SET_JOIN_STATUS(state, status) {
    state.hasJoined = status
  },
  CLEAR_SESSION(state) {
    state.activeSession = null
    state.hasJoined = false
    state.pendingClosure = false
  },
  SET_VOTING_STATUS(state, status) {
    state.votingStatus = status
  }
}

export const actions = {
  async fetchActiveSession({ commit }, projectId) {
    try {
      const session = await this.$services.discussion.getActiveDiscussion(projectId)
      commit('SET_ACTIVE_SESSION', session)
      commit('SET_PENDING_CLOSURE', session.pending_closure || false)
      return session
    } catch (error) {
      commit('SET_ACTIVE_SESSION', null)
      commit('SET_PENDING_CLOSURE', false)
    }
  },
  async joinSession({ commit }, { projectId, sessionId }) {
    try {
      await this.$services.discussion.joinSession(projectId, sessionId)
      commit('SET_JOIN_STATUS', true)
    } catch (error) {
      console.error('Failed to join session:', error)
    }
  },
  async checkParticipation({ commit, state }, projectId) {
    if (state.activeSession) {
      try {
        const response = await this.$services.discussion.checkParticipation(
          projectId, 
          state.activeSession.id
        )
        commit('SET_JOIN_STATUS', response.hasJoined)
      } catch (error) {
        console.error('Failed to check participation:', error)
      }
    }
  },
   async closeSession({ commit }, { projectId, sessionId }) {
    try {
      const response = await this.$services.discussion.closeSession(projectId, sessionId);
      if (response.pending_closure) {
        commit('SET_PENDING_CLOSURE', true);
      } else {
        commit('CLEAR_SESSION');
        this.$repositories.discussion.clearCommentCache(projectId);
      }
      return response;
    } catch (error) {
      console.error('Failed to close session:', error);
      throw error;
    }
  }
}