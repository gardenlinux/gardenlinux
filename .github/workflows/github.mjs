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

export function isMatrixEmpty(matrix) {
    return (!Object.keys(matrix).includes('include') || matrix['include'].length < 1);
}

export function getGHCRRepositoryFromTarget(target) {
    let repository = "";

    switch(target) {
        case "release":
            repository = "ghcr.io/gardenlinux/gardenlinux";
            break;
        case "nightly":
            repository = "ghcr.io/gardenlinux/nightly";
            break;
    }

    return repository;
}

export function getGitHubSigningEnvironmentFromTarget(target) {
    let environment = "";

    switch(target) {
        case "release":
            environment = "oidc_aws_kms_release";
            break;
        case "nightly":
            environment = "oidc_aws_kms_nightly";
            break;
    }

    return environment;
}

export function getTestEnvironmentsEnabled(commaSeparatedTestsRequested) {
    const knownTests = ["chroot", "cloud", "oci", "qemu", "bare"];
    const testsRequested = commaSeparatedTestsRequested.split(",");
    let tests = [];

    for (const test of knownTests) {
        if (testsRequested.includes(test)) {
            tests.push(test);
        }
    }

    return tests;
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

export async function createNightlyFailureIssue(core, github, context, needs, aptCompareOutput, newVersion, oldVersion) {
    const failedNeeds = Object.entries(needs).filter(([_, data]) => data.result === 'failure');
    const date = new Date().toISOString().split('T')[0];
    const title = `Nightly workflow failed on ${date} (run #${context.runId})`;
    const runUrl = `${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`;

    let body = `## Nightly workflow failed\n\n`;
    body += `A summary of the failure is provided below. See the [workflow run](${runUrl}) for full details.\n\n`;
    body += `| | |\n`;
    body += `|---|---|\n`;
    body += `| **Workflow** | ${context.workflow} |\n`;
    body += `| **Run** | ${runUrl} |\n`;
    body += `| **Ref** | ${context.ref} |\n`;
    body += `| **SHA** | ${context.sha} |\n\n`;

    body += `### Failed jobs\n\n`;
    if (failedNeeds.length > 0) {
        for (const [name, data] of failedNeeds) {
            body += `- **${name}**: ${data.result}\n`;
        }
    } else {
        body += `- No individual job reported a failure result, but the overall workflow failed.\n`;
    }

    const { data: jobsData } = await github.rest.actions.listJobsForWorkflowRun({
        owner: context.repo.owner,
        repo: context.repo.repo,
        run_id: context.runId,
    });

    const failedJobs = jobsData.jobs.filter(job => job.conclusion === 'failure');

    if (failedJobs.length > 0) {
        body += `\n### Failed job logs (last 10 lines)\n\n`;
        for (const job of failedJobs) {
            const logLines = await getLastJobLogLines(github, context, job.id);
            body += `<details>\n`;
            body += `<summary><b>${job.name}</b></summary>\n\n`;
            body += '```\n';
            body += logLines;
            body += '\n```\n\n';
            body += `</details>\n\n`;
        }
    }

    const { data: existingIssues } = await github.rest.issues.listForRepo({
        owner: context.repo.owner,
        repo: context.repo.repo,
        state: 'open',
    });

    const duplicate = existingIssues.find(issue =>
        issue.title.includes(`run #${context.runId}`)
    );

    if (duplicate) {
        core.notice(`Issue already exists for this run: ${duplicate.html_url}`);
        return;
    }

    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    const { data: pullsData } = await github.rest.pulls.list({
        owner: context.repo.owner,
        repo: context.repo.repo,
        state: 'closed',
        sort: 'updated',
        direction: 'desc',
        per_page: 100,
    });

    const recentlyMerged = pullsData.filter(pr => pr.merged_at && pr.merged_at >= oneDayAgo);

    body += `\n### Pull requests merged in the last 24 hours\n\n`;
    if (recentlyMerged.length > 0) {
        for (const pr of recentlyMerged) {
            body += `- #${pr.number} [${pr.title}](${pr.html_url}) by @${pr.user.login} (merged at ${pr.merged_at})\n`;
        }
    } else {
        body += `- No pull requests were merged in the last 24 hours.\n`;
    }

    body += `\n### Apt packages updated since yesterday's nightly run\n\n`;
    body += `<details>\n`;
    body += `<summary>Click to expand output of <code>./hack/compare-apt-repo-versions.sh ${newVersion} ${oldVersion}</code></summary>\n\n`;
    body += '```\n';
    body += aptCompareOutput || '(no output)';
    body += '\n```\n\n';
    body += `</details>\n\n`;

    await github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: title,
        body: body,
    });
}

async function getLastJobLogLines(github, context, jobId) {
    try {
        const resp = await github.rest.actions.downloadJobLogsForWorkflowRun({
            owner: context.repo.owner,
            repo: context.repo.repo,
            job_id: jobId,
        });
        const logText = typeof resp.data === 'string' ? resp.data : String(resp.data);
        const lines = logText.split('\n').filter(line => line !== '');
        const lastLines = lines.slice(-10);
        return lastLines.length > 0 ? lastLines.join('\n') : '(no log output)';
    } catch (err) {
        return `Error retrieving logs: ${err.message}`;
    }
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
