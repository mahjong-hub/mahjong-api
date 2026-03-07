import json
import os
import re
import sys

from util.github_api import github_api, update_pr_comment

BOT_IDENTIFIER = '<!-- pr-check-meta -->'


def main() -> int:
    # GitHub Actions context
    repo_full = os.environ.get('GITHUB_REPOSITORY')  # "owner/repo"
    event_path = os.environ.get('GITHUB_EVENT_PATH')

    if not repo_full or not event_path:
        print('Not running inside GitHub Actions with pull_request context.')
        return 0

    owner, repo = repo_full.split('/', 1)

    # Load event payload to get the PR number
    with open(event_path, encoding='utf-8') as f:
        event = json.load(f)

    # For pull_request events, this is always present
    pr_number = event.get('number')
    if not pr_number:
        print('No PR number found in event payload; skipping.')
        return 0

    # Fetch PR details
    pr_data = github_api(
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}',
    )

    title = pr_data.get('title') or ''
    assignees = pr_data.get('assignees') or []
    labels = pr_data.get('labels') or []

    # ---- Validation rules ----
    errors: list[str] = []

    # Title format: "<type>(optional-domain): description"
    # e.g. "feat(core): add scoring API", "fix: handle 500s"
    title_pattern = re.compile(r'^[a-z]+(\([^)]+\))?: .+')
    title_ok = bool(title_pattern.match(title))
    assignees_ok = bool(assignees)
    labels_ok = bool(labels)

    if not title_ok:
        errors.append(
            (
                'Title must follow the format '
                '`<type>(optional-domain): description` '
                '(for example: `feat(core): add scoring API`).'
            ),
        )

    if not assignees_ok:
        errors.append('An assignee must be set so ownership is clear.')

    if not labels_ok:
        errors.append('At least one label must be applied to the PR.')

    if errors:
        # Professional failure comment with status table
        status_rows = [
            f'| Title format | {"✅" if title_ok else "❌"} |',
            f'| Assignee set | {"✅" if assignees_ok else "❌"} |',
            f'| Labels set   | {"✅" if labels_ok else "❌"} |',
        ]
        status_table = '| Check | Status |\n|-------|--------|\n' + '\n'.join(
            status_rows,
        )

        body = (
            '## ❌ PR Meta Check\n\n'
            'The automated PR checks found one or more issues with this '
            'pull request.\n\n'
            f'{status_table}\n\n'
            '### Details\n' + '\n'.join(f'- {msg}' for msg in errors) + '\n\n'
            'Once you have addressed the above items (e.g. updating the title, '
            'adding an assignee or labels), this check will re-run automatically '
            'on the next PR update.'
        )
        update_pr_comment(owner, repo, pr_number, body, BOT_IDENTIFIER)
        return 1

    # Success: professional summary with table
    assignee_list = ', '.join(a['login'] for a in assignees) or '—'
    label_list = ', '.join(label['name'] for label in labels) or '—'

    summary_table = (
        '| Field     | Value |\n'
        '|-----------|-------|\n'
        f'| Title     | `{title}` |\n'
        f'| Assignees | {assignee_list} |\n'
        f'| Labels    | {label_list} |\n'
    )

    body = (
        '## ✅ PR Meta Check Passed\n\n'
        'All required PR hygiene checks have been satisfied.\n\n'
        f'{summary_table}\n'
        '\nThank you for keeping the pull request metadata consistent and clear.'
    )
    update_pr_comment(owner, repo, pr_number, body, BOT_IDENTIFIER)
    return 0


if __name__ == '__main__':
    sys.exit(main())
