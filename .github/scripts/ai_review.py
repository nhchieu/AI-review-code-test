import os
import sys
import google.generativeai as genai
from github import Github
import telegram
import asyncio
from typing import List, Dict
import json

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configure GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
gh = Github(GITHUB_TOKEN)

# Configure Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

def get_pr_files() -> List[Dict]:
    """Get the files changed in the PR"""
    event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(event_path, 'r') as f:
        event = json.load(f)
    
    repo = gh.get_repo(event['repository']['full_name'])
    pr = repo.get_pull(event['pull_request']['number'])
    
    files = []
    for file in pr.get_files():
from github import Github
import telegram
import asyncio
from typing import List, Dict
import json

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configure GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
gh = Github(GITHUB_TOKEN)

# Configure Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

def get_pr_files() -> List[Dict]:
    """Get the files changed in the PR"""
    event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(event_path, 'r') as f:
        event = json.load(f)
    
    repo = gh.get_repo(event['repository']['full_name'])
    pr = repo.get_pull(event['pull_request']['number'])
    
    files = []
    for file in pr.get_files():
        if file.filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.cs', '.go', '.rb')):
            files.append({
                'filename': file.filename,
                'content': file.patch,
                'raw_url': file.raw_url
            })
    return files

def review_code(content: str, filename: str) -> str:
    """Review code using Gemini API"""
    prompt = f"""
    Please review the following code from file {filename}. Focus on:
    1. Code style and best practices
    2. Potential bugs and security issues
    3. Performance considerations
    4. Architecture and design patterns
    5. Maintainability and readability

    Provide specific recommendations for improvements.
    
    Code to review:
    {content}
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_review_comment(review: str, pr_number: int, repo_name: str):
    """Post review comment on GitHub PR"""
    repo = gh.get_repo(repo_name)
            files.append({
                'filename': file.filename,
                'content': file.patch,
                'raw_url': file.raw_url
            })
    return files

def review_code(content: str, filename: str) -> str:
    """Review code using Gemini API"""
    prompt = f"""
    Please review the following code from file {filename}. Focus on:
    1. Code style and best practices
    2. Potential bugs and security issues
    3. Performance considerations
    4. Architecture and design patterns
    5. Maintainability and readability

    Provide specific recommendations for improvements.
    
    Code to review:
    {content}
    """
    
    response = model.generate_content(prompt)
    return response.text

def post_review_comment(review: str, pr_number: int, repo_name: str):
    """Post review comment on GitHub PR"""
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(review)

async def send_telegram_notification(message: str):
    """Send notification to Telegram"""
    if bot and TELEGRAM_CHAT_ID:
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
    pr.create_issue_comment(review)

async def send_telegram_notification(message: str):
    """Send notification to Telegram"""
    if bot and TELEGRAM_CHAT_ID:
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")

def main():
    try:
        # Get PR files
        files = get_pr_files()
    try:
        # Get PR files
        files = get_pr_files()
        
        if not files:
            print("No supported files found in PR")
        if not files:
            print("No supported files found in PR")
            return
        
        # Review each file
        for file in files:
            review = review_code(file['content'], file['filename'])
            
            # Post review on GitHub
            event_path = os.getenv('GITHUB_EVENT_PATH')
            with open(event_path, 'r') as f:
                event = json.load(f)
            
            repo_name = event['repository']['full_name']
            pr_number = event['pull_request']['number']
            
            comment = f"## AI Code Review for `{file['filename']}`\n\n{review}"
            post_review_comment(comment, pr_number, repo_name)
            
            # Send Telegram notification
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                notification = f"New code review posted for {file['filename']} in PR #{pr_number}"
                asyncio.run(send_telegram_notification(notification))
            
        # Review each file
        for file in files:
            review = review_code(file['content'], file['filename'])
            
            # Post review on GitHub
            event_path = os.getenv('GITHUB_EVENT_PATH')
            with open(event_path, 'r') as f:
                event = json.load(f)
            
            repo_name = event['repository']['full_name']
            pr_number = event['pull_request']['number']
            
            comment = f"## AI Code Review for `{file['filename']}`\n\n{review}"
            post_review_comment(comment, pr_number, repo_name)
            
            # Send Telegram notification
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                notification = f"New code review posted for {file['filename']} in PR #{pr_number}"
                asyncio.run(send_telegram_notification(notification))
            
    except Exception as e:
        print(f"Error during code review: {e}")
        sys.exit(1)
        print(f"Error during code review: {e}")
        sys.exit(1)

if __name__ == '__main__':
if __name__ == '__main__':
    main() 