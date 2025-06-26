import os
import requests
from github import Github
import google.generativeai as genai

def get_pr_changes(repo, pr_number):
    """Lấy thông tin thay đổi từ Pull Request."""
    pr = repo.get_pull(pr_number)
    files = pr.get_files()
    changes = []
    
    for file in files:
        # Chỉ xem xét các file code phổ biến
        if file.filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.cs', '.go', '.rb')):
            changes.append({
                'file': file.filename,
                'patch': file.patch,
                'status': file.status
            })
    
    return changes, pr

def analyze_code_changes(model, changes):
    """Phân tích code bằng Gemini API."""
    reviews = []
    
    for change in changes:
        prompt = f"""Hãy review đoạn code sau và cung cấp phản hồi chi tiết bằng tiếng Việt:
        File: {change['file']}
        Thay đổi:
        {change['patch']}
        
        Hãy phân tích các điểm sau:
        1. Chất lượng code và best practices
        2. Các vấn đề tiềm ẩn hoặc bugs
        3. Các vấn đề về bảo mật
        4. Tác động đến hiệu năng
        5. Đề xuất cải thiện
        
        Hãy đưa ra các nhận xét cụ thể và có thể thực hiện được."""

        response = model.generate_content(prompt)
        
        reviews.append({
            'file': change['file'],
            'feedback': response.text
        })
    
    return reviews

def post_github_review(repo, pr_number, reviews):
    """Đăng các nhận xét lên GitHub PR."""
    pr = repo.get_pull(pr_number)
    
    for review in reviews:
        comment = f"🤖 AI Code Review cho file {review['file']}:\n\n{review['feedback']}"
        pr.create_issue_comment(comment)

def send_mattermost_summary(webhook_url, pr_url, reviews):
    """Gửi tổng hợp lên Mattermost."""
    summary = f"### 🤖 Tổng hợp Code Review từ AI\n"
    summary += f"**Pull Request:** {pr_url}\n\n"
    
    for review in reviews:
        summary += f"#### 📝 {review['file']}\n"
        summary += f"{review['feedback']}\n\n"
    
    payload = {
        "text": summary,
        "username": "AI Code Reviewer",
        "icon_emoji": ":robot_face:"
    }
    
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        print(f"Lỗi khi gửi đến Mattermost: {response.status_code}")

def main():
    # Lấy thông tin môi trường
    github_token = os.getenv('GITHUB_TOKEN')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    mattermost_webhook_url = os.getenv('MATTERMOST_WEBHOOK_URL')
    pr_number = int(os.getenv('PR_NUMBER'))
    repo_name = os.getenv('REPO_NAME')
    pr_url = os.getenv('PR_URL')
    
    # Khởi tạo Gemini API
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # Khởi tạo GitHub client
    g = Github(github_token)
    
    # Lấy repository
    repo = g.get_repo(repo_name)
    
    try:
        # Lấy thay đổi từ PR
        print("Đang lấy thông tin thay đổi từ PR...")
        changes, pr = get_pr_changes(repo, pr_number)
        
        if not changes:
            print("Không tìm thấy file code nào cần review.")
            return
        
        # Phân tích code
        print("Đang phân tích code...")
        reviews = analyze_code_changes(model, changes)
        
        # Đăng review lên GitHub
        print("Đang đăng review lên GitHub...")
        post_github_review(repo, pr_number, reviews)
        
        # Gửi tổng hợp lên Mattermost
        print("Đang gửi tổng hợp lên Mattermost...")
        send_mattermost_summary(mattermost_webhook_url, pr_url, reviews)
        
        print("Hoàn thành quá trình review!")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 