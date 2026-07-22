/**
 * Node.js runner for createNightlyFailureIssue.
 * Called by create_nightly_issue.py — not intended for direct use.
 *
 * Reads all inputs from environment variables set by the Python wrapper:
 *   GITHUB_TOKEN, GL_OWNER, GL_REPO, GL_RUN_ID, GL_REF, GL_SHA,
 *   GL_WORKFLOW, GL_SERVER_URL, GL_NEEDS_JSON,
 *   GL_APT_COMPARE_OUTPUT, GL_NEW_VERSION, GL_OLD_VERSION
 */

import { Octokit } from "@octokit/rest";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const { createNightlyFailureIssue } = await import(join(__dirname, "github.mjs"));

const token = process.env.GITHUB_TOKEN;
if (!token) {
    console.error("GITHUB_TOKEN is not set");
    process.exit(1);
}

const octokit = new Octokit({ auth: token });

const core = {
    notice: (msg) => console.log(`NOTICE: ${msg}`),
    setFailed: (msg) => { console.error(`FAILED: ${msg}`); process.exit(1); },
};

const context = {
    runId: parseInt(process.env.GL_RUN_ID, 10),
    ref: process.env.GL_REF,
    sha: process.env.GL_SHA,
    workflow: process.env.GL_WORKFLOW,
    serverUrl: process.env.GL_SERVER_URL,
    repo: {
        owner: process.env.GL_OWNER,
        repo: process.env.GL_REPO,
    },
};

const needs = JSON.parse(process.env.GL_NEEDS_JSON || "{}");

await createNightlyFailureIssue(
    core,
    octokit,
    context,
    needs,
    process.env.GL_APT_COMPARE_OUTPUT || "",
    process.env.GL_NEW_VERSION || "",
    process.env.GL_OLD_VERSION || "",
);
