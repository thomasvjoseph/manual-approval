import os
import time
from datetime import datetime, timedelta
from github import Github

# Environment variables
title = os.getenv('INPUT_TITLE')
token = os.getenv('GITHUB_TOKEN')
labels = os.getenv('INPUT_LABELS')
assignees = os.getenv('INPUT_ASSIGNEES')
body = os.getenv('INPUT_BODY')
validate_assignees = os.getenv('INPUT_VALIDATE_ASSIGNEES', 'false').lower() == 'true'

# Validate GitHub token
if not token:
    raise ValueError("GitHub token is missing. Set 'GITHUB_TOKEN' as an environment variable.")

# Validate title
if not title.strip():
    raise ValueError("Title is missing. Please provide a valid title for the issue.")

# Process labels and assignees
labels = [label.strip() for label in labels.split(',') if label.strip()]
assignees = [assignee.strip() for assignee in assignees.split(',') if assignee.strip()]

# Authenticate using GitHub token
try:
    github = Github(token)
    repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))  # Format: "owner/repo"
except Exception as e:
    raise ValueError(f"Failed to authenticate with GitHub. Error: {e}")

# Create the issue
try:
    issue = repo.create_issue(
        title=title,
        body=body,
        labels=labels,
        assignees=assignees
    )
    print(f"Issue created successfully: {issue.html_url}")

    # Monitoring for comments
    timeout = timedelta(minutes=5)
    start_time = datetime.now()
    print("Monitoring comments on the issue...")
    print("Pending approval. Provide 'yes' or 'no' as a comment on the issue.")

    while True:
        # Refresh issue details
        issue = repo.get_issue(issue.number)

        # Fetch comments
        comments = issue.get_comments()
        for comment in comments:
            comment_author = comment.user.login
            comment_body = comment.body.lower().strip()

            # If assignee validation is enabled, validate the author
            if validate_assignees and comment_author not in assignees:
                print(f"Ignoring comment from non-assigned user '{comment_author}'.")
                continue

            # Process valid comments
            if comment_body == "yes":
                print(f"Approval received from '{comment_author}'. Proceeding with the workflow...")
                issue.create_comment(f"Approval received from '{comment_author}'. Closing the issue.")
                issue.edit(state="closed")
                exit(0)  # Exit with success status to continue the workflow
            elif comment_body == "no":
                print(f"Approval denied by '{comment_author}'. Stopping the workflow...")
                issue.create_comment(f"Approval denied by '{comment_author}'. Closing the issue.")
                issue.edit(state="closed")
                exit(1)  # Exit with failure status to stop the workflow

        # Check for timeout
        if datetime.now() - start_time >= timeout:
            print("No response within the timeout. Stopping the workflow...")
            issue.create_comment("No response within the timeout. Closing the issue.")
            issue.edit(state="closed")
            exit(1)

        print("Awaiting approval... Retrying in 10 seconds.")
        time.sleep(10)

except Exception as e:
    print(f"An error occurred: {e}")
    raise
