---
name: yao-geoflow-cli
description: Use when operating an existing GEOFlow system from local commands or Laravel API v1 to inspect catalog/materials, manage tasks/jobs/articles, publish content, or run API/Docker preflight. Use for scriptable GEOFlow operations instead of the web admin. Do not use for backend implementation, schema changes, direct database edits, or admin-only distribution setup.
---

<!--
Copyright © 2026 姚金刚. All rights reserved.
Project: yao-geoflow-cli
Created by: 姚金刚
Date: 2026-05-16
X: https://x.com/yaojingang
-->

# Yao GEOFlow CLI

Use this skill when the system already has the GEOFlow API available and the job is to operate that system from local commands. The current Laravel 2.0.x public repository commonly exposes `/api/v1` without a `bin/geoflow` wrapper, so use API v1 directly in that case. Prefer `bin/geoflow` only when it exists and supports the requested action.

## What This Skill Owns

- GEOFlow CLI or API v1 preflight checks
- Catalog lookup for model, prompt, keyword library, title library, image library, author, category, and knowledge-base IDs
- Material library lookup and CRUD for categories, authors, keyword libraries, title libraries, image libraries, and knowledge bases
- Material item management for keyword, title, and image library entries
- Task creation, update, delete, start, stop, enqueue, and status inspection
- Job inspection after enqueue or worker execution
- Article draft upload, article update, review, publish, and trash actions
- Safe command construction with idempotency keys for write operations

## What This Skill Does Not Cover

- Implementing or refactoring GEOFlow backend code
- Direct database writes or bypassing `/api/v1`
- Web-admin-only flows that do not exist in `geoflow` or `/api/v1`
- Distribution channel setup, target-site package download, Analytics, URL import, title async generation, or image upload orchestration outside the current CLI/API surface
- Debugging worker internals beyond reporting what the CLI and API return

## Required Preconditions

1. Confirm the target workspace is a GEOFlow Laravel workspace or contains `bin/geoflow`.
2. If `bin/geoflow` exists, confirm the CLI can resolve config via `--config`, env vars, or the default config path.
3. If `bin/geoflow` is missing, use API v1 fallback with `GEOFLOW_BASE_URL` and `GEOFLOW_API_TOKEN`, or login through `/api/v1/auth/login` without printing the password.
4. If authenticated reads return `401`/`403` or token-invalid errors, refresh login/token instead of treating the workspace as already authenticated.
5. Run the bundled preflight script before the first mutating action in a new workspace.
6. Treat preflight as successful only when an authenticated read succeeds. Local config parsing alone is not enough because it does not prove API reachability or token validity.
7. If preflight fails, stop and report the exact missing prerequisite instead of guessing.
8. For material operations, verify the token has `materials:read` and `materials:write` before mutating.

Use [references/operation-boundary.md](references/operation-boundary.md) for the enforced boundary and [references/command-map.md](references/command-map.md) for the supported commands.
Use [references/laravel-api-v1-docker.md](references/laravel-api-v1-docker.md) when the target GEOFlow system is the Laravel rewrite, runs through Docker Compose, or has no `bin/geoflow` wrapper yet.

## Default Workflow

1. Identify the target GEOFlow workspace. If the user did not specify one, prefer the current workspace when it has `artisan` or `bin/geoflow`.
2. If `bin/geoflow` exists and config is missing, run `bin/geoflow login --base-url ... --username ...` and let the CLI prompt for the password.
3. If `bin/geoflow` is missing, use API v1 fallback and first verify `GET /api/v1/catalog` with a bearer token.
4. Run `scripts/geoflow_preflight.sh "<workspace>" [config]` to verify the CLI entrypoint, authenticated API access, and current token. For material work, also verify `GET /api/v1/materials`.
5. For lookup work, call `geoflow catalog` or `GET /api/v1/catalog` first so IDs come from the system instead of memory. Use `GET /api/v1/materials/{type}` when the user needs material library records, counts, or item IDs.
6. For write operations, use an explicit `--idempotency-key` or `X-Idempotency-Key`.
7. After any write, immediately run the corresponding read command to verify the actual persisted state.
8. For task create/update, preserve the current API contract: optional `author_id`, `image_library_id`, `knowledge_base_id`, and `fixed_category_id` may be omitted; `publish_scope` is one of `local_and_distribution`, `distribution_only`, or `local_only`.
9. After `article publish`, verify the final local frontend URL using the system's slug route, not an `article.php?id=...` compatibility link. Treat `/article/{slug}` as the local publish URL only when the final article status is `published`.
10. For this system, generated article slugs should be 8-character short ASCII tokens such as `/article/bc7af3fb`. A user-supplied slug may differ; report what is persisted instead of inventing a URL rule.
11. If a generation job fails, separate CLI/API success from business-data failure. Example: missing titles is a task-data issue, not a CLI issue.
12. If the user asked for a publish smoke test and task generation is blocked by business data such as missing titles, stop the affected task first when it is still active or queued, then fall back to `article create` + `article review` + `article publish` so the publish chain can still be validated without leaving noisy retries behind.
13. Report commands run, resource IDs touched, and the resulting state in concise operational terms.

## Command Discipline

- Prefer direct executable invocation when `bin/geoflow` exists:

```bash
"/path/to/workspace/bin/geoflow" --config /path/to/config ...
```

- If the file is not executable but exists, fall back to:

```bash
php "/path/to/workspace/bin/geoflow" --config /path/to/config ...
```

- Never synthesize API requests directly when the CLI exists and already supports the action.
- When the CLI is absent, use `/api/v1` with explicit bearer auth and `X-Idempotency-Key` for mutating requests.
- Never store or print a full token in the final user-facing summary unless the user explicitly asked for it.
- Do not claim admin-only Distribution Management actions are available through API v1 unless the target workspace exposes matching routes.

## Typical Flows

### 1. Inspect available resources

```bash
"/path/to/workspace/bin/geoflow" --config /path/to/config catalog
```

API fallback:

```bash
curl -sS -H "Authorization: Bearer $GEOFLOW_API_TOKEN" -H "Accept: application/json" \
  "$GEOFLOW_BASE_URL/api/v1/catalog"
curl -sS -H "Authorization: Bearer $GEOFLOW_API_TOKEN" -H "Accept: application/json" \
  "$GEOFLOW_BASE_URL/api/v1/materials"
```

### 2. Manage materials

Material API types are `categories`, `authors`, `keyword-libraries`, `title-libraries`, `image-libraries`, and `knowledge-bases`. Item endpoints exist for `keyword-libraries`, `title-libraries`, `image-libraries`, and read-only `knowledge-bases` chunks.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $GEOFLOW_API_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: material-keyword-library-001" \
  --data '{"name":"API Keywords","description":"Created from API"}' \
  "$GEOFLOW_BASE_URL/api/v1/materials/keyword-libraries"
```

### 3. Create and run a task

```bash
"/path/to/workspace/bin/geoflow" --config /path/to/config task create --json ./task.json --idempotency-key task-create-001
"/path/to/workspace/bin/geoflow" --config /path/to/config task start 12 --idempotency-key task-start-12
"/path/to/workspace/bin/geoflow" --config /path/to/config task enqueue 12 --idempotency-key task-enqueue-12
"/path/to/workspace/bin/geoflow" --config /path/to/config job get 88
```

For task deletion, prefer the CLI when supported; otherwise use `DELETE /api/v1/tasks/{id}` with an idempotency key, then verify `GET /api/v1/tasks/{id}` returns not found.

### 4. Upload and publish an article

```bash
"/path/to/workspace/bin/geoflow" --config /path/to/config article create --title "标题" --content-file ./article.md --task-id 12 --author-id 5 --category-id 2 --idempotency-key article-create-001
"/path/to/workspace/bin/geoflow" --config /path/to/config article review 101 --status approved --note "CLI review pass" --idempotency-key article-review-101
"/path/to/workspace/bin/geoflow" --config /path/to/config article publish 101 --idempotency-key article-publish-101
```

Then verify both:

- the article state through `article get 101`
- the final local frontend URL using `/article/{slug}` when the persisted status is `published`

### 5. Fallback when task generation is blocked by business data

If `task jobs` or `job get` shows a business-data failure such as `没有可用的标题`, do not keep retrying the task as though the CLI were broken. If the user only needs a publish-path smoke test, stop the task first, then create a direct draft article instead:

```bash
"/path/to/workspace/bin/geoflow" --config /path/to/config task stop 12 --idempotency-key task-stop-12
"/path/to/workspace/bin/geoflow" --config /path/to/config article create \
  --title "测试文章" \
  --content-file ./article.md \
  --author-id 5 \
  --category-id 2 \
  --status draft \
  --review-status pending \
  --idempotency-key article-create-smoke-001
"/path/to/workspace/bin/geoflow" --config /path/to/config article review 101 --status approved --note "CLI smoke test" --idempotency-key article-review-101
"/path/to/workspace/bin/geoflow" --config /path/to/config article publish 101 --idempotency-key article-publish-101
```

## Response Rules

- When the user asks to operate GEOFlow, do the work through the CLI instead of just describing commands.
- If the user has not logged in yet, guide them through `geoflow login` first instead of asking them to create a token manually.
- If authenticated reads fail because the token is invalid or expired, treat that as a login problem and refresh with `geoflow login --force`.
- If authenticated reads fail for another reason, do not default to `login --force`; report the actual API or connectivity failure first.
- If the request implies batch operations, still keep each write idempotent and verify a sample of the outputs.
- Do not invent a frontend article URL rule from memory. Read the system's current routing or canonical behavior first, then return the final local `/article/{slug}` URL only when the article is locally published, not a temporary `article.php?id=...` entrypoint.
- If the user asks to configure distribution channels, download target-site packages, view Analytics, or perform other admin-only flows, state that the current API v1 surface does not expose that operation and use the web admin or a separate backend/admin skill instead.
- If the user asks for automation or a reusable flow, finish the operation first, then suggest whether an additional skill or automation is warranted.

## Reference Map

- Read [references/operation-boundary.md](references/operation-boundary.md) for safety and scope.
- Read [references/command-map.md](references/command-map.md) for CLI-to-capability mapping.
- Read [references/laravel-api-v1-docker.md](references/laravel-api-v1-docker.md) for Laravel API v1 fallback, Docker deployment checks, API scopes, and non-JSON response diagnosis.
- Use [scripts/geoflow_preflight.sh](scripts/geoflow_preflight.sh) before mutating a new workspace.
- Inspect [evals/trigger_cases.json](evals/trigger_cases.json) when tightening or reviewing the trigger boundary.
- If you need the underlying CLI semantics, inspect the target workspace's `bin/geoflow --help` and current `routes/api.php`; do not rely on a stale CLI guide path.
