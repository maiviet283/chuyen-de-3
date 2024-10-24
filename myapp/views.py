from django.shortcuts import render

# Create your views here.

def get_resource(request):
    id_value = request.GET.get('id')
    user_ip = request.META.get('REMOTE_ADDR')  # Lấy địa chỉ IP của người dùng

    # Truyền cả IP và ID vào context để hiển thị trên trang
    return render(request, 'myapp/index.html', {
        'message': f"Đang truy cập tài nguyên có ID = {id_value}",
        'user_ip': user_ip
    })
