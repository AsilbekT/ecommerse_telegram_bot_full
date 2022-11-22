from datetime import datetime, timedelta
from venv import create
from django.shortcuts import render
from django.http import HttpResponse
from api.serializer import OrderSerializer
from bot.models import Order, Order_items
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Create your views here.

@api_view(['GET', 'POST'])
def get_total_amount_by_days(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        order = Order.objects.all()
        today = datetime.today()
        try:
            how_many_days = int(request.data['days'])
        except:
            return Response({"error": "Iltimos attribute ga 'days' deb nechi kunlig keregligini kiriting!"})
        wanted_day = today - timedelta(days=how_many_days)
        days_list = []
        result_all_days = []
        result_all_days_final = []
        count_total = 0
        months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        delta = today - wanted_day
        for i in range(delta.days+ 1):
            day = wanted_day + timedelta(days=i)
            days_list.append(day.day)
            result_all_days.append({"day": day.strftime("%x"), "total": 0})
        a = 0
        b = 0
        for i in order:
            created_at = eval(i.created_at)
            wanted_date_real = datetime(int(created_at[-1]), months[created_at[0]], int(created_at[1]))
            formated_day = wanted_date_real.strftime("%x")
            for j in result_all_days:
                if formated_day == j['day']:
                    count_total += i.total_amount
                    j['total'] += i.total_amount
        result_all_days_final.append({"total": count_total})
        result_all_days_final[0]["details"] = result_all_days
        return Response(result_all_days_final[0])




