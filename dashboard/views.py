from importlib.resources import read_binary
from itertools import product
from django.shortcuts import render
from pyparsing import Or

from bot.models import BotUsers, Branch, Order, Order_items
from datetime import datetime, date, timedelta
from bot.models import Order, Order_items
# Create your views here.

def dashboard(request):
    orders = Order.objects.all()
    revenue = 0
    for i in orders:
        revenue += i.total_amount
    order_items = Order_items.objects.all()
    botusers = BotUsers.objects.all()
    context = {"count_user": len(botusers), "count_orders": len(order_items), "revenue": revenue}
    return render(request, "admin_lte/index.html", context)




def textToList(hashtags):
    return hashtags.strip('[]').replace('\'', '').replace(' ', '').split(',')


def statistics(request, period=None):
    branches = Branch.objects.all()
    label = []
    day1 = 0
    day2 = date.today()

    data = []
    if period == "weekly":
        day1 = date.today() - timedelta(days=7)
        data = {}
        label = [(day1 + timedelta(days=i+1)).day for i in range(7)]
        # geting them with their dates but need to seperate with their branch name
        for j in range(1, len(branches)):
            data[branches[j].name] = [0 for i in range(7)]
            count = 0
            for i in range(7):
                day_for_label = day1 + timedelta(days=i+1)
                orders = Order.objects.filter(branch_name=branches[j].name, date_ordered = day_for_label)
                for k in orders:
                    count += k.total_amount
                data[branches[j].name][i] = count
                count = 0
            branches[j].data_for_statistics = data[branches[j].name]
            branches[j].total_for_statistics = sum(data[branches[j].name])
            branches[j].save()

    elif period == "monthly":
        day1 = date.today() - timedelta(days=30)
        data = {}
        label = [(day1 + timedelta(days=i+1)).day for i in range(30)]
        # geting them with their dates but need to seperate with their branch name
        for j in range(1, len(branches)):
            data[branches[j].name] = [0 for i in range(30)]
            count = 0
            for i in range(30):
                day_for_label = day1 + timedelta(days=i+1)
                orders = Order.objects.filter(branch_name=branches[j].name, date_ordered = day_for_label)
                for k in orders:
                    count += k.total_amount
                data[branches[j].name][i] = count
                count = 0
            branches[j].data_for_statistics = data[branches[j].name]
            branches[j].total_for_statistics = sum(data[branches[j].name])
            branches[j].save()

    elif period == "yearly":
        data = {}
        label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for j in range(1, len(branches)):
            data[branches[j].name] = [0 for i in range(12)]
            count = 0
            for i in range(12):
                orders = Order.objects.filter(branch_name=branches[j].name, date_ordered__year = day2.year, date_ordered__month = i+1)
                for k in orders:
                    count += k.total_amount
                data[branches[j].name][i] = count
                count = 0

            branches[j].data_for_statistics = data[branches[j].name]
            branches[j].total_for_statistics = sum(data[branches[j].name])
            branches[j].save()
        
    if period == "daily":
        label = [str(day2)]
        data = {}
        for j in range(1, len(branches)):
            data[branches[j].name] = [0 for i in range(1)]
            count = 0
            for i in range(1):
                orders = Order.objects.filter(branch_name=branches[j].name, date_ordered = day2)
                for k in orders:
                    count += k.total_amount
                data[branches[j].name][i] = count
                count = 0
            
            branches[j].data_for_statistics = data[branches[j].name]
            branches[j].total_for_statistics = sum(data[branches[j].name])
            branches[j].save()
        
    if period == "all":
        data = {}
        label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for j in range(1, len(branches)):
            data[branches[j].name] = [0 for i in range(12)]
            count = 0
            for i in range(12):
                orders = Order.objects.filter(branch_name=branches[j].name, date_ordered__year = day2.year, date_ordered__month = i+1)
                for k in orders:
                    count += k.total_amount
                data[branches[j].name][i] = count
                count = 0

            branches[j].data_for_statistics = data[branches[j].name]
            branches[j].save()



    context = {"branches": branches, "label": label}
    return render(request, "admin_lte/statistics.html", context)

def statisticss(request, period=None):
    once_done = False

    orders = Order.objects.all()
    botusers = BotUsers.objects.all()
    order_items = Order_items.objects.all()
    monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    data = {}
    days = {}
    all_days1 = []
    count = len(orders) - 1
    
    # for i in range(len(orders)):
    #     day = orders[i].created_at
    #     day_now = orders[count].created_at
    #     count -= 1
    #     all_days = textToList(day)
    #     all_days_now = textToList(day_now)
    #     if once_done == False:
    #         first_day = datetime.date(int(all_days_now[-1]), int(monthDict[all_days_now[0]]), int(all_days_now[1]))
    #         once_done = True
    #     the_other_day = datetime.date(int(all_days[-1]), int(monthDict[all_days[0]]), int(all_days[1]))
    #     days_between = (first_day - the_other_day).days

    #     if period == "weekly" and days_between <= 7:
    #         all_days1.append([all_days[0] + ',' + all_days[1] + ',' + all_days[-1], orders[i].total_amount])
        
    #         if all_days[0] + ',' + all_days[1] + ',' + all_days[-1] not in days.keys():
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] = orders[i].total_amount
    #         else:
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] += int(orders[i].total_amount)
    #         data = days

    #     elif period == "monthly" and first_day.month == the_other_day.month and first_day.year == the_other_day.year:
    #         all_days1.append([all_days[0] + ',' + all_days[1] + ',' + all_days[-1], orders[i].total_amount])
        
    #         if all_days[0] + ',' + all_days[1] + ',' + all_days[-1] not in days.keys():
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] = orders[i].total_amount
    #         else:
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] += int(orders[i].total_amount)
    #         data = days

    #     elif period == "yearly" and first_day.year == the_other_day.year:
    #         all_days1.append([all_days[0] + ',' + all_days[1] + ',' + all_days[-1], orders[i].total_amount])
        
    #         if all_days[0] + ',' + all_days[1] + ',' + all_days[-1] not in days.keys():
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] = orders[i].total_amount
    #         else:
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] += int(orders[i].total_amount)
    #         data = days

    #     elif period == "all":
    #         all_days1.append([all_days[0] + ',' + all_days[1] + ',' + all_days[-1], orders[i].total_amount])
        
    #         if all_days[0] + ',' + all_days[1] + ',' + all_days[-1] not in days.keys():
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] = orders[i].total_amount
    #         else:
    #             days[all_days[0] + ',' + all_days[1] +',' + all_days[-1]] += int(orders[i].total_amount)
    #         data = days
            
    #     else:
    #         pass

        
    context = {"data": data, "count_user": len(botusers), "count_orders": len(order_items), "revenue": 100000}
    return render(request, "admin_lte/statistics.html", context)




def smm(request):
    orders = Order.objects.all()
    revenue = 0
    for i in orders:
        revenue += i.total_amount
    order_items = Order_items.objects.all()
    botusers = BotUsers.objects.all()
    context = {"count_user": len(botusers), "count_orders": len(order_items), "revenue": revenue}
    return render(request, "admin_lte/general.html", context)




def mahsuloatlar_statistikasi(request):
    branches = Branch.objects.all()
    data = {}
    selected_branch = None
    day_range = None
    if request.method == "POST":
        day_range = request.POST['day_range']
        selected_branch_id = request.POST['branches']
        selected_branch = Branch.objects.get(id=selected_branch_id)
        day_range_list = day_range.split(' - ')
        day1 = datetime.strptime(day_range_list[0], '%m/%d/%Y')
        day2 = datetime.strptime(day_range_list[1], '%m/%d/%Y')
        order_items = Order_items.objects.filter(branch_name=selected_branch.name, date_ordered__range=(day1, day2))

        for i in order_items:
            if i.product not in data.keys():
                data[i.product] = i.count
            else:
                data[i.product] += i.count 
    context = {
            "data": data, 
            "branches": branches, 
            "count_branches": len(branches), 
            "selected_branch": selected_branch,
            "day_range": day_range
        }
        
    return render(request, "admin_lte/pages/tables/data.html", context)