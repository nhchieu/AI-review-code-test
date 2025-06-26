# AI Code Review Bot

Bot AI tự động review code khi có Pull Request và gửi thông báo lên Mattermost.

## Tính năng

- Tự động kích hoạt khi có Pull Request mới hoặc cập nhật
- Phân tích code thay đổi sử dụng GPT-4
- Đăng comment review trực tiếp trên GitHub PR
- Gửi báo cáo tổng hợp lên Mattermost
- Hỗ trợ nhiều ngôn ngữ lập trình (Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby)

## Cài đặt

1. Thêm các secrets sau vào repository GitHub:

   - `OPENAI_API_KEY`: API key của OpenAI
   - `MATTERMOST_WEBHOOK_URL`: URL webhook của Mattermost

2. `GITHUB_TOKEN` sẽ được GitHub Actions tự động cung cấp

3. Bot sẽ tự động chạy khi có Pull Request

## Cách hoạt động

1. Khi có Pull Request mới hoặc cập nhật, action sẽ được kích hoạt
2. Bot sẽ phân tích các thay đổi code bằng GPT-4
3. Đăng các nhận xét chi tiết lên Pull Request
4. Gửi bản tổng hợp lên Mattermost

## Cấu hình

Bot được cấu hình để:
- Chạy khi có sự kiện Pull Request (tạo mới và cập nhật)
- Review các file có đuôi: .py, .js, .ts, .jsx, .tsx, .java, .cpp, .cs, .go, .rb
- Sử dụng GPT-4 để phân tích code
- Đăng cả comment chi tiết và bản tổng hợp

## Yêu cầu

- Python 3.10 trở lên
- OpenAI API
- PyGithub
- Requests

## Giấy phép

MIT 