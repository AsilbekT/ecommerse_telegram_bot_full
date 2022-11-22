from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import requests
from django.core.exceptions import ObjectDoesNotExist
import json
import time
from django.core import serializers
from geopy.geocoders import Nominatim
from django.views.decorators.csrf import csrf_exempt
from .models import (
    BotUsers,
    Branch,
    JoinedGroup,
    MenuCatagory,
    Ovqatlar,
    AddToCart,
    Location,
    Order,
    Order_items,
    Working)
from .credentials import API_ENDPOINT, URL
from .trans import t
# Create your views here.

user = ''


def index(request):
    return HttpResponse('index')


text = ''


@csrf_exempt
def receive_request(request):

    if request.method == "POST":
        data = json.loads(request.body)
        firebase_quary_id = data['all_data']
        order_id = data['order_id']

        try:
            orderModel = Order.objects.get(id=order_id)
            user_id = orderModel.user_id
            userModel = BotUsers.objects.get(user_id=user_id)
            userModel.firebase_quary_id = firebase_quary_id
            userModel.save()
            if data['button_type'] == "tastiqlash":
                bot_request('sendMessage', {
                    'chat_id': user_id,
                    'parse_mode': 'html',
                    'text': t(
                        "qabul_qilindi", user=userModel)
                })
            elif data['button_type'] == "yetqazib_berildi":
                bot_request('sendMessage', {
                    'chat_id': user_id,
                    'parse_mode': 'html',
                    'text': t("yetqazib_berildi", user=userModel),
                    'reply_markup': json.dumps(
                        {
                            "inline_keyboard":
                                [
                                    [{'text': t("👍", user=userModel),
                                      'callback_data': 'feedback_good'}],
                                    [{'text': t("👎", user=userModel),
                                      'callback_data': 'feedback_bad'},
                                     ]]

                        }
                    )})

        except ObjectDoesNotExist:
            orderModel = None

        return HttpResponse("success")

    return HttpResponse("salom")

def check_if_group_available(message):
    if "message" in message.keys():
        group_id = message['message']['chat']['id']
        group_name = message['message']['chat']['title']
        JoinedGroup.objects.get_or_create(group_name=group_name, group_chat_id=group_id)


@csrf_exempt
def hook(request):

    if request.method == 'POST':
        message = {}
        user_id = 0
        telegram_message = json.loads(request.body)
        message_type = 'a'
        # if "message" in telegram_message.keys():
        #     message_type = telegram_message['message']['chat']['type']
        # else:
        #     message_type = telegram_message

        # check_if_group_available(telegram_message)
        # if message_type == "private":
        if 'callback_query' in telegram_message.keys():

            user_id = telegram_message['callback_query']['from']['id']
            callbackHandler(telegram_message['callback_query'])
        elif 'message' in telegram_message.keys():
            user_id = telegram_message['message']['from']['id']
            message = telegram_message['message']

        elif 'edited_message' in telegram_message.keys():
            user_id = telegram_message['edited_message']['from']['id']
            message = telegram_message['edited_message']


        else:
            pass
        try:
            global user
            user = BotUsers.objects.get(user_id=user_id)

            if 'contact' in message.keys():
                contactHandler(message)
            elif 'reply_to_message' in message.keys() or 'location' in message.keys():
                check = Working.objects.get(pk=1)
                if check.working == True:

                    if user.user_step == "getLocation":
                        replyHandler(message, check=check)
                        setHandler(message, user)

                    if user.user_step == "getLocationName":
                        setHandler(message, user)

                    homePage(user)
                else:
                    bot_request('sendMessage', {
                        'chat_id': user.user_id,
                        'parse_mode': 'html',
                        'text': check.text
                    })

            elif 'text' in message.keys():
                messageHandler(message, user)

        except ObjectDoesNotExist:
            global text
            if 'text' in message.keys():
                text = message['text']

            if text == t('Register'):
                try:
                    user = BotUsers.objects.get(user_id=user_id)
                    stepHandler(user)

                except ObjectDoesNotExist:
                    branch = Branch.objects.first()
                    user = BotUsers.objects.create(user_id=user_id, user_step="getLang", branch=branch, orqaga_step="getLang", lang='uz')
                    stepHandler(user)

            else:
                bot_request('sendMessage', {
                    'chat_id': user_id,
                    'text': 'Ansor buyurtma botiga xush kelibsiz \nДобро пожаловать в Ансор бот',
                    'parse_mode': 'html',
                    'reply_markup': json.dumps(
                        {
                            'keyboard': [
                                [t('Register')]
                            ],
                            'resize_keyboard': True
                        }
                    )
                })

        
        return HttpResponse('got the post\n', request._get_post())
    return HttpResponse("working")


@require_http_methods(["GET", "POST"])
def setwebhook(request):
    response = requests.post(API_ENDPOINT + "setWebhook?url=" + URL).json()
    return HttpResponse(f"{response}")


def bot_request(method, data):
    return requests.post(API_ENDPOINT + method, data)




def orqaga_handler(user=None, message=None, back_to_from_addToCart=False):
    if 'message' in message.keys():
        menu = message['message']['reply_markup']['inline_keyboard']
        if back_to_from_addToCart:
            id = menu[0][0]['callback_data'][15:]
            example_items_id = json.loads(id)['product_id']
            ovqat = Ovqatlar.objects.get(id=example_items_id)
            step = ovqat.step

            if step == 0:
                ovqatlar = Ovqatlar.objects.filter(step=step, turi=ovqat.turi)
                a = {}
                for i in ovqatlar:
                    a[str(i)] = i.id

                menus = menu_dynamic(a, selected_category_name=a, message=message, go_back=True)
                categoryHandler(message, menu=menus)
            else:
                ovqatlar = Ovqatlar.objects.filter(step=step, parent=ovqat.parent)
                
                a = {}
                for i in ovqatlar:
                    a[str(i)] = i.id

                menus = menu_dynamic(a, selected_category_name=a, message=message, go_back=True)
                categoryHandler(message, menu=menus)



        elif message:
            example_items_id = menu[0][0]['callback_data'].split('_')[1]
            ovqat = Ovqatlar.objects.get(id=example_items_id)
            step = ovqat.step
            if step == 0:
                buyurtmaHandler(message, boshqatdan=True)
            else:
                ovqatlar = Ovqatlar.objects.filter(step=step - 1, turi=ovqat.turi)
                a = {}
                for i in ovqatlar:
                    a[str(i)] = i.id

                menus = menu_dynamic(a, selected_category_name=a, message=message, go_back=True)
                categoryHandler(message, menu=menus)
    else:
        if user:
            userModel = BotUsers.objects.get(user_id=user.user_id)
        elif message:
            userModel = BotUsers.objects.get(user_id=message['from']['id'])
        all_steps = list(userModel.orqaga_step.split(','))
        current_step = userModel.user_step
        current_step_index = all_steps.index(current_step)
        userModel.user_step = all_steps[current_step_index - 1]
        userModel.save()
        stepHandler(userModel)


def setHandler(message, user, change_number=False, callback=False):
    global lang
    if user.user_step == "getLang":
        if 'getIsm' not in user.orqaga_step:
            user.orqaga_step += ",getBranch"
        til = message['text']

        if til == t('uz til'):
            user.lang = 'uz'
            user.user_step = "getBranch"
            user.save()

        else:
            user.lang = 'ru'
            user.user_step = "getBranch"
            user.save()
        stepHandler(user)
    
    
    elif user.user_step == "getBranch":
        try:
            if message['text'] == t('orqaga', user=user):
                orqaga_handler(user=user, message=message)
            else:
                branches = Branch.objects.get(name=message['text'])
                user.branch = branches
                if 'getIsm' not in user.orqaga_step:
                    user.orqaga_step += ",getIsm"
                    user.user_step = "getIsm"
                elif 'getIsm' in user.orqaga_step:
                    user.user_step = ""
                user.save()
                stepHandler(user)

        except ObjectDoesNotExist:
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'text': t('Iltimos branchni tanlang', user=user),
                'reply_markup': json.dumps(
                    {
                        'resize_keyboard': True,
                    }
                )
            })
        


    elif user.user_step == "getIsm":
        if message['text'] == t('orqaga', user=user):
            orqaga_handler(user=user, message=message)
        else:
            user.firstname = message['text']
            if 'getPhone' not in user.orqaga_step:
                user.orqaga_step += ",getPhone"
            user.user_step = "getPhone"
            user.save()
            stepHandler(user)


    elif user.user_step == "getPhone":
        check_number = True
        if 'text' in message.keys() and change_number == False:
            if message['text'] == t('orqaga', user=user):
                orqaga_handler(user=user, message=message)
            elif "+" in message['text']:
                if len(message['text']) != 13:
                    check_number = False

                elif message['text'][0:4] == '+998':
                    for i in range(1, 13):
                        if message['text'][i].isdigit() == False:
                            check_number = False

                
            if "+" not in message['text']:
                check_number = False 

            if check_number == True:
                user.phone = message['text']
                user.user_step = ''
                user.save()
                stepHandler(user)

            elif check_number == False:
                bot_request('sendMessage', {
                    'chat_id': user.user_id,
                    'text': t("phone_number_warning", user=user),
                })

        elif change_number == True:
            stepHandler(user)
        else:
            if 'getPhone' not in user.orqaga_step:
                user.orqaga_step += ",getPhone"
            stepHandler(user)

    elif user.user_step == 'get_feedback':
        if callback:
            message_id = message['message']['message_id']
            data = give_selected_category(message)
            user.user_step = ''
            user.user_feedback = data
            user.save()
            delete_message(user.user_id, message_id)
            request_real_time(feedback=user.user_feedback, user=user)
        else:
            user.user_step = ''
            user.user_feedback = message['text']
            user.save()
            request_real_time(feedback=user.user_feedback, user=user)
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('feedback_done', user=user),
        })
        stepHandler(user)

    elif user.user_step == 'getPaymentType':
        if message['text'] != t('orqaga', user=user):
            user.user_step = 'getLocationName'
            user.save()
            stepHandler(user)


    elif user.user_step == 'getLocationName':
        if message['text'] == t('orqaga', user=user):
            orqaga_handler(user=user, message=message)
        else:
            user.user_step = 'getLocation'
            user.tem_address_name = message['text']
            user.save()
            stepHandler(user)


    elif user.user_step == 'getLocation':
        if 'text' in message.keys():
            if message['text'] == t('asosiy oynaga qaytish', user=user):
                user.user_step = ''
                user.tem_address_name = ''
                user.save()
                homePage(user)
        else:
            user.user_step = ''
            user.save()
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'text': t('Botimizdan foydalanganingiz uchun rahmat', user=user),
                'reply_markup': json.dumps(
                    {
                        'resize_keyboard': True,
                    }
                )
            })


def homePage(user, text=True, order_type=False):
    if text == True:
        text1 = t('quyidagilardan birini tanlang', user=user)
    else:
        text1 = t('Menular', user=user)

    keyboard = [[t('Buyurtma qilish', user=user)],
                [t('Mening buyurtmalarim', user=user), t('Telefon orqali aloqa', user=user)],
                [t('Sozlash', user=user), t('Branches', user=user)], [t('Savatcha', user=user)]
                ]
    bot_request('sendMessage', {
        'chat_id': user.user_id,
        'text': text1,
        'parse_mode': 'html',
        'reply_markup': json.dumps(
            {
                'keyboard': keyboard,
                'resize_keyboard': True,
            }
        )
    })

def dynamic_keyboards(obj):
    count = len(obj)
    count_to_two = []
    menu = []
    for i in obj:
        if i.name == "tegilmasin":
            pass
        else:
            if count % 2 == 0:
                menu.insert(0, [i.name])
                count -= 1
            elif count % 2 == 1:
                count_to_two.append(i.name)
                if len(count_to_two) == 2:
                    menu.append(count_to_two)
                    count_to_two = []
    return menu


def stepHandler(user):
    if user.user_step == "getLang":
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('Tilni tanlang uz/ru', user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [[t('uz til')], [t('ru til')]],
                    'resize_keyboard': True
                }
            )
        })

    elif user.user_step == "getBranch":
        branches = Branch.objects.all()
        menu = dynamic_keyboards(branches)
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('Branch ni tanglang', user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': menu + [[t('orqaga', user=user)]],
                    'resize_keyboard': True,

                }
            )
        })

    elif user.user_step == "getIsm":
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('Ismingizni kiriting', user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [[t('orqaga', user=user)]],
                    'resize_keyboard': True,

                }
            )
        })
    elif user.user_step == "getLastname":
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('Familyangizni kiriting', user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [[t('orqaga', user=user)]],
                    'resize_keyboard': True,
                }
            )
        })
    elif user.user_step == "getPhone":
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t('Mobil raqamingizni kiriting', user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [
                        [{
                            'text': t('contact', user=user),
                            'request_contact': True
                        }]
                    ],
                    'resize_keyboard': True,
                }
            )
        })
    elif user.user_step == 'getLocationName':
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t("Iltimos manzilingizni yozib qoldiring", user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [[t('orqaga', user=user)]],
                    'resize_keyboard': True,
                }
            )
        })
    elif user.user_step == 'getPaymentType':
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t("To'lash turini kiriting", user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [
                        [{
                            'text': t("Naqt pul", user=user)}, {'text': t("Karta orqali to'lash", user=user),
                                                                }]
                    ],
                    'resize_keyboard': True,
                }
            )
        })
    elif user.user_step == 'getLocation':
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t("Manzilingizni kiriting", user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [
                        [{
                            'text': t("Joylashuvni jo'natish", user=user),
                            'request_location': True
                        }], [t('asosiy oynaga qaytish', user=user)]
                    ],
                    'resize_keyboard': True,
                }
            )
        })
    elif user.user_step == 'get_feedback':
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'text': t("nima boldi", user=user),
            'parse_mode': 'html',
            'reply_markup': json.dumps(
                {
                    'keyboard': [
                        [{
                            'text': t("skip", user=user)
                        }]
                    ],
                    'resize_keyboard': True,
                }
            )
        })
    else:
        homePage(user)


def reviewHandler(message):
    user_id = message['from']['id']
    userModel = BotUsers.objects.get(user_id=user_id)
    message_id = message['message']['message_id']

    if message['data'] == "feedback_good":
        bot_request('editMessageReplyMarkup', {
            'chat_id': user_id,
            'message_id': message_id,
            'reply_markup': json.dumps(
                {
                    "inline_keyboard":
                        [
                            [{'text': t("Быстрая доставка", user=userModel),
                              'callback_data': 'feedback_Быстрая доставка'}], [
                            {'text': t("Вежливый курьер", user=userModel),
                             'callback_data': 'feedback_Вежливый курьер'}], [

                            {'text': t("Оператор молодец", user=userModel),
                             'callback_data': 'feedback_Оператор молодец'}], [
                            {'text': t("Великолепный вкус", user=userModel),
                             'callback_data': 'feedback_Великолепный вкус'},
                        ]
                        ]
                }
            )
        })
    elif message['data'] == "feedback_bad":
        userModel.user_step = "get_feedback"
        userModel.save()
        delete_message(user_id, message_id)
        stepHandler(userModel)


def request_real_time(**kwargs):
    user = kwargs['user']

    feedback = kwargs['feedback']
    url = f"https://ansormilliy-c0f34-default-rtdb.asia-southeast1.firebasedatabase.app/orders/{user.firebase_quary_id}.json"
    payload = json.dumps({
        'user_feedback': feedback,
    })
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "d40f61e7-bac1-e66b-0415-1169251aa220"
    }
    response = requests.request('patch', url, data=payload, headers=headers)
    


def messageHandler(message, user):
    message_text = message['text']
    check = Working.objects.get(id=1)


    if message_text == t('Buyurtma qilish', user=user):
        if check.working == True:
            orderTypeHandler(message)
        else:
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'parse_mode': 'html',
                'text': check.text
            })
            homePage(user)


    elif message_text == t('skip', user=user):
        setHandler(message, user)

    elif message_text == t('Savatcha', user=user):
        savatcha(message)
    
    elif user.user_step:
        setHandler(message, user)
    
    elif message_text == t('dastavka', message=message) or message_text == t('olib ketaman', message=message):
        if check.working == True:
            if message_text == t('olib ketaman', message=message):
                user.birthday = ''
                user.save()

            homePage(user, text=False, order_type=True)
            buyurtmaHandler(message, user=user, type=t(message_text, message=message))
        else:
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'parse_mode': 'html',
                'text': check.text
            })
            homePage(user)



    elif message_text == t("Karta orqali to'lash", user=user) or message_text == t("Naqt pul", user=user):
        if check.working == True:
            get_payment_type(message, user)
        else:
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'parse_mode': 'html',
                'text': check.text
            })
            homePage(user)

    elif message_text == t('Sozlash', user=user):
        settingHandler(message)

    elif message_text == t('Telefon orqali aloqa', user=user):
        givePhoneRumber(message)

    elif message_text == t('Mening buyurtmalarim', user=user):
        buyurtmaMalumotHandler(message)

    elif message_text == t('Branches', user=user):
        user.user_step = "getBranch"
        user.save()
        stepHandler(user)

    elif 'location' in message.keys():
        if check.working == True:
            getOrder(message)
        else:
            bot_request('sendMessage', {
                'chat_id': user.user_id,
                'parse_mode': 'html',
                'text': check.text
            })
    else:
        homePage(user)


def get_payment_type(message, user):
    message_text = message['text']
    user.birthday = message_text
    user.save()
    if message_text == t("Karta orqali to'lash", user=user):
        bot_request('sendMessage', {
            'chat_id': user.user_id,
            'parse_mode': 'html',
            'text': f"<b>{t('Bizni karta raqamimiz', user=user)}\n💳 8600530488775084 \n👤 {t('Azimov Tohir', user=user)}</b>"
        })
    setHandler(message, user)


def contactHandler(message):
    if user.user_step == "getPhone":
        user.phone = message['contact']['phone_number']
        user.user_step = ''
        user.save()
        stepHandler(user)


product = ''
text = ''


def callbackHandler(message):
    if message['data']:
        global product, text
        user = BotUsers.objects.get(user_id=message['from']['id'])
        callback = change_callback_data(message['data'])

        if user.user_step:
            setHandler(message, user)
            
        if message['data'] == "feedback_good" or message['data'] == "feedback_bad":
            reviewHandler(message)
        
        elif message['data'] == 'boshat':
            deleteOrder(message, addToCart_query=AddToCart)

        elif 'qabul_qilindi' in message['data']:
            # needs to be checked
            ordered_user_id = message['data'][14:]
            user = BotUsers.objects.get(user_id=ordered_user_id)
            change_data_from_channel(message, user, change_mode='qabul_qilindi')
            bot_request('sendMessage', {
                    'chat_id': message['data'][14:],
                    'parse_mode': 'html',
                    'text': t(
                        "qabul_qilindi", user=user)
                })

        elif 'yolda' in message['data']:
            ordered_user_id = message['data'][6:]
            user = BotUsers.objects.get(user_id=ordered_user_id)

            change_data_from_channel(message, user, change_mode='yolda')
            bot_request('sendMessage', {
                    'chat_id': ordered_user_id,
                    'parse_mode': 'html',
                    'text': t(
                        "yolda", user=user)
                })

        elif "tugatildi" in message['data']:
            ordered_user_id = message['data'].split("_")[1]
            user = BotUsers.objects.get(user_id=ordered_user_id)

            change_data_from_channel(message, user, change_mode='tugatildi')
            bot_request('sendMessage', {
                    'chat_id': ordered_user_id,
                    'parse_mode': 'html',
                    'text': t("yetqazib_berildi", user=user),
                    'reply_markup': json.dumps(
                        {
                            "inline_keyboard":
                                [
                                    [{'text': t("👍", user=user),
                                      'callback_data': 'feedback_good'}],
                                    [{'text': t("👎", user=user),
                                      'callback_data': 'feedback_bad'},
                                     ]]

                        }
                    )})

        elif 'print_data' in message['data']:
            arr = json.loads(message['data'][10:])
            product_id = arr['product_id']
            try:
                product = Ovqatlar.objects.get(id=int(product_id))
                total_price = int(product.narxi) * int(arr['count'])
                text = str(
                        arr['count']) + f" {t('ta', message=message)} ({t(product.name, message=message)}) {t('narxi', message=message)} : {total_price}"
                bot_request('answerCallbackQuery', {
                    'callback_query_id': message['id'],
                    'text': text,
                    'show_alert': True
                })
            except ObjectDoesNotExist:
                product = None

            

        elif 'deduct_one_item' in message['data']:
            arr = json.loads(message['data'][15:])
            product_id = arr['product_id']
            try:
                product = Ovqatlar.objects.get(id=int(product_id))
            except ObjectDoesNotExist:
                product = None
            editProductDetailTest_withAddToCart(message=message, productObj=product, object_from_database=Ovqatlar.objects.all(), count_num=-1, product_id=product_id)
        
        elif 'add_one_item' in message['data']:
            arr = json.loads(message['data'][12:])
            product_id = arr['product_id']
            try:
                product = Ovqatlar.objects.get(id=int(product_id))
            except ObjectDoesNotExist:
                product = None
            editProductDetailTest_withAddToCart(message=message, productObj=product, object_from_database=Ovqatlar.objects.all(), count_num=1, product_id=product_id)
        
        elif message['data'][:3] == 'del':
            deleteOrder(message, delete_single_item=AddToCart)
        
        
        elif message['data'][:9] == 'feedback_':
            user.user_step = "get_feedback"
            user.save()
            setHandler(message, user, callback=True)
        
        elif message['data'] == 'DavomEtish':
            savatda(message, deleted=False)
        
        elif message['data'] == 'ozbekchaga_ozgartir' or message['data'] == 'ruschaga_ozgartir':
            changeSettingHandler(message)

        elif message['data'] == 'tilni_ozgartir' or message['data'] == 'nomerni_ozgartir':
            changeSettingHandler(message)

        elif message['data'][0] == 'P' or message['data'][0] == 'C' or message['data'][0] == 'I' or message['data'][
            0] == 'T' or message['data'][0] == 'F':
            categoryHandler(message)

        elif message['data'] == 'orqaga':
            orqaga_handler(user=user, message=message)
        
        elif message['data'] == 'yangi_mahsulot':
            delete_message(message['from']['id'], message['message']['message_id'])
            buyurtmaHandler(message, text=savatda(message, deleted=True))
        
        elif message['data'] == 'buyurtma_qilish':
            checkoutHandler(message)
        
        elif message['data'] == "back_to_shop_area":
            orqaga_handler(message=message, back_to_from_addToCart=True)


def checkoutHandler(message):
    user_id = message['from']['id']
    userModel = BotUsers.objects.get(user_id=user_id)

    if userModel.delivery_type == t('dastavka', user=userModel):
        message_id = message['message']['message_id']
        user = BotUsers.objects.get(user_id=user_id)
        user.user_step = "getPaymentType"
        if 'getPaymentType' not in user.orqaga_step:
            user.orqaga_step += ',getPaymentType,getLocationName,getLocation'
        user.save()

        delete_message(user_id, message_id)
        stepHandler(user)
    else:
        message_id = message['message']['message_id']
        delete_message(userModel.user_id, message_id)
        replyHandler(message)
        bot_request('sendMessage', {
            'chat_id': userModel.user_id,
            "text": t("Botimizdan foydalanganingiz uchun rahmat", user=userModel)
        })
        homePage(
            userModel
        )


def orderTypeHandler(message) -> object:
    """
    order type: object
    """
    user_id = message['from']['id']
    bot_request('sendMessage', {
        'chat_id': user_id,
        'text': t("Buyurtmani o'zingiz olib ketasizmi yoki etkazib berishsinmi", message=message),
        'parse_mode': 'html',
        'reply_markup': json.dumps(
            {
                'keyboard': [[t('dastavka', message=message), t('olib ketaman', message=message)]],
                'resize_keyboard': True
            }

        )
    })


def categoryHandler(message, menu=None):
    user_id = message['from']['id']
    message_id = message['message']['message_id']
    arr = {}
    product_id = 0
    
    if menu is None:
        arr = give_selected_category(message, data_from_database=Ovqatlar.objects.all())

    if arr and menu is None:
        if arr[0]:
            menu = menu_dynamic(
                Ovqatlar.objects.all(),
                selected_category_name=arr[0],
                selected_callback=message['data'],
                message=message,
            )

            bot_request('editMessageReplyMarkup', {
                'chat_id': user_id,
                'message_id': message_id,
                'reply_markup': json.dumps(
                    {
                        "inline_keyboard": menu

                    }
                )
            })

        else:
            sendProductDetailTest(message, arr[1], Ovqatlar.objects.all(), message_with_inline=message['message']['reply_markup']['inline_keyboard'])

    elif menu:
        bot_request('editMessageReplyMarkup', {
            'chat_id': user_id,
            'message_id': message_id,
            'reply_markup': json.dumps(
                {
                    "inline_keyboard": menu

                }
            )
        })


def buyurtmaHandler(message, user=None, type=None, text=None, boshqatdan=False):
    user_id = message['from']['id']
    bot_user = BotUsers.objects.get(user_id=user_id)
    if not text:
        text = f'<b>{t("Menuni tanlang", message=message)}\n\n<a href="{bot_user.branch.telegraph_link}">{t("Barcha Menularni Korish", message=message).upper()}</a></b>'
    else:
        pass

    if type:
        user.delivery_type = type
        user.save()
    catagories = MenuCatagory.objects.filter(branch=bot_user.branch)
    menus = menu_dynamic(catagories, message=message, menu_to_be_added='yes')
    if boshqatdan == True:
        message_id = message['message']['message_id']
        delete_message(user_id, message_id)
    bot_request('sendMessage', {
        'chat_id': user_id,
        'text': text,
        'parse_mode': 'html',
        'reply_markup': json.dumps(
            {
                'inline_keyboard': menus,
            }
        )
    })


def give_selected_category(data, data_from_database=None, menus=None, product_id=False):

    if 'message' in data.keys():
        menus = data['message']['reply_markup']['inline_keyboard']
    else:
        menus = ''

    if data_from_database is None:
        for i in range(len(menus)):
            for b in range(len(menus[i])):
                if 'url' not in menus[i][b].keys():
                    if menus[i][b]['callback_data'] == data['data']:

                        return menus[i][b]['text']
    else:

        for i in range(len(menus)):
            for b in range(len(menus[i])):
                if 'url' not in menus[i][b].keys():
                    if data['data'] == menus[i][b]['callback_data']:
                        for_selected_category = {
                            str(key): key.id for key in data_from_database
                            if str(key.parent) == menus[i][b]['text'] or str(key.turi) == menus[i][b]['text'] and str(
                                key.parent) == 'None'
                        }
                        if product_id==True:
                            return menus[i][b]
                        return for_selected_category, menus[i][b]['text']


def change_callback_data(selected_callback):
    callback_change = 'P'
    if selected_callback:
        if selected_callback[0] == 'P':
            callback_change = 'C'
        elif selected_callback[0] == 'C':
            callback_change = 'InC'
        elif selected_callback[0] == 'I':
            callback_change = 'Turi'
        elif selected_callback[0] == 'T':
            callback_change = 'Final'
        elif selected_callback[0] == 'd':
            callback_change = 'add_to_cart'
        elif selected_callback[0] == 'add_to_cart':
            callback_change = 'location'
            callback_change = ''

        elif selected_callback[0][:3] == 'del':
            callback_change = 'del'
        elif selected_callback[0] == 'del':
            callback_change = 'P'

    return callback_change


def menu_dynamic(data_from_database=None, selected_category_name={}, selected_callback=None, item_with_callback=None,
                 message=None,
                 menu_to_be_added=None, go_back=False):
    if item_with_callback is not None:
        category_data = []
        products_id = []
        for k, v in item_with_callback.items():
            category_data.append(k)
            products_id.append(v)
    else:
        if selected_callback is None:
            category_data = data_from_database
        else:
            category_data = selected_category_name

    callback_change = change_callback_data(selected_callback)

    menus = []
    temporary_dict = []
    check = len(category_data)

    if menu_to_be_added is not None and check % 2 == 0:
        user_id = message['from']['id']
        bot_user = BotUsers.objects.get(user_id=user_id)

        menus.append(
            [{'text': t('Barcha menular', message=message), 'url': f'{bot_user.branch.telegraph_link}'}])
    if selected_category_name:
        user_id = message['from']['id']
        bot_user = BotUsers.objects.get(user_id=user_id)
        for key, value in category_data.items():
            one = {"text": t(key, message=message),
                   'callback_data': f'{callback_change}_{value}'}
            if check % 2 == 0:
                if len(temporary_dict) < 1:
                    temporary_dict.append(one)
                else:
                    temporary_dict.append(one)
                    menus.append(temporary_dict)
                    temporary_dict = []
            else:
                check -= 1
                temporary_dict.append(one)
                menus.append(temporary_dict)
                if menu_to_be_added is not None:
                    menus[0].insert(0,
                                    {'text': t('Barcha menular', message=message),
                                     'url': f'{bot_user.branch.telegraph_link}'})

                temporary_dict = []
    else:
        user_id = message['from']['id']
        bot_user = BotUsers.objects.get(user_id=user_id)
        for count_callback in range(len(category_data)):
            if item_with_callback is not None:
                one = {"text": t(str('❌ ' + category_data[count_callback]), message=message),
                       'callback_data': f'del_{products_id[count_callback]}'}

            else:
                one = {"text": t(str(category_data[count_callback]), message=message),
                       'callback_data': f'{callback_change}_{count_callback}'}
            if check % 2 == 0:

                if len(temporary_dict) < 1:
                    temporary_dict.append(one)

                else:

                    temporary_dict.append(one)
                    menus.append(temporary_dict)
                    temporary_dict = []
            else:
                check -= 1
                temporary_dict.append(one)
                menus.append(temporary_dict)
                if menu_to_be_added is not None:
                    menus[0].insert(0,
                                    {'text': t('Barcha menular', message=message),
                                     'url': f'{bot_user.branch.telegraph_link}'})

                temporary_dict = []
            count_callback += 1
    if selected_category_name or go_back == True:
        menus += [[{'text': t('orqaga', message=message), 'callback_data': 'orqaga'}]]
    return menus


def sendProductDetail(message, data, object_from_database):
    user_id = message['from']['id']
    message_id = message['message']['message_id']
    delete_message(user_id, message_id)

    for i in object_from_database:
        if str(i) == data:
            bot_request('sendPhoto', {
                'chat_id': user_id,
                'photo': "https://ansorfamily.isaak.uz/media/" + f"{i.image}",
                # 'photo': open("GMP_9988.jpg", 'rb'),
                'caption': f"{t(str(i))}\n"
                           f"{t('Narxi', message=message)}: {i.narxi}\n"
                           f"{t('Tarkibi', message=message)}: {i.tarkibi}\n",
                'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [{'text': '1', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 1})},
                             {'text': '2', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 2})},
                             {'text': '3', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 3})}],
                            [{'text': '4', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 4})},
                             {'text': '5', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 5})},
                             {'text': '6', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 6})}],
                            [{'text': '7', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 7})},
                             {'text': '8', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 8})},
                             {'text': '9', 'callback_data': 'd_' + json.dumps({"product_id": str(i.id), "count": 9})}],
                            [{'text': t('Davom etish', message=message), 'callback_data': 'DavomEtish'},
                             {'text': t('orqaga', message=message), 'callback_data': 'back_to_shop_area'}]
                        ]
                    }
                )
            })

def editProductDetailTest_withAddToCart(**kwargs):
    user_id = kwargs['message']['from']['id']
    message_id = kwargs['message']['message']['message_id']
    text = ''
    try:
        price = int(kwargs['productObj'].narxi) * 1
        cart = AddToCart.objects.get(user_id=user_id, product_id=kwargs['product_id'])
        if cart.count == 1 and int(kwargs['count_num']) == -1:
            cart.count = 1
            cart.price = price
            cart.name = kwargs['productObj'].name
            cart.save()
            text = str(
                    cart.count) + f" {t('ta', message=kwargs['message'])} ({t(kwargs['productObj'].name, message=kwargs['message'])}) {t('narxi', message=kwargs['message'])} : {cart.price}"

        else:
            cart.count += int(kwargs['count_num'])
            if int(kwargs['count_num']) == -1:
                cart.price -= price
            else:
                cart.price += price
            cart.name = kwargs['productObj'].name
            cart.save()
            text = str(
                    cart.count) + f" {t('ta', message=kwargs['message'])} ({t(kwargs['productObj'].name, message=kwargs['message'])}) {t('narxi', message=kwargs['message'])} : {cart.price}"


    except ObjectDoesNotExist:
        if int(kwargs['count_num']) != -1:
            price = int(kwargs['productObj'].narxi) * 1

            cart = AddToCart.objects.create(food_obj=kwargs['productObj'], user_id=user_id, product_id=kwargs['productObj'].id,
                                            price=price, name=kwargs['productObj'].name,

                                            count=int(kwargs['count_num']))

            cart.save()
            text = str(
                        cart.count) + f" {t('ta', message=kwargs['message'])} ({t(kwargs['productObj'].name, message=kwargs['message'])}) {t('narxi', message=kwargs['message'])} : {cart.price}"

        else:
            price = int(kwargs['productObj'].narxi) * 1
            cart = AddToCart.objects.create(food_obj=kwargs['productObj'], user_id=user_id, product_id=kwargs['productObj'].id,
                                            price=price, name=kwargs['productObj'].name,

                                            count=1)
            cart.save()
            text = str(
                        cart.count) + f" {t('ta', message=kwargs['message'])} ({t(kwargs['productObj'].name, message=kwargs['message'])}) {t('narxi', message=kwargs['message'])} : {cart.price}"

    bot_request('answerCallbackQuery', {
        'callback_query_id': kwargs['message']['id'],
        'text': text,
        'show_alert': True
    })         
    bot_request('editMessageCaption', {
        'chat_id': user_id,
        'message_id': message_id,
        'photo': "https://ansorfamily.isaak.uz/media/" + f"{kwargs['productObj'].image}",
        'caption': 
                f"{t(str(kwargs['productObj']))}\n"
                    f"{t('Narxi', message=kwargs['message'])}: {kwargs['productObj'].narxi}\n"
                    f"{t('Tarkibi', message=kwargs['message'])}: {kwargs['productObj'].tarkibi}\n",
            'reply_markup': json.dumps(
                {
                    "inline_keyboard": [
                        [{'text': '-', 'callback_data': 'deduct_one_item' + json.dumps({"product_id": str(kwargs['productObj'].id), "count": -1}) },
                        {'text': f'{cart.count}', 'callback_data': 'print_data' + json.dumps({"product_id": str(kwargs['productObj'].id), "count": str(cart.count)}) },
                        {'text': '+', 'callback_data': 'add_one_item' + json.dumps({"product_id": str(kwargs['productObj'].id), "count": 1}) } ],
                        
                        [
                        {'text': t('orqaga', message=kwargs['message']), 'callback_data': 'back_to_shop_area'}, 
                        {'text': t('Davom etish', message=kwargs['message']), 'callback_data': 'DavomEtish'}]
                    ]
                }
            )
        })

    

def sendProductDetailTest(message, data, object_from_database, count_num=0, check_first_time=True, message_with_inline=None):
    if check_first_time == True:
        count_num = 0
        check_first_time = False
    user_id = message['from']['id']
    message_id = message['message']['message_id']
    product_info = give_selected_category(message, data_from_database=Ovqatlar.objects.all(), product_id=True)
    product_id = product_info['callback_data'].split('_')[1]
    delete_message(user_id, message_id)
    ovqat = Ovqatlar.objects.get(id=product_id)
    bot_request('sendPhoto', {
                'chat_id': user_id,
                'photo': "https://ansorfamily.isaak.uz/media/" + f"{ovqat.image}",
                'caption': f"{t(str(ovqat))}\n"
                        f"{t('Narxi', message=message)}: {ovqat.narxi}\n"
                        f"{t('Tarkibi', message=message)}: {ovqat.tarkibi}\n",
                'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [{'text': '-', 'callback_data': 'deduct_one_item' + json.dumps({"product_id": str(ovqat.id), "count": count_num}) },
                            {'text': f'{count_num}', 'callback_data': 'print_data' + json.dumps({"product_id": str(ovqat.id), "count": str(count_num)}) },
                            {'text': '+', 'callback_data': 'add_one_item' + json.dumps({"product_id": str(ovqat.id), "count": count_num}) } ],
                            
                            [
                            {'text': t('orqaga', message=message), 'callback_data': 'back_to_shop_area'}, 
                            {'text': t('Davom etish', message=message), 'callback_data': 'DavomEtish'}]
                        ]
                    }
                )
            })
    # for i in object_from_database:
    #     if str(i) == data:

            


def change_item(data, count_num):
    if count_num == 0:
        return 0
    elif data == "add":
        count_num += 1
    elif data == "deduct":
        count_num -= 1
    return count_num

product_id = 0
text = ''
count = 0
tem = 0
price = 0


def addToCart(message):
    global count, price, product_id, text, tem
    # pass
    product_callback_json = json.loads(message['data'][2:])
    data = {
        'count': 0,
        'product': '',
        'product_id': 0,
        'price': 0,
        'singe_price': 0,
        'ordering_price': 0
    }
    selected_item = give_selected_category(message)
    productModel = Ovqatlar.objects.get(id=product_callback_json['product_id'])
    user_id = message['from']['id']

    if len(selected_item) == 1:
        if productModel.working:
            try:
                price = int(productModel.narxi) * int(product_callback_json['count'])
                cart = AddToCart.objects.get(user_id=user_id, product_id=product_callback_json['product_id'])
                cart.count += int(product_callback_json['count'])
                cart.price += price
                cart.name = productModel.name
                cart.save()
                text = str(
                    cart.count) + f" {t('ta', message=message)} ({t(productModel.name, message=message)}) {t('narxi', message=message)} : {cart.price}"

                data = {
                    'count': cart.count,
                    'product': productModel.name,
                    'product_id': productModel.id,
                    'price': cart.price,
                    'singe_price': int(productModel.narxi),
                    'ordering_price': 6000
                }

            except ObjectDoesNotExist:

                price = int(productModel.narxi) * int(product_callback_json['count'])

                cart = AddToCart.objects.create(food_obj=productModel, user_id=user_id, product_id=product_callback_json['product_id'],
                                                price=price, name=productModel.name,
                                                count=int(product_callback_json['count']))

                cart.save()
                text = str(
                    cart.count) + f" ta ({t(productModel.name, message=message)}) {t('narxi', message=message)} : {cart.price}"

                data = {
                    'count': cart.count,
                    'product': productModel.name,
                    'product_id': productModel.id,
                    'price': cart.price,
                    'singe_price': int(productModel.narxi),
                    'ordering_price': 6000
                }
        else:
            text = t("Kechirasiz hozir bu maxsulot yo'q", message=message)

            

    bot_request('answerCallbackQuery', {
        'callback_query_id': message['id'],
        'text': text,
        'show_alert': True
    })
    return data


def delete_message(chat_id, message_id):
    bot_request('deleteMessage', {
        'chat_id': chat_id,
        'message_id': message_id
    })


count = 0
check = []


def savatcha(message):
    global count, check
    user_id = message['from']['id']
    botuserModel = BotUsers.objects.get(user_id=user_id)
    userModel = AddToCart.objects.filter(user_id=user_id)
    count = len(userModel)
    working_status = Working.objects.get(pk=1)
    paketlar_narxi = 0
    if count == 0:
        text1 = t("Hali hech narsa yo'q", message=message)
        bot_request('sendMessage', {
            'chat_id': message['from']['id'],
            'parse_mode': 'html',
            'text': text1})
    else:
        sum = 0
        sana = ''
        items_for_deleting = {}
        if len(userModel) > 1:
            items_for_deleting = {}
            for i in userModel:
                paketlar_narxi += i.food_obj.paket_narxi * i.count
                items_for_deleting[i.name] = i.id
                sum += i.price
                sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"
        else:
            items_for_deleting = {}
            for i in userModel:
                paketlar_narxi += i.food_obj.paket_narxi * i.count
                items_for_deleting[i.name] = i.id
                sum += i.price
                # sana = f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n"
                sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"

            if botuserModel.delivery_type == t('dastavka', user=botuserModel):
                yetkazib_berish_narxi = botuserModel.branch.delivery_price
                botuserModel.delivery_price = yetkazib_berish_narxi
                botuserModel.save()
            else:
                yetkazib_berish_narxi = 0
                botuserModel.delivery_price = yetkazib_berish_narxi
                botuserModel.save()

        deleting_menu = menu_dynamic([], item_with_callback=items_for_deleting, message=message)
        som = t("so'm", message=message)
        text = f"<b>{t('savatchada', message=message)}:</b>\n\n {sana} \n<b>{t('Mahsulot narxi', message=message)}:</b> {sum} {som} \n" \
               f"<b>{t('Yetkazib berish narxi', message=message)}:</b> {botuserModel.delivery_price} {som}\n" \
               f"<b>{t('Paketlar narxi', message=message)}:</b> {paketlar_narxi} {som}\n" \
               f"<b>{t('Jami', message=message)}:</b> {sum + botuserModel.delivery_price + paketlar_narxi} {som}"

        bot_request('sendMessage', {
            'chat_id': user_id,
            'parse_mode': 'html',
            'text': text,
            'reply_markup': json.dumps(
                {
                    "inline_keyboard": [
                                           [
                                               {'text': t("Yangi mahsulot qo'shish", message=message),
                                                'callback_data': 'yangi_mahsulot'},
                                               {'text': t("checkout", message=message),
                                                'callback_data': 'buyurtma_qilish'}
                                           ],
                                           [
                                               {'text': t("Savatni bo'shatish", message=message),
                                                'callback_data': 'boshat'},
                                           ]
                                       ] + deleting_menu
                }
            )
        }
                    )


def savatda(message, deleted=False):
    global count, check
    working_status = Working.objects.get(pk=1)
    paketlar_narxi = 0

    if deleted:

        user_id = message['from']['id']
        userModel = AddToCart.objects.filter(user_id=user_id)
        botuserModel = BotUsers.objects.get(user_id=user_id)
        count = len(userModel)

        sum = 0
        sana = ''
        yetkazib_berish_narxi = 0
        message_id = message['message']['message_id']
        delete_message(user_id, message_id)
        items_for_deleting = {}
        if len(userModel) > 1:
            items_for_deleting = {}
            for i in userModel:
                paketlar_narxi += i.food_obj.paket_narxi * i.count
                items_for_deleting[i.name] = i.id
                sum += i.price
                sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"
        else:
            items_for_deleting = {}
            for i in userModel:
                items_for_deleting[i.name] = i.id
                paketlar_narxi += i.food_obj.paket_narxi * i.count
                sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"
                sum += i.price
                # sana = f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n"
            if botuserModel.delivery_type == t('dastavka', user=botuserModel):
                yetkazib_berish_narxi = botuserModel.branch.delivery_price
                botuserModel.delivery_price = yetkazib_berish_narxi
                botuserModel.save()
            else:
                yetkazib_berish_narxi = 0
                botuserModel.delivery_price = yetkazib_berish_narxi
                botuserModel.save()

            deleting_menu = menu_dynamic([], item_with_callback=items_for_deleting, message=message)
            som = t("so'm", message=message)
            text = f"<b>{t('savatchada', message=message)}:</b>\n\n {sana} \n<b>{t('Mahsulot narxi', message=message)}:</b> {sum} {som} \n" \
               f"<b>{t('Yetkazib berish narxi', message=message)}:</b> {botuserModel.delivery_price} {som}\n" \
               f"<b>{t('Paketlar narxi', message=message)}:</b> {paketlar_narxi} {som}\n" \
               f"<b>{t('Jami', message=message)}:</b> {sum + botuserModel.delivery_price + paketlar_narxi} {som}"

            return text

    else:

        user_id = message['from']['id']
        userModel = AddToCart.objects.filter(user_id=user_id)
        botuserModel = BotUsers.objects.get(user_id=user_id)
        count = len(userModel)

        if count == 0:
            bot_request('sendMessage', {
                'chat_id': message['from']['id'],
                'parse_mode': 'html',
                'text': 'yoq hech narsa'})
        else:
            sum = 0
            sana = ''
            yetkazib_berish_narxi = 0
            # userModel = json.dumps(list(a))

            message_id = message['message']['message_id']
            delete_message(user_id, message_id)
            items_for_deleting = {}
            if len(userModel) > 1:
                items_for_deleting = {}
                for i in userModel:
                    items_for_deleting[i.name] = i.id
                    paketlar_narxi += i.food_obj.paket_narxi * i.count
                    sum += i.price
                    sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"
                    # sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n"
            else:
                items_for_deleting = {}
                for i in userModel:
                    items_for_deleting[i.name] = i.id
                    paketlar_narxi += i.food_obj.paket_narxi * i.count
                    sum += i.price
                    sana += f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n {t('Paketlar narxi', message=message)}: {i.food_obj.paket_narxi * i.count}\n"
                    # sana = f"{i.count} ✔ {t(i.name, message=message).upper()} {int(i.price / i.count)}\n"
                if botuserModel.delivery_type == t('dastavka', user=botuserModel):
                    yetkazib_berish_narxi = botuserModel.branch.delivery_price
                    botuserModel.delivery_price = yetkazib_berish_narxi
                    botuserModel.save()
                else:
                    yetkazib_berish_narxi = 0
                    botuserModel.delivery_price = yetkazib_berish_narxi
                    botuserModel.save()

            deleting_menu = menu_dynamic([], item_with_callback=items_for_deleting, message=message)
            som = t("so'm", message=message)
            text = f"<b>{t('savatchada', message=message)}:</b>\n\n {sana} \n<b>{t('Mahsulot narxi', message=message)}:</b> {sum} {som} \n" \
               f"<b>{t('Yetkazib berish narxi', message=message)}:</b> {botuserModel.delivery_price} {som}\n" \
               f"<b>{t('Paketlar narxi', message=message)}:</b> {paketlar_narxi} {som}\n" \
               f"<b>{t('Jami', message=message)}:</b> {sum + botuserModel.delivery_price + paketlar_narxi} {som}"

            bot_request('sendMessage', {
                'chat_id': user_id,
                'parse_mode': 'html',
                'text': text,
                'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                                               [
                                                   {'text': t("Yangi mahsulot qo'shish", message=message),
                                                    'callback_data': 'yangi_mahsulot'},
                                                   {'text': t("checkout", message=message),
                                                    'callback_data': 'buyurtma_qilish'}
                                               ],
                                               [
                                                   {'text': t("Savatni bo'shatish", message=message),
                                                    'callback_data': 'boshat'},
                                               ]

                                           ] + deleting_menu
                    }
                )
            }
                        )
            return text


def getOrder(message):
    pass
    # for i in userAddToCartModel:


def replyHandler(message, check=None):
    user_id = message['from']['id']
    userModel = BotUsers.objects.get(user_id=user_id)
    delivery_price = 0
    userAddToCartModel = AddToCart.objects.filter(user_id=user_id)
    working_status = Working.objects.get(pk=1)
    location = 'olib ketadi'
    tem_location = 'olib ketadi'
    location_telegram = {"latitude": 0, 'longitude': 0}
    if 'location' in message.keys():
        location_telegram = message['location']
        geolocator = Nominatim(user_agent="geoapiExercises")
        Latitude = f"{location_telegram['latitude']}"
        Longitude = f"{location_telegram['longitude']}"
        # {'latitude': 40.445419, 'longitude': 71.942576}
        location = geolocator.reverse(Latitude + "," + Longitude)
        address = location.raw['address']
        delivery_price = check.delivery_price
        #  "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyDLm6CCJz4QsbC7neTpiWMgljvGsZwRtGw"
        #  "https://geocode-maps.yandex.ru/1.x/?apikey=61e60c55-613c-4ce8-9b90-291d02c8b9f1&geocode=28.975555,41.008074&lang=en-US"
        tem_location = userModel.tem_address_name

    total_amount = 0
    full_name = f'{userModel.firstname} {userModel.surname}'
    delivery_type = userModel.delivery_type
    phone = userModel.phone

    for i in userAddToCartModel:
        total_amount += i.price + i.food_obj.paket_narxi

    total_amount += userModel.delivery_price
    secs = time.time()
    now = time.ctime(secs).split()
    if total_amount > delivery_price:
        order = Order.objects.create(
            user_id=user_id,
            fio=full_name,
            phone=phone,
            status=1,
            total_amount=total_amount,
            created_at=now[1:],
            location=location,
            tem_lat=location_telegram['latitude'],
            tem_long=location_telegram['longitude'],
            tem_address_name=tem_location,
            branch_name = userModel.branch.name,
            order_type=delivery_type,
            # payment_type

        )
        order.save()
        products = {}
        for i in userAddToCartModel:
            products[i.name] = i.count
            item = Order_items.objects.create(
                order_id=order,
                user_id=i.user_id,
                location=order.location,
                phone=order.phone,
                product_id=i.product_id,
                product=i.name,
                price=i.price,
                count=i.count,
                branch_name = userModel.branch.name
            )
            item.save()
        AddToCart.objects.filter(user_id=user_id).delete()
        products_to_send_to_front = ''
        for k, v in products.items():
            products_to_send_to_front += k + ':\t' + str(v) + ' | '
        
        url = "https://ansormilliy-c0f34-default-rtdb.asia-southeast1.firebasedatabase.app/orders.json"
        payment_type = userModel.birthday
        payload = json.dumps({
            # 'order': order,
            "id": order.id,
            'fio': order.fio,
            'phone': order.phone,
            'total_amount': order.total_amount,
            'location': str(order.location),
            'name': products_to_send_to_front,
            'order_type': order.order_type,
            'payment_type': payment_type,
            'selected_location': userModel.tem_address_name,
            'time': order.created_at,
        })

        text_to_channel = f"<b>  NEW ORDER  </b>\n<b>id:</b> {order.id},\n<b>fio:</b> {order.fio},\n<b>phone:</b> {order.phone},\n<b>total_amount:</b>  {order.total_amount},\n<b>name:</b> {products_to_send_to_front},\n<b>order_type:</b> {order.order_type},\n <b>payment_type:</b> {payment_type},\n<b>selected_location:</b> {userModel.tem_address_name},\n<b>time:</b> {order.created_at}"
        
        send_to_channel(message, order.tem_lat, order.tem_long, text=text_to_channel, order_type=order.order_type, ordered_user_id=user_id)

        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'postman-token': "d40f61e7-bac1-e66b-0415-1169251aa220"
        }
        response = requests.request("POST", url, data=payload, headers=headers)




def deleteOrder(message, addToCart_query=None, delete_single_item=None):
    message_id = message['message']['message_id']

    if message['data'][:3] == 'del':
        id = message['data'].split('_')[1]
        id = int(id)
        delete_single_item.objects.filter(id=id).delete()
        user_id = message['from']['id']
        delete_message(user_id, message_id)
        savatda(message)

    else:
        id = message['from']['id']
        delete_message(id, message_id)

    if addToCart_query:
        addToCart_query.objects.filter(user_id=id).delete()


def settingHandler(message):
    user_id = message['from']['id']
    userModel = BotUsers.objects.get(user_id=user_id)
    muloqot_tili = t("O'zbekcha", message=message) if userModel.lang == 'uz' else t('Ruscha',
                                                                                    message=message)
    text = f"<b>{t('Muloqot tili', message=message)}:</b> {muloqot_tili}\n" \
           f"<b>{t('Telefon nomer', message=message)}:</b> {userModel.phone}\n\n" \
           f'{t("quyidagilardan birini tanlang", message=message)}'

    bot_request('sendMessage', {
        'chat_id': user_id,
        'parse_mode': 'html',
        'text': text,
        'reply_markup': json.dumps(
            {
                "inline_keyboard": [
                    [
                        {'text': t("Til", message=message), 'callback_data': 'tilni_ozgartir'},
                        {'text': t("Telefon", message=message), 'callback_data': 'nomerni_ozgartir'}
                    ]
                ]
            }
        )
    }
                )


def changeSettingHandler(message):
    user_id = message['from']['id']
    message_id = message['message']['message_id']
    userModel = BotUsers.objects.get(user_id=user_id)
    if message['data'] == 'tilni_ozgartir':
        bot_request('editMessageReplyMarkup', {
            'chat_id': user_id,
            'message_id': message_id,
            'parse_mode': 'html',
            'text': text + t('tilni tanlang', message=message),
            'reply_markup': json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {'text': t("O'zbekcha", message=message), 'callback_data': 'ozbekchaga_ozgartir'},
                            {'text': t("Ruscha", message=message), 'callback_data': 'ruschaga_ozgartir'}
                        ]
                    ]
                }
            )
        }
                    )
    elif message['data'] == "nomerni_ozgartir":
        delete_message(user_id, message_id)

        userModel.user_step = 'getPhone'
        userModel.save()
        setHandler(message, userModel)

    elif message['data'] == 'ozbekchaga_ozgartir':
        delete_message(user_id, message_id)
        userModel.lang = 'uz'
        userModel.save()
        homePage(userModel)
    elif message['data'] == 'ruschaga_ozgartir':
        delete_message(user_id, message_id)
        userModel.lang = 'ru'
        userModel.save()
        homePage(userModel)


# menuni tanlang
def buyurtmaMalumotHandler(message):
    user_id = message['from']['id']
    temText = ''
    userOrder = Order_items.objects.filter(user_id=user_id)
    name = ''
    count = 0
    if userOrder:
        for i in userOrder:
            count += 1
            name = f"<b>№ | 👤 {i.order_id}</b>\n\n"
            temText += f"<b>{count} | {i.count} ta {t(i.product, message=message).upper()}  {i.price}</b>\n"
    else:
        temText = t('Siz hali 1 taham buyurtma qilmagansiz', message=message)
    temText = name.upper() + temText
    bot_request('sendMessage', {
        'chat_id': user_id,
        'parse_mode': 'html',
        'text': temText
    }
                )

# check.delivery_price:
def givePhoneRumber(message):
    user_id = message['from']['id']
    user = BotUsers.objects.get(user_id=user_id)
    a = t("Biz bilan bog'laning", message=message)
    tem_text = f"<b>🆘  {a}\n\n📞  {user.branch.branch_number}</b>"
    
    bot_request('sendMessage', {
        'chat_id': user_id,
        'parse_mode': 'html',
        'text': tem_text
    }
                )



def send_to_channel(message, lat, long, text, order_type, ordered_user_id=0):
    user_id = message['from']['id']
    user = BotUsers.objects.get(user_id=user_id)
    telegram_group_id = user.branch.telegram_group_id

    bot_request("sendMessage", {
        'chat_id': telegram_group_id,
        'parse_mode': 'html',
        'text': text,
        'reply_markup': json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {'text': t("Qabul qilish", message=message), 'callback_data': f'qabul_qilindi_{ordered_user_id}'},
                            {'text': t("Yo'lda", message=message), 'callback_data': f'yolda_{ordered_user_id}'}
                        ],
                        [
                            {'text': t("Yakunlash", message=message), 'callback_data': f'tugatildi_{ordered_user_id}'}
                        ]
                    ]
                }
            )
        })
    
    type = t('dastavka', message=message)
    if order_type == type:
        bot_request("sendLocation", {
            'chat_id': user.branch.telegram_group_id,
            'latitude': lat,
            'longitude': long,
            
            })
            




def change_data_from_channel(message, user, change_mode, ordered_user_id=0):
    message_id = message['message']['message_id']
    qabul_qilindi = '✅' in  message['message']['reply_markup']['inline_keyboard'][0][0]['text']
    yolda = '✅' in  message['message']['reply_markup']['inline_keyboard'][0][1]['text']
    tugatildi = '✅' in  message['message']['reply_markup']['inline_keyboard'][1][0]['text']
    if change_mode == 'qabul_qilindi':
        bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("✅ Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })

    elif change_mode == 'yolda':
        if qabul_qilindi == False:
            bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("🚫 Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("✅ Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })
        else:
            bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("✅ Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("✅ Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })
    elif change_mode == 'tugatildi':
        text = f"<b>Qabul qilindi:</b> {qabul_qilindi}\n<b>Chiqarib yuborildi:</b> {yolda}\n<b>Yakunlandi:</b> True"
        bot_request("sendMessage", {
            'chat_id': user.branch.telegram_group_id,
            'parse_mode': 'html',
            "text": text
        })
        if qabul_qilindi == False and yolda == False:
                bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("🚫 Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("🚫 Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("✅ Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })
        elif qabul_qilindi == True and yolda == False:
            bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("✅ Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("🚫 Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("✅ Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })
        elif yolda == True and qabul_qilindi == False:
            bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("🚫 Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("✅ Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("✅ Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })

        else:
            bot_request('editMessageReplyMarkup', {
                    'chat_id': user.branch.telegram_group_id,
                    'message_id': message_id,
                    'reply_markup': json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {'text': t("✅ Qabul qilindi", message=message), 'callback_data': f'qabul_qilindi_{user.user_id}'},
                                {'text': t("✅ Yo'lda", message=message), 'callback_data': f'yolda_{user.user_id}'}
                            ],
                            [
                                {'text': t("✅ Yakunlash", message=message), 'callback_data': f'tugatildi_{user.user_id}'}
                            ]
                        ]
                    }
                )
                })