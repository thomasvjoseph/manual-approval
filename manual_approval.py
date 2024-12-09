import os
import time
from datetime import datetime, timedelta
from github import Github, GithubException

# Environment variables
token = os.getenv('GITHUB_TOKEN')
title = os.getenv('INPUT_TITLE', 'Manual Approval')
labels = os.getenv('INPUT_LABELS', '')
assignees = os.getenv('INPUT_ASSIGNEES', '')
body = os.getenv('INPUT_BODY', 'Provide approval as yes or no.')
timeout_minutes = int(os.getenv('INPUT_TIMEOUT', '5'))  # Default timeout in minutes
min_approvers = int(os.getenv('INPUT_MIN_APPROVERS', '1'))  # Minimum approvals required

# Authenticate using GitHub token
if not token:
    raise ValueError("GitHub token is missing. Set 'GITHUB_TOKEN' as an environment variable.")

try:
    github = Github(token)
    repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))  # Format: "owner/repo"
except GithubException as e:
    raise ValueError(f"Failed to authenticate or access repository. Error: {e}")

# Process assignees
assignees = [assignee.strip() for assignee in assignees.split(',') if assignee.strip()]
valid_assignees = []

if assignees:
    print("Validating assignees...")
    repo_collaborators = [collaborator.login for collaborator in repo.get_collaborators()]
    for assignee in assignees:
        if assignee in repo_collaborators:
            valid_assignees.append(assignee)
        else:
            print(f"Warning: '{assignee}' is not a collaborator or has insufficient permissions. Skipping.")

# Create the issue
try:
    issue = repo.create_issue(
        title=title,
        body=body,
        labels=[label.strip() for label in labels.split(',') if label.strip()]
    )
    print(f"Issue created successfully: {issue.html_url}")

    # Explicitly assign users
    if valid_assignees:
        print(f"Assigning issue to: {', '.join(valid_assignees)}")
        try:
            issue.edit(assignees=valid_assignees)
            print("Issue successfully assigned to all valid assignees.")
        except GithubException as e:
            print(f"Error assigning issue to all assignees: {e}")
    else:
        print("No valid assignees. Proceeding without assigning.")

    # Start monitoring for comments
    timeout = timedelta(minutes=timeout_minutes)
    start_time = datetime.now()
    print("Monitoring comments on the issue...")
    print(f"At least {min_approvers} approval(s) required to close the issue.")

    approvals = set()
    while True:
        # Refresh issue details
        issue = repo.get_issue(issue.number)

        # Fetch comments
        comments = issue.get_comments()
        for comment in comments:
            comment_author = comment.user.login
            comment_body = comment.body.lower().strip()

            if not valid_assignees or comment_author in valid_assignees:
                if comment_body == "yes":
                    approvals.add(comment_author)
                    print(f"Approval received from '{comment_author}'. Total approvals: {len(approvals)}.")

                    if len(approvals) >= min_approvers:
                        print(f"Minimum approvals met. Closing the issue...")
                        issue.create_comment(
                            f"Minimum approvals ({min_approvers}) received. Closing the issue."
                        )
                        issue.edit(state="closed")
                        exit(0)  # Exit with success status

                elif comment_body == "no":
                    print(f"Rejection received from '{comment_author}'. Closing the issue...")
                    issue.create_comment(f"Rejection received from '{comment_author}'. Closing the issue.")
                    issue.edit(state="closed")
                    exit(1)  # Exit with failure status
            else:
                print(f"Ignoring comment from non-assigned user '{comment_author}'.")

        # Check for timeout
        if datetime.now() - start_time >= timeout:
            print("No response within the timeout period. Closing the issue...")
            issue.create_comment("No response within the timeout period. Closing the issue.")
            issue.edit(state="closed")
            exit(1)  # Exit with failure status

        print("Awaiting response... Retrying in 10 seconds.")
        time.sleep(10)

except GithubException as e:
    print(f"Error while creating or managing the issue: {e}")
    raise