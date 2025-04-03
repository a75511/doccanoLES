export const state = () => ({
  current: {
    id: '',
    name: '',
    perspective: null,
  }
})

export const getters = {
  currentProject(state) {
    return state.current
  },

  project(state) {
    return state.current
  }
}

export const mutations = {
  setCurrent(state, payload) {
    state.current = payload
  },
  updateCurrentProjectPerspective(state, perspective) {
    if (state.current) {
      state.current.perspective = perspective;
    }
  },
}
export const actions = {
  async setCurrentProject({ commit }, projectId) {
    try {
      const project = await this.$services.project.findById(projectId)
      commit('setCurrent', project)
    } catch (error) {
      if (error.response && error.response.status === 500) {
        throw new Error('Database currently unavailable. Please try again later.')
      }
      throw error
    }
  }
}