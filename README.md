# Manual Approval GitHub Action

This GitHub Action allows you to create an issue on your repository that requires manual approval through comments. Assignees of the issue (or any user if no assignees are set) can approve or reject the issue by commenting `"yes"` or `"no"` on the issue.
The action can also be configured to require a minimum number of approvals if multiple assignees are set.

## Features
- Creates an issue for manual approval.
- Only allows assignees (or anyone if no assignees are specified) to approve or reject.
- Tracks approvals and rejections based on user comments.
- Optionally requires a minimum number of approvals for closing the issue.

## Inputs

| Input Name          | Description                                                              | Default               |
| ------------------- | ------------------------------------------------------------------------ | --------------------- |
| `INPUT_TITLE`        | Title of the issue to be created.                                        | `Manual Approval`     |
| `INPUT_BODY`         | Body of the issue. This should include instructions for users to approve or reject. | `Provide approval as yes or no.` |
| `INPUT_LABELS`       | A comma-separated list of labels to apply to the issue.                  | `""` (empty)          |
| `INPUT_ASSIGNEES`    | A comma-separated list of assignees for the issue. If not provided, anyone can approve/reject. | `""` (empty)          |
| `INPUT_TIMEOUT`      | Timeout period (in minutes) for waiting for approval. If no comment is received within this time, the issue will be closed. | `5`                   |
| `INPUT_MIN_APPROVERS`| Minimum number of approvals required to close the issue. Only applicable when there are multiple assignees. | `1`                   |

## Outputs

This action does not produce any direct outputs, but it will close the issue with a success or failure status based on the comments received.

## Usage

### Workflow Example

```yaml
name: Manual Approval Workflow

on:
  push:
    branches:
      - main

jobs:
  approval:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Request approval
        uses: yourusername/manual-approval@v0.1.0
        with:
          INPUT_TITLE: "Manual Approval Request"
          INPUT_BODY: "Please approve or reject by commenting 'yes' or 'no'."
          INPUT_ASSIGNEES: "user1,user2"
          INPUT_MIN_APPROVERS: 1
          INPUT_TIMEOUT: 10

```

## How it Works

	1.	When the workflow is triggered, it creates an issue with the title and body you provide.
	2.	If you have set assignees, only those users can approve or reject the issue by commenting "yes" or "no".
	3.	If the number of approvals meets the INPUT_MIN_APPROVERS threshold, the issue will be closed with a success message.
	4.	If any assignee comments "no", the issue will be closed with a rejection message.
	5.	If no approval is received within the specified timeout (INPUT_TIMEOUT), the issue will be closed with a failure message.

## Example Use Cases

	•	Single Assignee: If you have only one assignee, the workflow will proceed when that assignee approves or rejects the issue.
	•	Multiple Assignees: If you have multiple assignees, you can set a minimum number of approvals required to close the issue.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests. If you have suggestions or find any bugs, open an issue to discuss them.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.


## Author:  
thomas joseph
- [linkedin](https://www.linkedin.com/in/thomas-joseph-88792b132/)
- [medium](https://medium.com/@thomasvjoseph)
