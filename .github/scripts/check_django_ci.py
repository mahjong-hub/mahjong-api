import json
import os
import sys

from util.github_api import update_pr_comment

BOT_IDENTIFIER = '<!-- pr-check-django-ci -->'


def main() -> int:
    repo_full = os.environ.get('GITHUB_REPOSITORY')
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    django_changed = (
        os.environ.get('DJANGO_CHANGED', 'false').lower() == 'true'
    )
    django_ci_result = os.environ.get('DJANGO_CI_RESULT', '')

    if not repo_full or not event_path:
        print('Not running inside GitHub Actions.')
        return 0

    owner, repo = repo_full.split('/', 1)

    with open(event_path, encoding='utf-8') as f:
        event = json.load(f)

    pr_number = event.get('number')
    if not pr_number:
        print('No PR number found in event payload; skipping.')
        return 0

    if not django_changed:
        update_pr_comment(
            owner,
            repo,
            pr_number,
            '## ➖ Django CI\n\nNot required for this PR (no Django files changed).',
            BOT_IDENTIFIER,
        )
        return 0

    if django_ci_result == 'success':
        update_pr_comment(
            owner,
            repo,
            pr_number,
            '## ✅ Django CI\n\nAll Django CI checks passed.',
            BOT_IDENTIFIER,
        )
        return 0

    if django_ci_result == 'failure':
        update_pr_comment(
            owner,
            repo,
            pr_number,
            '## ❌ Django CI\n\nDjango CI failed. '
            'Please fix the failing checks before merging.',
            BOT_IDENTIFIER,
        )
        return 1

    # cancelled, skipped unexpectedly, or empty
    update_pr_comment(
        owner,
        repo,
        pr_number,
        f'## ❌ Django CI\n\nDjango CI did not complete '
        f'successfully (result: `{django_ci_result}`).',
        BOT_IDENTIFIER,
    )
    return 1


if __name__ == '__main__':
    sys.exit(main())
