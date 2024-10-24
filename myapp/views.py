from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def get_resource(request):
    id_value = request.GET.get('id')
    return JsonResponse({"message": f"Dang Truy Cap Vao id={id_value}"})
