export default async function ({ store, route, redirect }) {
  const projectId = route.params.id;
  
  // Skip middleware for sessions page
  if (route.path.includes('/discussions/sessions')) return;

  try {
    // Always clear cache and fetch fresh data
    const session = await store.dispatch('discussion/fetchActiveSession', projectId);

    if (!session) {
      store.commit('discussion/CLEAR_SESSION');
      return;
    }
    
    // Check participation only if user is authenticated
    if (store.state.auth.loggedIn) {
      await store.dispatch('discussion/checkParticipation', projectId);
    }

    const { activeSession, hasJoined } = store.state.discussion;
    
    // Redirect to sessions page if not joined (only for authenticated users)
    if (store.state.auth.loggedIn && (!activeSession || !hasJoined)) {
      return redirect(`/projects/${projectId}/discussions/sessions`);
    }
  } catch (error) {
    console.error('Discussion middleware error:', error);
    store.commit('discussion/CLEAR_SESSION');
  }
}