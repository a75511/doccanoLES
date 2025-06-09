// discussion.js middleware
export default async function ({ store, route, redirect }) {
  const projectId = route.params.id;
  
  // Skip middleware for sessions page
  if (route.path.includes('/discussions/sessions')) return;

    // Always clear cache and fetch fresh data
  const session = await store.dispatch('discussion/fetchActiveSession', projectId);

  if (!session) {
     store.commit('discussion/CLEAR_SESSION');
  }
  
  const { activeSession, hasJoined } = store.state.discussion;
  
  // Redirect to sessions page if not joined
  if (!activeSession || !hasJoined) {
    return redirect(`/projects/${projectId}/discussions/sessions`);
  }
}