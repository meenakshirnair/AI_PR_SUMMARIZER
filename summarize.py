import os
import sys
import json
from github import Github
from google import genai

def main():
    # 1. Load Secrets & Environment
    token = os.getenv("GH_PAT")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # GitHub Action provides the event path (contains PR info)
    with open(os.getenv('GITHUB_EVENT_PATH')) as f:
        event_data = json.load(f)
    
    repo_name = event_data['repository']['full_name']
    pr_number = event_data['number']

    # 2. Initialize Clients
    gh = Github(token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    client = genai.Client(api_key=gemini_key)

    # 3. Get Code Changes (Diff)
    # We collect the 'patch' (the actual +/- code) from each file
    changes = []
    for file in pr.get_files():
        changes.append(f"File: {file.filename}\n{file.patch}")
    
    diff_text = "\n\n".join(changes)

    # 4. Generate AI Summary
    prompt = (
        "You are a Senior Software Engineer. Summarize the following code changes "
        "from a Pull Request into 3 clear bullet points. "
        "Focus on 'What changed' and 'Why'.\n\n"
        f"{diff_text}"
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )

    # 5. Post the Comment
    comment_body = f"### 🤖 AI Code Review Summary\n\n{response.text}"
    pr.create_issue_comment(comment_body)
    print("Summary posted successfully!")

if __name__ == "__main__":
    main()
