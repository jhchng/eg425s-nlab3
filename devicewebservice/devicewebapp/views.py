from django.shortcuts import render
import pymongo
import json

from devicewebapp.mqttdev import xdata, ydata, motor_on
#import socketio

from datetime import datetime as dt

#for post request with query
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return render(request,'devicewebapp/index.html')

def viewdevices(request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["UIOT"]
    mycol = mydb["Devices"]
    devconncol = mydb["DeviceConns"]

    viewdevices = []
    viewdeviceconns = []

    for device in mycol.find():
        viewdevices.append(device)

    for devconns in devconncol.find():
        viewdeviceconns.append(devconns)
        print(devconns)

    devdata = {'viewdevicesdata': viewdevices, 'viewdeviceconndata':viewdeviceconns}
    return render(request,'devicewebapp/viewdevices.html',context=devdata)

def devices(request,param1):
    dev_name = param1
    dtnow = dt.now()

    iotdev = { "name": dev_name, "datetime": dtnow }

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["UIOT"]
    mycol = mydb["Devices"]
    devconncol = mydb["DeviceConns"]

    viewdevices = []
    for device in mycol.find({'name':dev_name}):
        viewdevices.append(device)

    if (len(viewdevices) >= 1):
        iotdevlog={ "name": dev_name, "datetime": dtnow, "status":"updated" }
        y = devconncol.insert_one(iotdevlog)
        dev_name = "{} updated in DB".format(dev_name)
    else:
        x = mycol.insert_one(iotdev)
        iotdevlog={ "name": dev_name, "datetime": dtnow, "status":"new" }
        y = devconncol.insert_one(iotdevlog)
        dev_name = "{} device has been recorded!!".format(dev_name)

    return render(request, 'devicewebapp/devices.html', context={'data': dev_name})
    #return render(request, 'devicewebapp/devices.html', context={'data': iotdev, 'datalog': iotdevlog, 'msg_display': res_dev_name})

@csrf_exempt
def postview(request):
    if request.method == 'POST':
        usrname = request.POST.get('username')
        passwd = request.POST.get('password')
        print("HTTP-POST: username:{} and password:{}".format(usrname,passwd))
        return HttpResponse("POST Request data {} with {} sent- successful".format(usrname,passwd))

    elif request.method == 'GET':
        if request.GET.get('username',''):
            usrname = request.GET.get('username','')
            access_token=request.GET.get('token','')
            if access_token != "":
                print("username:{} | token:{} - HTTP-GET successful".format(usrname,access_token))
                response_data = {"username": usrname, "token received": access_token}
            else:
                print("username:{} - HTTP-GET successful".format(usrname))
                response_data = {"username": usrname, "time queried": dt.now().strftime("%d-%m-%Y %H:%M:%S")}
            return JsonResponse(response_data)
            #return HttpResponse("Request {} exist with {} - HTTP-GET successful".format(usrname,passwd))
        else:
            qstring=request.GET.get('search','')
            print("HTTP-GET: query string:{}".format(qstring))
            return HttpResponse("HTTP-GET: Query Done - {}".format(qstring))

    else:
        print("Error - Request is Invalid {}".format(request))
        return HttpResponse("Request {} with {} - HTTP-GET error in data".format(usrname,passwd))

def messageview(request):
    getydata=""
    getxdata=0

    #data received from mqttdev.py module
    print("xdata:{}".format(xdata))
    print("ydata:{}".format(ydata))

    #data received from mqttdev.py module assigned to local variable to be passed to html
    getxdata=xdata
    getydata=ydata
    print("getxdata:{}".format(getxdata))
    print("getydata:{}".format(getydata))

    return render(request,'devicewebapp/messageview.html',context={'yetdata':getydata,'getdata': getxdata})

def activatemotorview(request):
    # import function to run
    #from path_to_script import function_to_run
    # call function
    #function_to_run()
    # return user to required page
    if request.method == 'POST' and 'activate' in request.POST:
        print("Run script request received {}".format(request.POST.get('activate')))
        activate_value=request.POST.get('activate')
        print("Activate:{}".format(activate_value))
        motor_on(activate_value)
    elif request.method == 'POST' and 'deactivate' in request.POST:
        print("Run script request received {}".format(request.POST.get('deactivate')))
        activate_value=request.POST.get('deactivate')
        print("Dectivate:{}".format(activate_value))
        motor_on(activate_value)
    return HttpResponseRedirect(reverse(messageview))
