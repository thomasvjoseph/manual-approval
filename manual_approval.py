import os
from github import Github
import time
from datetime import datetime, timedelta

# Environment variables
title = os.getenv('INPUT_TITLE') 
token = os.getenv('GITHUB_TOKEN')
labels = os.getenv('INPUT_LABELS')
assignees = os.getenv('INPUT_ASSIGNEES')
body = os.getenv('INPUT_BODY')

# Validate title
if not title:
    raise ValueError("Title is missing. Please provide a valid title for the issue.")

# If labels are provided, split by ',' to make it a list
if labels:
    labels = [label.strip() for label in labels.split(',') if label.strip()]
else:
    labels = []

# Validate and filter assignees
if assignees:
    assignees = [assignee.strip() for assignee in assignees.split(',') if assignee.strip()]
else:
    assignees = []

# Authenticate using GitHub token
github = Github(token)
repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))  # Format: "owner/repo"

# Create the issue
try:
    issue = repo.create_issue(
        title=title,
        body=body,
        assignees=assignees,
        labels=labels
    )
    print(f"Issue created successfully: {issue.html_url}")

    # Define timeout for no comments
    timeout = timedelta(minutes=30)
    start_time = datetime.now()

    print("Pending approval. Provide 'yes' or 'no' as a comment on the issue.")

    while True:
        # Refresh issue details
        issue = repo.get_issue(issue.number)

        # Fetch comments
        comments = issue.get_comments()
        yes_found = any("yes" in comment.body.lower().strip() for comment in comments)
        no_found = any("no" in comment.body.lower().strip() for comment in comments)

        # If "yes" is found, close the issue and proceed with the workflow
        if yes_found:
            print("Approval received: 'yes'. Proceeding with the workflow...")
            issue.create_comment("Approval received: 'yes'. Closing the issue.")
            issue.edit(state="closed")
            exit(0)  # Exit with success status to continue the workflow

        # If "no" is found, close the issue and stop the workflow
        if no_found:
            print("Approval denied: 'no'. Stopping the workflow...")
            issue.create_comment("Approval denied: 'no'. Closing the issue.")
            issue.edit(state="closed")
            exit(1)  # Exit with failure status to stop the workflow

        # If no comments, check the timeout
        if not comments:
            elapsed_time = datetime.now() - start_time
            if elapsed_time < timeout:
                print("Pending approval. Waiting for 'yes' or 'no' comment...")
            else:
                print("No response within the timeout. Stopping the workflow...")
                issue.create_comment("No response within the time frame. Closing the issue.")
                issue.edit(state="closed")
                exit(1)  # Exit with failure status to stop the workflow
        else:
            print("Comment detected. Waiting for 'yes' or 'no' to decide...")

        # Sleep briefly to reduce API usage
        time.sleep(10)

except Exception as e:
    print(f"Error: {e}")
    raise