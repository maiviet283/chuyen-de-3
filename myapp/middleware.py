import time
from django.shortcuts import render

# Thiết lập thời gian và số lần chặn
BLOCK_THRESHOLD = 5  # Số lần chấp nhận thay đổi id
TIME_FRAME = 30  # Thời gian tối đa cho các lần thay đổi liên tiếp (tính bằng giây)
BLOCK_TIME = 45  # Thời gian chặn là 3 tiếng (ở đây tạm đặt là 45 giây cho dễ test)

# Dictionary để theo dõi user theo IP
user_requests = {}

# Dictionary để lưu các IP đã bị chặn
blocked_ips = {}

class IDFuzzingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip = request.META.get('REMOTE_ADDR')  # Lấy IP người dùng
        current_id = request.GET.get('id')  # Lấy tham số ID từ query string
        current_time = time.time()

        # Kiểm tra xem IP có đang bị chặn không
        if user_ip in blocked_ips:
            block_start_time = blocked_ips[user_ip]
            if current_time - block_start_time < BLOCK_TIME:
                # Nếu chưa hết thời gian chặn, render trang chặn
                return render(request, 'myapp/blocked.html', {'message': 'IP của bạn đã bị chặn do hành vi đáng ngờ'}, status=403)
            else:
                # Hết thời gian chặn, xóa IP khỏi danh sách
                del blocked_ips[user_ip]

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
                    # Lưu IP vào danh sách bị chặn và ghi lại thời gian chặn
                    blocked_ips[user_ip] = current_time
                    return render(request, 'myapp/blocked.html', {'message': 'IP của bạn đã bị chặn do hành vi đáng ngờ'}, status=403)

        response = self.get_response(request)
        return response
