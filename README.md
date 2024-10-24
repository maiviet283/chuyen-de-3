# Chuyên Đề 3: Bảo Mật Endpoint bằng Middleware Chống Fuzzing

## Giới Thiệu Đề Bài
Đề tài của chúng ta nhằm mục đích phát hiện và ngăn chặn các cuộc tấn công fuzzing trên các endpoint của ứng dụng web. Trong trường hợp cụ thể này, chúng ta sẽ bảo vệ ứng dụng khỏi kiểu tấn công IDOR (Insecure Direct Object References), nơi hacker cố gắng thay đổi giá trị `id` trong các yêu cầu để truy cập trái phép vào dữ liệu của người dùng khác.

Giả sử một ứng dụng web cung cấp endpoint `/resource/?id=1`, hacker có thể thay đổi tham số `id` một cách liên tục để truy cập vào các tài nguyên khác như `/resource/?id=2`, `/resource/?id=3`,... Nếu số lần thay đổi giá trị `id` vượt quá một ngưỡng cho phép trong thời gian ngắn, chúng ta sẽ coi đây là hành vi tấn công và chặn yêu cầu.

## Giới Thiệu Middleware

Middleware chống fuzzing được phát triển để theo dõi các yêu cầu từ phía người dùng dựa trên địa chỉ IP và tham số `id` của họ. Middleware này hoạt động như sau:

- Theo dõi số lượng thay đổi liên tiếp của tham số `id` trong một khoảng thời gian nhất định.
- Nếu số lần thay đổi vượt quá ngưỡng cho phép (ví dụ 10 lần), yêu cầu sẽ bị chặn và trả về mã lỗi HTTP 403.
- Middleware cũng có thể reset lại bộ đếm nếu không có thay đổi nào trong một thời gian nhất định.

## Cách Middleware Được Code và Hoạt Động

### 1. Cấu Trúc Dự Án
- **myapp**: Ứng dụng chính chứa endpoint và logic xử lý.
- **middleware**: Chứa middleware `IDFuzzingMiddleware` để theo dõi và chặn fuzzing.

### 2. Cách Code Middleware

Middleware `IDFuzzingMiddleware` hoạt động như sau:

- Khi có yêu cầu đến, middleware sẽ lấy địa chỉ IP của người dùng và tham số `id` từ query string.
- Lưu lại thông tin người dùng, bao gồm địa chỉ IP, giá trị `id` cuối cùng, số lần thay đổi `id`, và thời gian bắt đầu theo dõi.
- Nếu số lần thay đổi giá trị `id` liên tiếp vượt quá ngưỡng (mặc định là 10 lần trong vòng 30 giây), middleware sẽ trả về phản hồi chặn yêu cầu với mã 403 (Forbidden).

### 3. Cách Cài Đặt

Để tích hợp middleware này vào dự án Django, ta cần thực hiện các bước sau:

1. Thêm middleware vào danh sách `MIDDLEWARE` trong file `settings.py`:
    ```python
    MIDDLEWARE = [
        ...,
        'myapp.middleware.IDFuzzingMiddleware',
    ]
    ```

2. Thêm endpoint vào file `urls.py` để người dùng có thể truy cập tài nguyên:
    ```python
    from django.urls import path
    from . import views

    urlpatterns = [
        path('resource/', views.get_resource),
    ]
    ```

3. Triển khai logic trong file `views.py` để hiển thị dữ liệu theo `id`:
    ```python
    from django.http import JsonResponse

    def get_resource(request):
        id_value = request.GET.get('id')
        return JsonResponse({"message": f"Accessing resource with id={id_value}"})
    ```

### 4. Cách Middleware Hoạt Động
Khi người dùng gửi nhiều yêu cầu đến `/resource/?id=`, middleware sẽ giám sát các giá trị `id` được yêu cầu. Nếu phát hiện số lần thay đổi `id` vượt quá 10 lần trong vòng 30 giây, middleware sẽ chặn yêu cầu và trả về phản hồi:

```json
{
  "message": "Request blocked due to suspicious behavior"
}