from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent
from module import func

## 原本的webhook https://noutest.herokuapp.com/callback

nowqa='N'
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    global nowqa
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        #mtext=""
        for event in events:
            if isinstance(event, MessageEvent):                
                if event.message.text.find("@")>0:
                    mtext = event.message.text[event.message.text.find("@"):]                 
                else :
                    mtext = event.message.text

                if event.message.text.find("@A")>0:                    
                    mtext = event.message.text
                
                if mtext == '@個人化設定':
                    nowqa='N' 
                    func.sendConstruct(event)                  
                elif mtext[-7::][0:2]=='@A' : #使用qa_id進行解答呼叫->call sendQnA()
                    #ttext = mtext[-6::]
                    #func.retAns(event,ttext)
                    #func.sendQnA(event, mtext[0:-7])  #QnA     
                    #questext = mtext[0:-7]   
                    mtext = mtext[0:mtext.find("@A")]
                    func.sendQnA(event, mtext)  #QnA                  
                elif mtext == '@教務資訊':
                    nowqa='N' 
                    func.sendConstruct(event)  
                elif mtext == '@註冊選課':
                    nowqa='N' 
                    func.sendConstruct(event)
                elif mtext == '@寄信':
                    nowqa='N' 
                    func.sendemail(event)     
                elif mtext=='@OpenQA':
                    nowqa='Y' #進入開放式問題狀態
                    func.sendOpenQA(event)  
                elif mtext == '@常見問題':  #測試                  
                    func.exeDoorQA(event)                      
                elif mtext == '@DireQA':
                    func.sendDireQA(event)                                           
                elif mtext == '@行事曆':
                    func.sendCalendar(event)  
                elif mtext[0:3]=='@L1': #得到第1層結果，要呼叫第2層(傳入@L1-後的字串[3:])
                    func.exDQALv2(event,mtext[4:])                        
                elif mtext[0:3]=='@L2': #得到第2層結果，要呼叫第3層(傳入@L2-後的字串[3:])
                    inxlv2=mtext[mtext.find("-")+1:mtext.find("_")]
                    inxlv3=mtext[mtext.find("_")+1:]
                    func.exDQALv3(event,inxlv2,inxlv3)   
                elif mtext=='@RTN':
                    func.retExtQue(event,'A02-01')  
                elif nowqa=='Y' and (mtext=='/q' or mtext=='/Q'): #EXIT開放式問答  
                    nowqa='N' 
                    func.sendFinQnA(event)
                #elif nowqa=='Y':   #開放式問答       
                else:
                    func.sendQnA(event, mtext)                                                                
        return HttpResponse()

    else:
        return HttpResponseBadRequest()
