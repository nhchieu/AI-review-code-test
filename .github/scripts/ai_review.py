import os
import sys
import json
import asyncio
from typing import List, Dict
import google.generativeai as genai
from github import Github
import telegram

def validate_env_vars():
    """Validate required environment variables"""
    required_vars = {
        'GITHUB_TOKEN': 'GitHub access token',
        'GOOGLE_API_KEY': 'Google API key',
        'GITHUB_EVENT_PATH': 'GitHub event path'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        sys.exit(1)

# Validate environment variables
validate_env_vars()

# Configure Gemini API
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Initialize model with specific model name
    print("Initializing Gemini Flash 2.0 model...")
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    print("Model initialized successfully!")
except Exception as e:
    print(f"Error configuring Gemini API: {str(e)}")
    sys.exit(1)

# Configure GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
gh = Github(GITHUB_TOKEN)

# Configure Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

def get_pr_files() -> List[Dict]:
    """Get the files changed in the PR"""
    try:
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
    except Exception as e:
        print(f"Error getting PR files: {str(e)}")
        raise

def review_code(content: str, filename: str) -> str:
    """Review code using Gemini API"""
    try:
        prompt = f"""
        Hãy review đoạn code sau từ file {filename}. Tập trung phân tích các vấn đề sau:

        1. Lỗi cú pháp và vi phạm quy tắc coding:
           - Chỉ ra chính xác dòng code có vấn đề
           - Giải thích tại sao đó là lỗi
           - Đề xuất cách sửa

        2. Các lỗ hổng bảo mật:
           - Xác định vị trí có nguy cơ bảo mật
           - Mô tả chi tiết mối nguy hiểm
           - Đề xuất biện pháp khắc phục

        3. Lỗi tiềm ẩn và vấn đề về hiệu năng:
           - Chỉ ra các đoạn code có thể gây lỗi runtime
           - Xác định các vấn đề về memory leak, race condition
           - Đề xuất cách tối ưu

        Lưu ý:
        - Chỉ tập trung vào các vấn đề, KHÔNG đề cập ưu điểm
        - Với mỗi vấn đề, cần chỉ rõ vị trí (số dòng) trong code và đưa ra đoạn code có vấn đề
        - Đề xuất cách sửa phải cụ thể và có thể áp dụng ngay
        
        Code cần review:
        {content}
        """
        
        response = model.generate_content(prompt)
        if not response or not response.text:
            return "Error: Unable to generate review. Please check the API configuration."
        return response.text
    except Exception as e:
        print(f"Error reviewing code: {str(e)}")
        raise

def post_review_comment(review: str, pr_number: int, repo_name: str):
    """Post review comment on GitHub PR"""
    try:
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(review)
    except Exception as e:
        print(f"Error posting review comment: {str(e)}")
        raise

async def send_telegram_notification(message: str):
    """Send notification to Telegram"""
    if bot and TELEGRAM_CHAT_ID:
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
            # Don't raise the error as Telegram notification is optional

def main():
    try:
        # Get PR files
        files = get_pr_files()
        
        if not files:
            print("No supported files found in PR")
            return
        
        # Review each file
        for file in files:
            try:
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
                print(f"Error processing file {file['filename']}: {str(e)}")
                continue
            
    except Exception as e:
        print(f"Error during code review: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 