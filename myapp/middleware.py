import time
from django.http import JsonResponse

# Thiết lập thời gian và số lần chặn
BLOCK_THRESHOLD = 5  # Số lần chấp nhận thay đổi id
TIME_FRAME = 30  # Thời gian tối đa cho các lần thay đổi liên tiếp (tính bằng giây)

# Dictionary để theo dõi user theo IP
user_requests = {}

class IDFuzzingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip = request.META.get('REMOTE_ADDR')  # Lấy IP người dùng
        current_id = request.GET.get('id')  # Lấy tham số ID từ query string
        current_time = time.time()

        # Kiểm tra nếu user đã có trong danh sách theo dõi
        if user_ip not in user_requests:
            user_requests[user_ip] = {
                'last_id': current_id,
                'count': 1,
                'start_time': current_time
            }
        else:
            user_data = user_requests[user_ip]

            # Kiểm tra thời gian nếu quá TIME_FRAME thì reset
            if current_time - user_data['start_time'] > TIME_FRAME:
                user_requests[user_ip] = {
                    'last_id': current_id,
                    'count': 1,
                    'start_time': current_time
                }
            else:
                # Nếu id thay đổi liên tiếp (tăng hoặc giảm)
                if current_id != user_data['last_id']:
                    user_data['count'] += 1
                    user_data['last_id'] = current_id
                else:
                    user_data['count'] = 1

                # Nếu vượt quá giới hạn số lần thay đổi id, chặn yêu cầu
                if user_data['count'] > BLOCK_THRESHOLD:
                    return JsonResponse({"message": "Cut"}, status=403)

        response = self.get_response(request)
        return response
