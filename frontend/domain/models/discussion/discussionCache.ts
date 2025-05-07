import { APIDiscussionRepository } from "~/repositories/discussion/apiDiscussionRepository"

const CACHE_KEY = 'discussion_cache'

export class DiscussionCache {
    static async processCache(projectId: string,
         repository: APIDiscussionRepository): Promise<void> {
        const cache = this.getCache()
        const keys = ['pending', 'updates', 'deletes']
        
        for (const key of keys) {
          const fullKey = `${projectId}_${key}`
          const items = cache[fullKey] || []
          
          while(items.length > 0) {
            const item = items.shift()
            try {
              if (key === 'pending') {
                await repository.addComment(projectId, item.text)
              } else if (key === 'updates') {
                await repository.updateComment(projectId, item.id, item.text)
              } else if (key === 'deletes') {
                await repository.deleteComment(projectId, item)
              }
            } catch (error) {
              items.unshift(item)
              cache[fullKey] = items
              this.saveCache(cache)
              throw error
            }
          }
          
          delete cache[fullKey]
          this.saveCache(cache)
        }
      }
      
    static cacheComment(projectId: string, comment: any) {
        const cache = this.getCache()
        const key = `${projectId}_pending`
        cache[key] = cache[key] || []
        cache[key].push(comment)
        this.saveCache(cache)
    }

    static cacheUpdate(projectId: string, comment: any) {
        const cache = this.getCache()
        const key = `${projectId}_updates`
        cache[key] = cache[key] || []
        cache[key].push(comment)
        this.saveCache(cache)
    }

    static cacheDeletion(projectId: string, commentId: number) {
        const cache = this.getCache()
        const key = `${projectId}_deletes`
        cache[key] = cache[key] || []
        cache[key].push(commentId)
        this.saveCache(cache)
    }

    static getCachedComments(projectId: string) {
        const cache = this.getCache()
        return [
        ...(cache[`${projectId}_pending`] || []),
        ...(cache[`${projectId}_updates`] || [])
        ]
    }

    static removeCachedComment(projectId: string, commentId: number) {
        const cache = this.getCache()
        const keys = [`${projectId}_pending`, `${projectId}_updates`]
        keys.forEach(key => {
        cache[key] = (cache[key] || []).filter((c: any) => c.id !== commentId)
        })
        this.saveCache(cache)
    }

    private static getCache() {
        return JSON.parse(localStorage.getItem(CACHE_KEY) || '{}')
    }

    private static saveCache(cache: any) {
        localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
    }
}