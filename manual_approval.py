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
        labels=[label.strip() for label in labels.split(',') if label.strip()],
        assignees=valid_assignees
    )
    print(f"Issue created successfully: {issue.html_url}")

    # Start monitoring for comments
    timeout = timedelta(minutes=timeout_minutes)
    start_time = datetime.now()
    print("Monitoring comments on the issue...")
    print("Only assigned users can approve or deny the issue by commenting 'yes' or 'no'.")

    while True:
        # Refresh issue details
        issue = repo.get_issue(issue.number)

        # Fetch comments
        comments = issue.get_comments()
        for comment in comments:
            comment_author = comment.user.login
            comment_body = comment.body.lower().strip()

            if comment_author in valid_assignees:
                if comment_body == "yes":
                    print(f"Approval received from '{comment_author}'. Closing the issue...")
                    issue.create_comment(f"Approval received from '{comment_author}'. Closing the issue.")
                    issue.edit(state="closed")
                    exit(0)  # Exit with success status
                elif comment_body == "no":
                    print(f"Approval denied by '{comment_author}'. Closing the issue...")
                    issue.create_comment(f"Approval denied by '{comment_author}'. Closing the issue.")
                    issue.edit(state="closed")
                    exit(1)  # Exit with failure status
            else:
                print(f"Ignoring comment from non-assigned user '{comment_author}'.")

        # Check for timeout
        if datetime.now() - start_time >= timeout:
            print("No response from assignees within the timeout period. Closing the issue...")
            issue.create_comment("No response from assignees within the timeout period. Closing the issue.")
            issue.edit(state="closed")
            exit(1)  # Exit with failure status

        print("Awaiting response from assigned users... Retrying in 10 seconds.")
        time.sleep(10)

except GithubException as e:
    print(f"Error while creating or managing the issue: {e}")
    raise
