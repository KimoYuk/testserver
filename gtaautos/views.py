from django.shortcuts import render, redirect
from gtaautos.models import Autos
import sys, os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from gyazo import Api
import io

# Create your views here.

def get_car(car):
    pricetxt = 'Название: {}\nСалон: {}\nС салона: {} руб.\nГос: {} руб.\n\n'.format(car[0], car[6], car[1],
                                                                         car[2])
    price = '{:{fill}{align}{width}}'.format('Цена', fill='-', align='^', width=50)
    price = '{}\n\n{}'.format(price, pricetxt)

    stocktxt = 'Макс. скорость: {} км/ч\nДо 100: {} секунд\nРемонт: {} руб.'.format(car[3], car[4],
                                                                                    car[5])
    stock = '{:{fill}{align}{width}}'.format('Сток', fill='-', align='^', width=50)
    stock = '{}\n\n{}'.format(stock, stocktxt)
    return price+stock

def add_info(car):
    im1 = Image.open(car[-1])
    width, height = im1.size
    line=get_car(car)
    img = Image.new("RGB", (350, 450))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("gtaautos/static/gtaautos/Roboto-Regular.ttf", 23, layout_engine=ImageFont.LAYOUT_BASIC)
    draw.text((175, 80),line,(255,255,255),font=font, anchor='ms')
    back_im = im1.copy()
    back_im.paste(img, (width-350, (height-450)//2))
    byte_arr=io.BytesIO()
    back_im.save(byte_arr, format='PNG')
    back_im = byte_arr.getvalue()
    url=upload_to_gyazo(back_im)
    print(url)
    return url

def upload_to_gyazo(img):
    acctoken = "6836cd34545bea27d299fe39d711e1da7689f6b6f594bf263af0a81d50752137"
    client = Api(access_token=acctoken)
    image = client.upload_image(img)
    return image.url

def get_base_context(request, pagename):
    return {
        'pagename': pagename,
        'user': request.user,
    }

def index(request):
    context = get_base_context(request, 'Index')
    context['autos'] = Autos.objects.filter()
    return render(request, 'gtaautos/index.html', context)

def addcar(request):
    context = get_base_context(request, 'Addcar')
    if request.method == 'POST' and request.FILES['picture']:
        picture = request.FILES['picture']
        car=[request.POST.get('name'),request.POST.get('price'),request.POST.get('pricegos'),request.POST.get('max'),request.POST.get('tohun'),request.POST.get('repair'),request.POST.get('salon'),request.POST.get('type'),request.POST.get('addinfo'),picture.file]
        picture = add_info(car)
        print(request.POST.get('server'))
        record = Autos(
            server=request.POST.get('server'),
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            sellprice=request.POST.get('pricegos'),
            maxspeed=request.POST.get('max'),
            tohun=request.POST.get('tohun'),
            salon=request.POST.get('salon'),
            type=request.POST.get('type'),
            picture=picture,
            addinfo=request.POST.get('addinfo'),
            repair=request.POST.get('repair')
        )
        print(record)
        record.save()
    return render(request, 'gtaautos/addcar.html', context)

def editcar(request):
    
    context = get_base_context(request, 'Editcar')
    if request.method == 'POST' and request.POST.get('action')=='name':
        car=request.POST.get('name')
        print(car)
        info = Autos.objects.filter(name=car)
        context['info']=info
        context['action'] = 'editcar'
    elif request.method == 'POST' and request.POST.get('action')=='editcar':
        picture = request.FILES['picture']
        cars = [request.POST.get('name'), request.POST.get('price'), request.POST.get('pricegos'),
               request.POST.get('max'), request.POST.get('tohun'), request.POST.get('repair'),
               request.POST.get('salon'), request.POST.get('type'), request.POST.get('addinfo'), picture.file]
        picture = add_info(cars)
        car = request.POST.get('name')
        info = Autos.objects.get(name=car)
        info.server=request.POST.get('server')
        info.name=request.POST.get('name')
        info.price=request.POST.get('price')
        info.sellprice=request.POST.get('pricegos')
        info.maxspeed=request.POST.get('max')
        info.tohun=request.POST.get('tohun')
        info.salon=request.POST.get('salon')
        info.type=request.POST.get('type')
        info.picture=picture
        info.addinfo=request.POST.get('addinfo')
        info.repair=request.POST.get('repair')
        info.save()
        return redirect("index")
    elif request.method == 'GET':
        context['action']='findname'
        print('d')
    return render(request, 'gtaautos/editcar.html', context)

def serverlist(request):
    context = get_base_context(request, 'Serverlist')
    print(Autos.objects.values('server').distinct())
    context['servers']=Autos.objects.values('server').distinct()
    return render(request, 'gtaautos/serverlist.html', context)

def autoslist(request, server):
    servers=Autos.objects.values('server').distinct()
    context = get_base_context(request, 'Autoslist')
    context['autos']=Autos.objects.filter(server=servers[int(server)]['server']).values('name')
    return render(request, 'gtaautos/autoslist.html', context)

def autopage(request, server, auto):
    context = get_base_context(request, 'Autopage')
    servers=Autos.objects.values('server').distinct()
    autos=Autos.objects.filter(server=servers[int(server)]['server']).values('name')
    context['auto']=Autos.objects.filter(name=autos[int(auto)]['name'],server=servers[int(server)]['server']).get()
    print(context['auto'].name)
    return render(request, 'gtaautos/autopage.html', context)

