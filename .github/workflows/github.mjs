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

export function excludeFlavorsMatrix(matrixA, matrixB) {
    matrixA = flattenFlavorsMatrixByArch(matrixA);
    matrixB = flattenFlavorsMatrixByArch(matrixB);
    let resultMatrix = [];

    for (const arch in matrixA) {
        for (const flavor of matrixA[arch]) {
            if (!matrixB.hasOwnProperty(arch) || !matrixB[arch].includes(flavor)) {
                resultMatrix.push({ "arch": arch, "flavor": flavor });
            }
        }
    }

    return { "include": resultMatrix };
}

export function flattenFlavorsMatrixByArch(matrix) {
    let matrixByArch = {};

    for (const flavor of matrix.include) {
        if (!(flavor["arch"] in matrixByArch)) {
            matrixByArch[flavor["arch"]] = [];
        }

        matrixByArch[flavor["arch"]].push(flavor["flavor"]);
    }

    return matrixByArch;
}

export function intersectFlavorsMatrix(matrixA, matrixB) {
    matrixA = flattenFlavorsMatrixByArch(matrixA);
    matrixB = flattenFlavorsMatrixByArch(matrixB);
    let intersectMatrix = [];

    for (const arch in matrixA) {
        if (!matrixB.hasOwnProperty(arch)) {
            continue;
        }

        for (const flavor of matrixA[arch]) {
            if (matrixB[arch].includes(flavor)) {
                intersectMatrix.push({ "arch": arch, "flavor": flavor });
            }
        }
    }

    return { "include": intersectMatrix };
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
