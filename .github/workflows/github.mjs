export async function dispatchRetryWorkflow(core, githubActions, context, refName, retries = 1) {
    if (context.runAttempt >= retries) {
        core.setFailed("Workflow run failed permanently");
        return false;
    }

    if (refName == "") {
        core.setFailed("Workflow run retry requested refName is invalid");
        return false;
    }

    githubActions.createWorkflowDispatch({
        owner: context.repo.owner,
        repo: context.repo.repo,
        workflow_id: "github_rerun_workflow.yml",
        ref: refName,
        inputs: {
            run_id: String(context.runId),
            retries: String(retries)
        }
    });

    return true;
}

export async function retryWorkflow(core, githubActions, context, runID, retries) {
    if (isNaN(retries)) {
        core.setFailed("Workflow run retry requested retries are invalid");
        return false;
    }

    const workflowRun = await githubActions.getWorkflowRun({
        owner: context.repo.owner,
        repo: context.repo.repo,
        run_id: runID,
        exclude_pull_requests: true
    });

    if (workflowRun.data.run_attempt >= retries) {
        core.setFailed("Workflow run failed permanently");
        return false;
    }

    await githubActions.reRunWorkflowFailedJobs({
        owner: context.repo.owner,
        repo: context.repo.repo,
        run_id: runID
    });

    return true;
}
