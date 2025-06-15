import { NuxtAppOptions } from '@nuxt/types'
import _ from 'lodash'

export default _.debounce(async ({ app, route, redirect, error }: NuxtAppOptions) => {
  const project = app.store.getters['projects/currentProject']
  if (project.id !== route.params.id) {
    try {
      await app.store.dispatch('projects/setCurrentProject', route.params.id)
    } catch (e: any) {
      if (e.message.includes('Database currently unavailable')) {
        return error({
          statusCode: 503,
          message: 'Database currently unavailable. Please try again later.'
        })
      }
      redirect('/projects')
    }
  }
}, 4000)