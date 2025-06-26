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
        if file.filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.cs', '.go', '.rb')):
            changes.append({
                'file': file.filename,
                'patch': file.patch,
                'status': file.status,
                'additions': file.additions,
                'deletions': file.deletions,
                'changes': file.changes
            })
    
    return changes, pr

def analyze_code_changes(model, changes):
    """Phân tích code với cả góc nhìn cơ bản và chuyên sâu."""
    reviews = []
    
    for change in changes:
        prompt = f"""Với vai trò là một Tech Lead có nhiều năm kinh nghiệm, hãy review đoạn code sau với cả góc nhìn cơ bản và chuyên sâu:

File: {change['file']}
Số dòng thêm mới: {change['additions']}
Số dòng xóa: {change['deletions']}
Tổng thay đổi: {change['changes']}

Thay đổi chi tiết:
{change['patch']}

A. PHÂN TÍCH CƠ BẢN (Bắt buộc phải check):
1. SYNTAX & CODING STANDARDS:
   - Kiểm tra lỗi cú pháp
   - Kiểm tra coding style (indentation, spacing)
   - Kiểm tra naming conventions
   - Format code

2. LOGIC ERRORS:
   - Kiểm tra logic flow
   - Điều kiện if-else
   - Vòng lặp
   - Xử lý null/undefined
   - Type checking

3. COMMON BUGS:
   - Off-by-one errors
   - Null pointer exceptions
   - Memory leaks
   - Resource management
   - Exception handling

4. CODE SMELLS:
   - Duplicate code
   - Long methods
   - Large classes
   - Complex conditions
   - Magic numbers/strings

B. PHÂN TÍCH CHUYÊN SÂU:
1. ĐÁNH GIÁ KIẾN TRÚC VÀ THIẾT KẾ:
   - Code có phù hợp với kiến trúc tổng thể không?
   - Có tuân thủ các design patterns phù hợp không?
   - Đánh giá tính mở rộng và khả năng tái sử dụng

2. ĐÁNH GIÁ BUSINESS LOGIC:
   - Logic nghiệp vụ có được xử lý đúng không?
   - Có xử lý đầy đủ các edge cases không?
   - Có phù hợp với yêu cầu business không?

3. PHÂN TÍCH TÁC ĐỘNG HỆ THỐNG:
   - Ảnh hưởng đến hiệu năng hệ thống
   - Tác động đến các thành phần khác
   - Khả năng scale của giải pháp

4. RỦI RO VÀ BẢO MẬT:
   - Các rủi ro tiềm ẩn
   - Lỗ hổng bảo mật có thể có
   - Cách xử lý dữ liệu nhạy cảm

C. HƯỚNG DẪN KHẮC PHỤC:
1. LỖI SYNTAX & LOGIC:
   - Chỉ ra vị trí lỗi cụ thể
   - Cung cấp code mẫu để sửa
   - Giải thích cách khắc phục

2. CẢI THIỆN CODE:
   - Đề xuất refactoring
   - Cách tối ưu hiệu năng
   - Best practices nên áp dụng

3. KINH NGHIỆM THỰC TẾ:
   - Chia sẻ các bài học từ thực tế
   - Các vấn đề thường gặp và cách phòng tránh
   - Tips và tricks

Yêu cầu đặc biệt:
1. Với mỗi lỗi syntax hoặc logic, phải cung cấp:
   - Vị trí chính xác của lỗi
   - Code mẫu để sửa
   - Giải thích tại sao cần sửa

2. Với các vấn đề về hiệu năng hoặc bảo mật:
   - Đánh giá mức độ nghiêm trọng
   - Ưu tiên các vấn đề cần xử lý ngay
   - Đề xuất giải pháp cụ thể

Hãy đưa ra nhận xét chi tiết, thực tế và có tính xây dựng. Ưu tiên các vấn đề syntax và logic trước, sau đó mới đến các góc nhìn chuyên sâu khác."""

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
        comment = f"""## 🔍 Code Review chi tiết

### 📝 File: {review['file']}

{review['feedback']}

---
> 💡 Bot này sử dụng AI để phân tích code với góc nhìn của một Tech Lead, tập trung vào các khía cạnh thực tế và kinh nghiệm chuyên sâu.
"""
        pr.create_issue_comment(comment)

def get_telegram_chat_id(bot_token):
    """Lấy chat ID của group đầu tiên mà bot là thành viên."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        updates = response.json()
        if updates.get('result'):
            for update in updates['result']:
                if update.get('message', {}).get('chat', {}).get('type') in ['group', 'supergroup']:
                    return update['message']['chat']['id']
                elif update.get('message', {}).get('chat', {}).get('type') == 'private':
                    return update['message']['chat']['id']
    
    return None

def send_telegram_message(bot_token, message):
    """Gửi tin nhắn qua Telegram."""
    chat_id = get_telegram_chat_id(bot_token)
    if not chat_id:
        print("Không tìm thấy chat ID. Hãy đảm bảo bot đã được thêm vào group hoặc đã nhận tin nhắn.")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Telegram có giới hạn 4096 ký tự cho mỗi tin nhắn
    max_length = 4000
    
    for i in range(0, len(message), max_length):
        chunk = message[i:i + max_length]
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Lỗi khi gửi tin nhắn Telegram: {response.status_code}")
            print(response.text)

def send_review_summary(bot_token, pr_url, reviews):
    """Gửi tổng hợp review qua Telegram."""
    summary = f"""*🔍 PHÂN TÍCH CODE CHI TIẾT*

*Pull Request:* {pr_url}

*📊 Tổng quan:*
- Số files được review: {len(reviews)}
"""
    
    for review in reviews:
        summary += f"""
*📝 File: {review['file']}*
{review['feedback']}

*-----------------------------------*
"""
    
    send_telegram_message(bot_token, summary)

def main():
    # Lấy thông tin môi trường
    github_token = os.getenv('GITHUB_TOKEN')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
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
        
        # Gửi tổng hợp qua Telegram
        print("Đang gửi tổng hợp qua Telegram...")
        send_review_summary(telegram_bot_token, pr_url, reviews)
        
        print("Hoàn thành quá trình review!")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 