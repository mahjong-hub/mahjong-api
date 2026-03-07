import json
import os
import urllib.request


def github_api(url: str, method: str = 'GET', data=None):
    """Generic GitHub API request."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('Missing GITHUB_TOKEN')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }

    req = urllib.request.Request(url, method=method, headers=headers)

    if data is not None:
        req.data = json.dumps(data).encode('utf-8')

    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def update_pr_comment(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
    identifier: str,
):
    """Create or update a bot comment on a PR, identified by a unique HTML marker."""
    comments_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments'
    comments = github_api(comments_url)

    existing_id = None
    for c in comments:
        if (c.get('body') or '').startswith(identifier):
            existing_id = c['id']
            break

    full_body = f'{identifier}\n{body}'

    if existing_id:
        update_url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{existing_id}'
        github_api(update_url, method='PATCH', data={'body': full_body})
        print(f'Updated comment (id={existing_id})')
    else:
        github_api(comments_url, method='POST', data={'body': full_body})
        print('Created comment')
