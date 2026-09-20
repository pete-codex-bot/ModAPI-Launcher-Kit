#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
artifact_dir="$repository_root/artifacts/standard-user"
workflow_name="standard-user-build.yml"

cd "$repository_root"

python3 scripts/verify-standard-user.py --source-only

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This helper is the macOS entry point for the Windows CI build." >&2
  echo "On Windows, run the restore and MSBuild commands documented in artifacts/standard-user/README.md." >&2
  exit 2
fi

if command -v msbuild >/dev/null 2>&1 || command -v xbuild >/dev/null 2>&1; then
  echo "A local MSBuild-like tool was found, but this .NET Framework 4.8 WPF build requires Windows build targets." >&2
fi

github_cli="${GH_CLI:-gh}"
build_repository="${STANDARD_USER_BUILD_REPOSITORY:-}"

if [[ -z "$build_repository" ]]; then
  echo "Set STANDARD_USER_BUILD_REPOSITORY to the GitHub fork containing the current commit." >&2
  echo "For Codex automation, also set GH_CLI=codex-gh." >&2
  exit 2
fi

if ! command -v "$github_cli" >/dev/null 2>&1; then
  echo "Required GitHub CLI command was not found: $github_cli" >&2
  exit 2
fi

commit_sha="$(git rev-parse HEAD)"
run_id="$($github_cli run list \
  --repo "$build_repository" \
  --workflow "$workflow_name" \
  --commit "$commit_sha" \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId // empty')"

if [[ -z "$run_id" ]]; then
  echo "No CI build exists for $commit_sha in $build_repository." >&2
  echo "Push this commit to the fork; the workflow's push trigger will start the Windows build." >&2
  exit 3
fi

$github_cli run watch "$run_id" --repo "$build_repository" --exit-status

mkdir -p "$artifact_dir"
find "$artifact_dir" -maxdepth 1 -type f \( -name '*.exe' -o -name '*.dll' -o -name 'SHA256SUMS.txt' \) -delete
$github_cli run download "$run_id" \
  --repo "$build_repository" \
  --name "Spore-ModAPI-standard-user-$commit_sha" \
  --dir "$artifact_dir"

python3 scripts/verify-standard-user.py "$artifact_dir"
echo "Standard-user binaries are ready in: $artifact_dir"
