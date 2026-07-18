# Rollback Plan
Every deployment is a git commit; every state is recoverable.
- Bad deploy: `git revert <sha>` on main -> Actions rebuilds and redeploys the previous good state. Or re-run a previous successful "Build and deploy" workflow from the Actions tab.
- Data error only: revert the offending data/*.json change; rebuild.
- Emergency takedown: Settings -> Pages -> unpublish, or set the workflow to no-op; investigate; redeploy.
- Always keep main green: the deploy workflow runs tests before publishing, so a failing build never reaches the live site.
Verification after rollback: load the live URL and confirm the reverted content is served.
