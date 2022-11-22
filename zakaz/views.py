from django.shortcuts import render
from bot.models import Order, Order_items, BotUsers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


# Create your views here.

def orders(request):
    return render(request, 'orders.html')


def textToList(hashtags):
    return hashtags.strip('[]').replace('\'', '').replace(' ', '').split(',')


@csrf_exempt
@login_required(login_url='/admin/')
def statistics(request):
    orders = Order.objects.all()
    botusers = BotUsers.objects.all()
    order_items = Order_items.objects.all()
    data = {}
    days = {}
    all_days1 = []
    if request.method == 'POST':
        if 'mahsulotlar' in request.POST:
            for i in range(len(order_items)):
                data[order_items[i].product] = order_items[i].count
        else:
            for i in range(len(orders)):
                day = orders[i].created_at
                all_days = textToList(day)
                all_days1.append([all_days[0] + ', ' + all_days[1], orders[i].total_amount])
                if all_days[0] + ', ' + all_days[1] not in days.keys():
                    days[all_days[0] + ', ' + all_days[1]] = orders[i].total_amount
                else:
                    days[all_days[0] + ', ' + all_days[1]] += int(orders[i].total_amount)
            # data = {key: value for key, value in days.items()}
            data = days


    return render(request, 'statistics.html', {"data": data, "count": len(order_items), 'botusers': len(botusers)})
