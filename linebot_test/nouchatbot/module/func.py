from django.conf import settings

import os,psycopg2
from linebot.models.events import JoinEvent
from psycopg2 import Error
from linebot.models.template import CarouselColumn, CarouselTemplate #for DB

from linebot import LineBotApi
#from linebot.models import TextSendMessage

from linebot.models import TextSendMessage, TemplateSendMessage, MessageTemplateAction,URIAction, ImageSendMessage
from linebot.models.send_messages import  QuickReply, QuickReplyButton
from linebot.models.actions import MessageAction

import http.client, json
from botapp.models import users

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

#new QA marker published連線資訊 2021/6/13
'''
POST /knowledgebases/36968ced-d7ac-41a9-9ec0-f883c7ccc103/generateAnswer
Host: https://nouqa.azurewebsites.net/qnamaker
Authorization: EndpointKey 236ee310-4f7c-4402-94c2-1715c913da03
Content-Type: application/json
{"question":"<Your question>"}
'''

# old QA marker連線資訊
'''
host = "nouqa.azurewebsites.net"  #主機
endpoint_key = "dd7eb362-0ca4-4b0b-9c7f-925cf8b30101"  #授權碼
kb = "35146f0e-b42e-4b46-99f8-dcbcc15d4b9f"  #GUID碼
method = "/qnamaker/knowledgebases/" + kb + "/generateAnswer"
'''

#CYCU https://cycu1226.herokuapp.com/callback

host = "nouqa.azurewebsites.net"  #主機
endpoint_key = "236ee310-4f7c-4402-94c2-1715c913da03"  #授權碼
kb = "36968ced-d7ac-41a9-9ec0-f883c7ccc103"  #GUID碼
method = "/qnamaker/knowledgebases/" + kb + "/generateAnswer"

def sendConstruct(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='此功能建構中\n敬請期待'))
    '''try:
        message = [
            TextSendMessage(
                text="此功能建構中"
            ),
            #TextSendMessage(
            #    text="敬請期待"
            #),
        ]
        line_bot_api.reply_message(event.reply_token,message))
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    '''
    
def sendemail(event):
    try:
        message = [TextSendMessage(text = "在使用上有遇到問題，歡迎填表單回報，我們會盡快修復\n https://forms.gle/KfyRP9t5JDdHxsp28"),
                   TextSendMessage(text = "如果有其他關於空大e點通的問題歡迎寄信至noubot5632@gapps.nou.edu.tw \n我們將盡快解決！")]
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text = "出錯了"))

def sendOpenQA(event):  #開放式問題解答    
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='gggh'))
    try:
        text1 ='國立空中大學常見問題解答，請直接輸入您的問題。\n若要結束常見問題請輸入 /Q 或 /q'
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendFinQnA(event):  #已結束問題解答    
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='gggh'))
    try:
        text1 ='已結束問題解答...'
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendQnA(event, mtext):  #QnA
    question = {
        'question': mtext,
    }
    content = json.dumps(question)
    headers = {
        'Authorization': 'EndpointKey ' + endpoint_key,
        'Content-Type': 'application/json',
        'Content-Length': len(content)
    }     

    conn = http.client.HTTPSConnection(host)                            
    conn.request ("POST", method, content, headers)      
    response = conn.getresponse()           
    result = json.loads(response.read().decode())                 
    result1 = result['answers'][0]['answer']  
    
    #result1
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='result1'))     
    if 'No good match found' in result1:        
        text1 ='很抱歉，在目前已建立的知識庫裡無法找到此問題解答，請再輸入問題。'

        #將沒有解答的問題寫入資料庫(F:失敗)
        userid = event.source.user_id
        unit = users.objects.create(uid=userid, question=mtext,resSF='F',restext='NA')
        unit.save()        
    else:
        result2 = result1[7:]  #移除「A:XX_XX 」
        text1 = result2  
        
        #將問答結果寫檔 (S:成功)
        userid = event.source.user_id
        unit = users.objects.create(uid=userid, question=mtext,resSF='S',restext=result1[1:6])
        unit.save()  


    message = TextSendMessage(
        text = text1
    )
    line_bot_api.reply_message(event.reply_token,message)

def sendCalendar(event): #空大行事曆，連結到imguar
    try:
        message = [
            TextSendMessage(
                text="國立空中大學111學年度行事曆"
            ),
            ImageSendMessage(
            original_content_url = 'https://i.imgur.com/brkq1Qy.jpg',
            preview_image_url = 'https://i.imgur.com/brkq1Qy.jpg')
        ]
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,message,TextSendMessage(text='發生錯誤!'))

def sendDireQA(event): 
    try:
        message= TextSendMessage (
            text='請選擇想查詢的項目種類:',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="報名入學",text="報名入學 @L1-1")
                    ),  
                    QuickReplyButton(
                        action=MessageAction(label="註冊選課",text="註冊選課 @L1-2")
                    ),                       
                    QuickReplyButton(
                        action=MessageAction(label="學籍管理",text="學籍管理 @L1-3")
                    ),    
                    QuickReplyButton(
                        action=MessageAction(label="畢業相關",text="畢業相關 @L1-4")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="減免申請、就學輔助、特殊生",text="減免申請、就學輔助、特殊生 @L1-5")
                    ), 
                    QuickReplyButton(
                        action=MessageAction(label="考試、成績、獎學金",text="考試、成績、獎學金 @L1-6")
                    ),                        
                    QuickReplyButton(
                        action=MessageAction(label="學分抵免",text="學分抵免 @L1-7")
                    ),    
                    QuickReplyButton(
                        action=MessageAction(label="學生社團活動",text="學生社團活動 @L1-8")
                    ),                                                                           
                    QuickReplyButton(
                        action=MessageAction(label="面授(含視訊)",text="面授(含視訊) @L1-9")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="其他問題",text="其他問題 @L1-10")
                    )
                ]
            )
        )
    
        line_bot_api.reply_message(event.reply_token,message)

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
   
def exeDoorQA(event): #QA入口主要副程式
    try:        
        message = [
            TextSendMessage(text = "如果有其他關於空大e點通的問題歡迎寄信至noubot5632@gapps.nou.edu.tw \n我們將盡快解決！"),
            ImageSendMessage(
            original_content_url = 'https://i.imgur.com/QYckiLM.jpeg',
            preview_image_url = 'https://i.imgur.com/QYckiLM.jpeg'),
            ImageSendMessage(
            original_content_url = 'https://i.imgur.com/D3mhW3b.jpg',
            preview_image_url = 'https://i.imgur.com/D3mhW3b.jpg'),
            TemplateSendMessage(
            alt_text='可使用不同方式進行常見問題',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        #thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                        title='常見問題-引導式問答',
                        text='由系統引導，逐步找到問題方向，並提供解答',
                        actions=[
                            MessageTemplateAction(
                                label='引導式QA',
                                text='@DireQA'
                            ),                            
                        ]
                    ),
                    CarouselColumn(
                        #thumbnail_image_url='https://i.imgur.com/qaAdBkR.png',
                        title='常見問題-開放式問答',
                        text='直接輸入問題，系統辨識問題內容並提供解答',
                        actions=[
                            MessageTemplateAction(
                                label='開放式QA',
                                text='@OpenQA'
                            ),
                        ]
                    )
                ]
            )
        )
        ]



        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def exDQALv2(event,inxlv2):
    level='2'
    try :
        # label="報名入學、註冊選課" , text="@L1-1"        

        ''' DB connect section 先MARK
        DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a noutest').read()[:-1]
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        query_string = "select * from struct_tbl where level=%s and par_id=%s order by par_id, ordseq"
        cursor.execute(query_string, (level, inxlv2,))

        all_fetrecords = cursor.fetchall()                          
        for row in all_fetrecords:
        '''                  
        #cursor.close()
        #conn.close()

        if inxlv2=='1' : #action=MessageAction(label="報名入學",text="@L1-1")
            message= TextSendMessage (
                text='請選擇想跟"報名入學"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="報名資格",text="報名資格 @L2-1_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="報名方式",text="報名方式 @L2-1_2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="報名費用",text="報名費用 @L2-1_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="招生資訊",text="招生資訊 @L2-1_4")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="報名相關其他資訊",text="報名相關其他資訊 @L2-1_5")
                        )                  
                    ]
                )
            )

        elif inxlv2=='2' : #action=MessageAction(label="註冊選課",text="@L1-2 註冊選課")
            message= TextSendMessage (
                text='請選擇想跟"註冊選課"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="選課相關",text="選課相關 @L2-2_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="繳費相關",text="繳費相關 @L2-2_2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="資訊系統登入問題",text="資訊系統登入問題 @L2-2_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="註冊相關其他資訊",text="註冊相關其他資訊 @L2-2_4")
                        ),                                        
                    ]
                )
            )

        elif inxlv2=='3' : #action=MessageAction(label="學籍管理",text="@L1-3")
            message= TextSendMessage (
                text='請選擇想跟"學籍管理"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="休、退學相關",text="休、退學相關 @L2-3_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="學生證相關",text="學生證相關 @L2-3_2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="學籍更新",text="學籍更新 @L2-3_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="學分學程",text="學分學程 @L2-3_4")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="學籍相關其他資訊",text="學籍相關其他資訊 @L2-3_5")
                        ),                                       
                    ]
                )
            )

        elif inxlv2=='4' : #action=MessageAction(label="畢業相關",text="@L1-4") $在DB上是LEVEL2,id=7
            message= TextSendMessage (
                text='請選擇想跟"畢業相關"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="畢業申請",text="畢業申請 @L2-4_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="畢業條件",text="畢業條件 @L2-4_2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="畢業證書",text="畢業證書 @L2-4_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="畢業相關其他資訊",text="畢業相關其他資訊 @L2-4_4")
                        ),                                                             
                    ]
                )
            )

        #action=MessageAction(label="減免申請、就學輔助、特殊生",text="@L1-5") $在DB上是LEVEL2, par_id in ('4','9','10')
        elif inxlv2=='5' : 
            message= TextSendMessage (
                text='請選擇想跟"減免申請、就學輔助、特教生"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="減免申請資格",text="減免申請資格 @L2-5_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="減免相關其他資訊",text="減免相關其他資訊 @L2_5-2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="就學補助",text="就學補助 @L2-5_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="特教生鑑定",text="特教生鑑定 @L2-5_4")
                        ), 
                        QuickReplyButton(
                            action=MessageAction(label="特教生學習協助",text="特教生學習協助 @L2-5_5")
                        ),                                                             
                    ]
                )
            )    

        #action=MessageAction(label="考試、成績、獎學金",text="@L1-6") $在DB上是LEVEL2, par_id in ('12','5','6')
        elif inxlv2=='6' : 
            message= TextSendMessage (
                text='請選擇想跟"考試、成績、獎學金"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="成績計算",text="成績計算 @L2-6_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="平時作業",text="平時作業 @L2-6_2")
                        ),                       
                        QuickReplyButton(
                            action=MessageAction(label="成績相關其他資訊",text="成績相關其他資訊 @L2-6_3")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="獎學金種類",text="獎學金種類 @L2-6_4")
                        ), 
                        QuickReplyButton(
                            action=MessageAction(label="獎學金申請",text="獎學金申請 @L2-6_5")
                        ), 
                        QuickReplyButton(
                            action=MessageAction(label="考試資訊",text="考試資訊 @L2-6_6")
                        ),    
                        QuickReplyButton(
                            action=MessageAction(label="請假、補考",text="請假、補考 @L2-6_7")
                        ), 
                        QuickReplyButton(
                            action=MessageAction(label="考試相關其他資訊",text="考試相關其他資訊 @L2-6_8")
                        ),                                                             
                    ]
                )
            )

        #action=MessageAction(label="學分抵免",text="@L1-7") $在DB上是LEVEL2, par_id ='13'
        elif inxlv2=='7' : 
            message= TextSendMessage (
                text='請選擇想跟"學分抵免"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="抵免辦理事項",text="抵免辦理事項 @L2-7_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="抵免相關規定",text="抵免相關規定 @L2-7_2")
                        ),                                                                                                           
                    ]
                )
            )

        #action=MessageAction(label="學生社團活動",text="@L1-8") $在DB上是LEVEL2, par_id ='8'
        elif inxlv2=='8' : 
            message= TextSendMessage (
                text='請選擇想跟"學生社團活動"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="社團活動",text="社團活動 @L2-8_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="學生會",text="學生會 @L2-8_2")
                        ),                                                                                                           
                    ]
                )
            ) 

        #action=MessageAction(label="面授(含視訊)",text="@L1-9") $在DB上是LEVEL2, par_id ='14'
        elif inxlv2=='9' : 
            message= TextSendMessage (
                text='請選擇想跟"面授(含視訊)"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="面授上課",text="面授上課 @L2-9_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="視訊面授教室系統",text="視訊面授教室系統 @L2-9_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="面授相關其他問題",text="面授相關其他問題 @L2-9_1")
                        ),                                                                                                          
                    ]
                )
            )

        #action=MessageAction(label="其他問題",text="@L1-10") $在DB上是LEVEL2, par_id ='11'
        elif inxlv2=='10' : 
            message= TextSendMessage (
                text='請選擇想跟"其他問題"相關的問題:',
                quick_reply=QuickReply(
                    items=[                    
                        QuickReplyButton(
                            action=MessageAction(label="公務人員終身學習認證",text="公務人員終身學習認證 @L2-10_1")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="心理諮商輔導",text="心理諮商輔導 @L2-10_2")
                        ),  
                        QuickReplyButton(
                            action=MessageAction(label="其他問題",text="其他問題 @L2-10_3")
                        ),                                                                                                          
                    ]
                )
            )    

        line_bot_api.reply_message(event.reply_token,message)
    except:              
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def exDQALv3(event,inxlv2,inxlv3):
    level='3'
    try :
        if inxlv2=='1' : #action=MessageAction(label="報名入學",text="@L1-1")
            if inxlv3=="1": #action=MessageAction(label="報名資格",text="@L2-1_1")
                message = TemplateSendMessage(
                    alt_text='報名資格問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='報名資格問題',
                                text='請問報名資格為何？全修生與選修生的區別為？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問報名資格為何？全修生與選修生的區別為？ @A01-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='大學肄業可以報名嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='大學肄業可以報名嗎？ @A01-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='僑胞可以讀空大嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='僑胞可以讀空大嗎？ @A01-14'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='警察可以讀空大嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='警察可以讀空大嗎？ @A01-15'
                                    ),                            
                                ]
                            ),
                            
                            CarouselColumn(
                                title='報名資格問題',
                                text='我想讀海巡專班',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我想讀海巡專班 @A01-16'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='我有他校專科學歷畢業可以修讀空大嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我有他校專科學歷畢業可以修讀空大嗎？ @A01-17'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='我有他校大學學歷，可以讀空大嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我有他校大學學歷，可以讀空大嗎？ @A01-18'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='外籍配偶可以修讀空大嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='外籍配偶可以修讀空大嗎？ @A01-19'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名資格問題',
                                text='持外國學歷可以報名嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='持外國學歷可以報名嗎？ @A01-20'
                                    ),                            
                                ]
                            ),

                        ]
                    )
                )

            elif inxlv3=="2": #action=MessageAction(label="報名方式",text="@L2-1_2")
                message = TemplateSendMessage(
                    alt_text='報名方式問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='報名方式問題',
                                text='如何網路報名？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何網路報名？ @A01-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名方式問題',
                                text='如何通信報名？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何通信報名？ @A01-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名方式問題',
                                text='如何現場報名？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何現場報名？ @A01-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名方式問題',
                                text='我想讀空大要到哪裡報名？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我想讀空大要到哪裡報名？ @A01-32'
                                    ),                            
                                ]
                            ),
                            
                            CarouselColumn(
                                title='報名方式問題',
                                text='持中華民國居留證如何報名？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='持中華民國居留證如何報名？ @A01-13'
                                    ),                            
                                ]
                            ),                    
                        ]
                    )
                )  

            elif inxlv3=="3": #action=MessageAction(label="報名費用",text="@L2-1_3")
                message = TemplateSendMessage(
                    alt_text='報名費用問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='報名費用問題',
                                text='報名費問題？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='報名費問題？ @A01-12'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名費用問題',
                                text='每學期要繳交多少學費？一個學分費多少錢？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='每學期要繳交多少學費？一個學分費多少錢？ @A01-22'
                                    ),                            
                                ]
                            ),   
                            CarouselColumn(
                                title='報名費用問題',
                                text='我可不可以辦理學分學雜費減免?請問是用什麼樣的身分辦理學雜費減免？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我可不可以辦理學分學雜費減免?請問是用什麼樣的身分辦理學雜費減免？ @A01-10'
                                    ),                            
                                ]
                            ),               
                        ]
                    )
                )  

            elif inxlv3=="4": #action=MessageAction(label="招生資訊",text="@L2-1_4")
                message = TemplateSendMessage(
                    alt_text='招生資訊問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='招生資訊問題',
                                text='如何獲得招生資訊？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何獲得招生資訊？ @A01-21'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='招生資訊問題',
                                text='簡章及報名資料？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='簡章及報名資料？ @A01-29'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='招生資訊問題',
                                text='本校有哪些學系？本校專科部有哪些科系？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='本校有哪些學系？本校專科部有哪些科系？ @A01-30'
                                    ),                            
                                ]
                            ),              
                        ]
                    )
                )               
 
            elif inxlv3=="5": #action=MessageAction(label="報名相關其他資訊",text="@L2-1_5") level='3' and par_id='4'
                message = TemplateSendMessage(
                    alt_text='報名相關其他資訊',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='請問學校上班時間是幾點？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問學校上班時間是幾點？ @A01-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='請問報名方式、日期及開播日？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問報名方式、日期及開播日？ @A01-02'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='錯過了網路報名的時間，怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='錯過了網路報名的時間，怎麼辦？ @A01-03'
                                    ),                            
                                ]
                            ),   
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='念空大能否申請兵役緩徵或儘後召集？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='念空大能否申請兵役緩徵或儘後召集？ @A01-09'
                                    ),                            
                                ]
                            ),   
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='中英文證件申請一定要本人親臨辦理嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='中英文證件申請一定要本人親臨辦理嗎？ @A01-26'
                                    ),                            
                                ]
                            ),   
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='沒有高中畢業證書怎麼報名空大？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='沒有高中畢業證書怎麼報名空大？ @A01-27'
                                    ),                            
                                ]
                            ),     
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='若要申請基本資料變更，要帶什麼資料才能辦理？如何辦理？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='若要申請基本資料變更，要帶什麼資料才能辦理？如何辦理？ @A01-31'
                                    ),                            
                                ]
                            ),     
                            CarouselColumn(
                                title='報名相關其他資訊',
                                text='如已在本校修完大學部/專科部的學生，想再修第二個學位，還需要修幾個學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如已在本校修完大學部/專科部的學生，想再修第二個學位，還需要修幾個學分？ @A01-24'
                                    ),                            
                                ]
                            ),   
                        ]
                    )
                )

        if inxlv2=='2' : #action=MessageAction(label="註冊選課",text="@L2-2") level='3' and par_id='5'
            if inxlv3=="1": #action=MessageAction(label="選課相關",text="@L2-2_1")
                message = TemplateSendMessage(
                    alt_text='選課相關問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='選課相關問題',
                                text='哪裡可以看到選課說明？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='哪裡可以看到選課說明？ @A02-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='選課相關問題',
                                text='我選錯學系，要怎麼改科系？我報錯學系，要改麼改科系？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我選錯學系，要怎麼改科系？我報錯學系，要改麼改科系？ @A02-02'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='請問空大的專班是什麼？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問空大的專班是什麼？ @A02-05'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='請問空大的社工專班是什麼？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問空大的社工專班是什麼？ @A02-04'
                                    ),                            
                                ]
                            ),   
                            CarouselColumn(
                                title='選課相關問題',
                                text='是否可以自行上網選課？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='是否可以自行上網選課？ @A02-10'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='每學期最多能選多少科目(學分)？一學期可選幾門課程？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='每學期最多能選多少科目(學分)？一學期可選幾門課程？ @A02-11'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='選錯科目怎麼辦？選課後還能改選科目？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='選錯科目怎麼辦？選課後還能改選科目？ @A02-12'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='我可以退選嗎？我可以退費嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我可以退選嗎？我可以退費嗎？ @A02-13'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='選課相關問題',
                                text='選課卡怎麼列印？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='選課卡怎麼列印？ @A02-18'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='選課相關問題',
                                text='辦理新生註冊選課，可否託人代辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='辦理新生註冊選課，可否託人代辦？ @A01-25'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 

            if inxlv3=="2": #action=MessageAction(label="繳費相關",text="@L2-2_2") level='3' and par_id='7'
                message = TemplateSendMessage(
                    alt_text='繳費相關問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='繳費相關問題',
                                text='請問如何繳費？ 如何繳納學分學雜費？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問如何繳費？ 如何繳納學分學雜費？ @A02-14'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='繳費相關問題',
                                text='我要如何用信用卡繳費？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我要如何用信用卡繳費？ @A02-21'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='繳費相關問題',
                                text='如何取得繳費證明？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何取得繳費證明？ @A02-20'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 

            if inxlv3=="3": #action=MessageAction(label="資訊系統登入問題",text="@L2-2_3") level='3' and par_id='8'
                message = TemplateSendMessage(
                    alt_text='資訊系統登入問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='資訊系統登入問題',
                                text='為什麼密碼一直無法修改成功？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='為什麼密碼一直無法修改成功？ @A02-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='資訊系統登入問題',
                                text='忘記密碼怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='忘記密碼怎麼辦？ @A02-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='資訊系統登入問題',
                                text='忘記帳號學號該怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='忘記帳號學號該怎麼辦？ @A02-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='資訊系統登入問題',
                                text='網頁顯示登入失敗怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='網頁顯示登入失敗怎麼辦？ @A02-09'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 

            if inxlv3=="4": #action=MessageAction(label="註冊相關其他資訊",text="@L2-2_4") level='3' and par_id='9'
                message = TemplateSendMessage(
                    alt_text='註冊相關其他資訊',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='註冊相關其他資訊',
                                text='如何知道導師班相關資訊？我的導師是誰?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何知道導師班相關資訊？我的導師是誰? @A02-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='註冊相關其他資訊',
                                text='我是其他學校學生，可以選修空大課程嗎?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是其他學校學生，可以選修空大課程嗎? @A02-15'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='註冊相關其他資訊',
                                text='如何購買教科書？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何購買教科書？ @A02-16'
                                    ),                            
                                ]
                            ),        
                            CarouselColumn(
                                title='註冊相關其他資訊',
                                text='如何購買空大課程採用的坊間書籍？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何購買空大課程採用的坊間書籍？ @A02-17'
                                    ),                            
                                ]
                            ),                     
                        ]
                    )
                ) 

        if inxlv2=='3' : #action=MessageAction(label="學籍管理",text="@L2-3")
            if inxlv3=="1": #action=MessageAction(label="休、退學相關",text="@L2-3_1") level='3' and par_id='10'
                message = TemplateSendMessage(
                    alt_text='休、退學相關',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='休、退學相關',
                                text='我已休學好多年了，可以再修學分嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已休學好多年了，可以再修學分嗎？ @A03-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='休、退學相關',
                                text='如何申請退學？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何申請退學？ @A03-03'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='休、退學相關',
                                text='讀了空大之後碰到有事可以休學嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='讀了空大之後碰到有事可以休學嗎？ @A03-04'
                                    ),                            
                                ]
                            ),                             
                        ]
                    )
                ) 

            if inxlv3=="2": #action=MessageAction(label="學生證相關",text="@L2-3_2") level='3' and par_id='11'
                message = TemplateSendMessage(
                    alt_text='學生證相關',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='學生證相關',
                                text='本校學生均會發給學生證嗎? 選修生會有學生證嗎?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='本校學生均會發給學生證嗎? 選修生會有學生證嗎? @A03-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='學生證相關',
                                text='新生學生證何時會發給? 何時可以取得學生證?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='新生學生證何時會發給? 何時可以取得學生證? @A03-06'
                                    ),                            
                                ]
                            ),                                                      
                        ]
                    )
                ) 

            if inxlv3=="3": #action=MessageAction(label="學籍更新",text="@L2-3_3") level='3' and par_id='12'
                message = TemplateSendMessage(
                    alt_text='學籍更新相關',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='學籍更新相關',
                                text='我是選修生如何轉成全修生?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是選修生如何轉成全修生? @A03-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='學籍更新相關',
                                text='舊生註冊選課前為何需更新學籍資料?',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='舊生註冊選課前為何需更新學籍資料? @A03-07'
                                    ),                            
                                ]
                            ),                                                      
                        ]
                    )
                )    

            if inxlv3=="4": # action=MessageAction(label="學分學程",text="@L2-3_4") level='3' and par_id='13'
                message = TemplateSendMessage(
                    alt_text='學分學程相關',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='學分學程相關',
                                text='如何申請學分學程證明書？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何申請學分學程證明書？ @A03-19'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='學分學程相關',
                                text='如何修讀學分學程？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何修讀學分學程？ @A03-09'
                                    ),                            
                                ]
                            ),                                                      
                        ]
                    )
                )  

            if inxlv3=="5": # action=MessageAction(label="學籍相關其他資訊",text="@L2-3_5") level='3' and par_id='14'
                message = TemplateSendMessage(
                    alt_text='學籍相關其他資訊',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='學籍相關其他資訊',
                                text='請問學業成績優良獎狀如何申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問學業成績優良獎狀如何申請 @A03-10'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='學籍相關其他資訊',
                                text='大學部的學生是否可以在修滿80學分時就先取得副學士學位？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='大學部的學生是否可以在修滿80學分時就先取得副學士學位？ @A03-11'
                                    ),                            
                                ]
                            ),    
                            CarouselColumn(
                                title='學籍相關其他資訊',
                                text='如何查詢以前修過的學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何查詢以前修過的學分？A03-08'
                                    ),                            
                                ]
                            ),                                                     
                        ]
                    )
                ) 

        if inxlv2=='4' : #action=MessageAction(label="畢業相關",text="@L2-4") $在DB上是LEVEL2,id=7
            if inxlv3=="1": #action=MessageAction(label="畢業申請",text="@L2-4_1")  level='3' and par_id='22'
                message = TemplateSendMessage(
                    alt_text='畢業申請問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='畢業申請問題',
                                text='請問畢業申請有規定何時提出嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問畢業申請有規定何時提出嗎？ @A07-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='畢業申請問題',
                                text='請問我要如何提出畢業申請呢？我要如何提出畢業申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何提出畢業申請呢？我要如何提出畢業申請？ @A07-02'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='畢業申請問題',
                                text='請問我萬一於申請當下發現應修學分數不足怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我萬一於申請當下發現應修學分數不足怎麼辦？ @A07-06'
                                    ),                            
                                ]
                            ),      
                            CarouselColumn(
                                title='畢業申請問題',
                                text='請問我要如何知道畢業審查結果？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何知道畢業審查結果？ @A07-07'
                                    ),                            
                                ]
                            ),                         
                        ]
                    )
                ) 

            if inxlv3=="2": #action=MessageAction(label="畢業條件",text="@L2-4_2")  level='3' and par_id='23'
                message = TemplateSendMessage(
                    alt_text='畢業條件問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='畢業條件問題',
                                text='請問我要如何知道自己有沒有符合畢業條件呢？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何知道自己有沒有符合畢業條件呢？ @A07-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='畢業條件問題',
                                text='學分學程是否為畢業條件？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學分學程是否為畢業條件？ @A07-04'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='畢業條件問題',
                                text='請問要如何知道我選的科目可不可以採計到主修學系呢？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問要如何知道我選的科目可不可以採計到主修學系呢？ @A07-05'
                                    ),                            
                                ]
                            ),      
                            CarouselColumn(
                                title='畢業條件問題',
                                text='空大的畢業條件？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='空大的畢業條件？ @A01-23'
                                    ),                            
                                ]
                            ),                         
                        ]
                    )
                ) 

            if inxlv3=="3": #action=MessageAction(label="畢業證書",text="@L2-4_3")  level='3' and par_id='24'
                message = TemplateSendMessage(
                    alt_text='畢業證書問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='畢業證書問題',
                                text='請問我要參加相關考試或要應徵工作，可否先申請畢業證書？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要參加相關考試或要應徵工作，可否先申請畢業證書？ @A07-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='畢業證書問題',
                                text='請問我什麼時候可以領到畢業證書？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我什麼時候可以領到畢業證書？ @A07-09'
                                    ),                            
                                ]
                            ), 
                            CarouselColumn(
                                title='畢業證書問題',
                                text='畢業證書可以委託他人領取嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='畢業證書可以委託他人領取嗎？ @A07-10'
                                    ),                            
                                ]
                            ),                                                         
                        ]
                    )
                ) 

            if inxlv3=="4": #action=MessageAction(label="畢業相關其他資訊",text="@L2-4_4")  level='3' and par_id='25'
                message = TemplateSendMessage(
                    alt_text='畢業相關其他資訊',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='畢業證書問題',
                                text='學校何時舉行畢業典禮？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學校何時舉行畢業典禮？ @A07-11'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='畢業相關其他資訊',
                                text='請問選修生修得40學分以後，40學分能否併計畢業學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問選修生修得40學分以後，40學分能否併計畢業學分？ @A01-28'
                                    ),                            
                                ]
                            ),                                                                                   
                        ]
                    )
                )                
        
        if inxlv2=='5' : ##action=MessageAction(label="減免申請、就學輔助、特殊生",text="@L2-5") --減免申請4、就學輔助9、特殊生10
            if inxlv3=="1": #action=MessageAction(label="減免申請資格",text="@L2-5_1")  level='3' and and par_id='15'
                message = TemplateSendMessage(
                    alt_text='減免申請、就學輔助、特殊生問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='減免申請資格',
                                text='在他校專科以上學校肄業到空大讀書，還可以辦學雜費減免嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='在他校專科以上學校肄業到空大讀書，還可以辦學雜費減免嗎？ @A04-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我已經完成身心障礙人士子女減免學費申請且已繳費，為什麼還會接到補繳費通知？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='A04-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我已經完成原住民學費減免申請且已繳費，為什麼還會接到補繳費通知？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已經完成原住民學費減免申請且已繳費，為什麼還會接到補繳費通知？ @A04-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我已經完成中低收入戶學費減免申請且已繳費，為什麼還會接到補繳費通知？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已經完成中低收入戶學費減免申請且已繳費，為什麼還會接到補繳費通知？ @A04-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我已經完成低收入戶學費減免申請且已繳費，為什麼還會接到補繳費通知？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已經完成低收入戶學費減免申請且已繳費，為什麼還會接到補繳費通知？ @A04-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我已完成特殊境遇家庭之子女或孫子女學費減免申請且已繳費，為什麼還會接到補繳費通知？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已完成特殊境遇家庭之子女或孫子女學費減免申請且已繳費，為什麼還會接到補繳費通知？ @A04-09'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我在空大完成學費減免申請，已經繳費、上課，還可以在其他學校辦學費減免嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我在空大完成學費減免申請，已經繳費、上課，還可以在其他學校辦學費減免嗎？ @A04-10'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免申請資格',
                                text='我的年齡是否可以報名入學與申請減免學分學雜費？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我的年齡是否可以報名入學與申請減免學分學雜費？ @A04-11'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
            
            if inxlv3=="2": #action=MessageAction(label="減免相關其他資訊",text="@L2-5_2")  level='3' and and par_id='16'
                message = TemplateSendMessage(
                    alt_text='減免申請、就學輔助、特殊生問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='減免相關其他資訊',
                                text='何時要提出申請減免學費？忘記申請可以補辦嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='何時要提出申請減免學費？忘記申請可以補辦嗎？ @A04-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免相關其他資訊',
                                text='選課繳費後，可以申請減免學費嗎？選課但尚未繳費，可以申請減免學費嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='選課繳費後，可以申請減免學費嗎？選課但尚未繳費，可以申請減免學費嗎？ @A04-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='減免相關其他資訊',
                                text='我已經完成減免申請，為什麼印出來的繳費單還是全額？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我已經完成減免申請，為什麼印出來的繳費單還是全額？ @A04-04'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="3": #action=MessageAction(label="就學補助",text="@L2-5_3")  level='3' and and par_id='28'
                message = TemplateSendMessage(
                    alt_text='減免申請、就學輔助、特殊生問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='就學補助',
                                text='遭遇重大變故或重大災害，學校可以提供協助嗎﹖怎麼申請急難慰問金﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='遭遇重大變故或重大災害，學校可以提供協助嗎﹖怎麼申請急難慰問金﹖ @A09-01'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
            
            if inxlv3=="4": #action=MessageAction(label="特教生鑑定",text="@L2-5_4")  level='3' and and par_id='29'
                message = TemplateSendMessage(
                    alt_text='減免申請、就學輔助、特殊生問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='特教生鑑定',
                                text='請問特殊教育學生鑑定如何申請？我是身心障礙人士，學校有發獎助學金嗎',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問特殊教育學生鑑定如何申請？我是身心障礙人士，學校有發獎助學金嗎 @A10-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='特教生鑑定',
                                text='我的特殊教育學生鑑定證明書遺失了，請問要如何申請補發？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我的特殊教育學生鑑定證明書遺失了，請問要如何申請補發？ @A10-02'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
            
            if inxlv3=="5": #action=MessageAction(label="減免申請資格",text="@L2-5_5")  level='3' and and par_id='30'
                message = TemplateSendMessage(
                    alt_text='減免申請、就學輔助、特殊生問題',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='特教生學習協助',
                                text='我是視障生想要申請點字書或有聲書，請問要如何申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是視障生想要申請點字書或有聲書，請問要如何申請？ @A10-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='特教生學習協助',
                                text='請問我要如何申請輔具？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何申請輔具？ @A10-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='特教生學習協助',
                                text='我是聽障人士，面授時可不可以申請手語翻譯﹖我是身障人士，面授時學校可以提供協助嗎﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是聽障人士，面授時可不可以申請手語翻譯﹖我是身障人士，面授時學校可以提供協助嗎﹖ @A10-05'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
            
        if inxlv2=='6' : ##action=MessageAction(label="考試、成績、獎學金",text="@L2-6") --考試12、成績管理5、獎學金6
            if inxlv3=="1": #action=MessageAction(label="成績計算",text="@L2-6_1")  level='3' and and par_id='17'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='成績計算',
                                text='學期平均成績怎麼算？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學期平均成績怎麼算？ @A05-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='成績計算',
                                text='學期總成績怎麼計算？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學期總成績怎麼計算？ @A05-03'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="2": #action=MessageAction(label="平時作業",text="@L2-6_2")  level='3' and and par_id='18'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='平時作業',
                                text='平時作業繳交時間？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='平時作業繳交時間？ @A05-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='平時作業',
                                text='平時作業題目如何取得？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='平時作業題目如何取得？ @A05-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='平時作業',
                                text='平時作業已繳交卻未看到成績？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='平時作業已繳交卻未看到成績？ @A05-12'
                                    ),                            
                                ]
                            ),CarouselColumn(
                                title='平時作業',
                                text='公告的平時作業成績和老師給我的成績有誤差，該怎麼辦？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='公告的平時作業成績和老師給我的成績有誤差，該怎麼辦？ @A05-12'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="3": #action=MessageAction(label="成績相關其他資訊",text="@L2-6_3")  level='3' and and par_id='19'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='成績相關其他資訊',
                                text='教務處行事曆公告於何處？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='教務處行事曆公告於何處？ @A05-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='成績相關其他資訊',
                                text='我對成績有疑問，可以申請複查嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我對成績有疑問，可以申請複查嗎？ @A05-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='成績相關其他資訊',
                                text='請問我要如何申請操行成績？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何申請操行成績？ @A05-11'
                                    ),                            
                                ]
                            ),CarouselColumn(
                                title='成績相關其他資訊',
                                text='公告成績日期為何？成績公告日期為何？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='公告成績日期為何？成績公告日期為何？ @A02-03'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="4": #action=MessageAction(label="獎學金種類",text="@L2-6_3")  level='3' and and par_id='20'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='獎學金種類',
                                text='學校有哪些獎學金可以申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學校有哪些獎學金可以申請？ @A06-01'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="5": #action=MessageAction(label="獎學金申請",text="@L2-6_4")  level='3' and and par_id='21'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='獎學金申請',
                                text='學業成績優秀獎學金如何申請？特殊成就學生獎學金怎麼申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學業成績優秀獎學金如何申請？特殊成就學生獎學金怎麼申請？ @A06-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='獎學金申請',
                                text='請問原住民獎學金怎麼申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問原住民獎學金怎麼申請？ @A06-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='獎學金申請',
                                text='請問新住民獎學金怎麼申請？請問新住民子女獎學金怎麼申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問新住民獎學金怎麼申請？請問新住民子女獎學金怎麼申請？ @A06-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='獎學金申請',
                                text='我是新住民的子女，可以申請獎學金嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是新住民的子女，可以申請獎學金嗎？ @A06-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='獎學金申請',
                                text='身心障礙學生獎補助金怎麼申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='身心障礙學生獎補助金怎麼申請？ @A06-06'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="6": #action=MessageAction(label="考試資訊",text="@L2-6_5")  level='3' and and par_id='33'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='考試資訊',
                                text='考試後參考答案及歷屆考題在哪裡公告？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='考試後參考答案及歷屆考題在哪裡公告？ @A12-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='考試資訊',
                                text='考試發現試題（題目）有疑義（問題），應該如何提出釋疑？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='試發現試題（題目）有疑義（問題），應該如何提出釋疑？ @A12-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='考試資訊',
                                text='請問要去哪裡看考試資訊？期中考試或期末考試命題範圍、試題題型何時公告？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問要去哪裡看考試資訊？期中考試或期末考試命題範圍、試題題型何時公告？ @A12-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='考試資訊',
                                text='一學期有幾次考試？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='一學期有幾次考試？ @A05-02'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="7": #action=MessageAction(label="請假、補考",text="@L2-6_6")  level='3' and and par_id='34'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='請假、補考',
                                text='期中考試或期末考試如何申請補考？期中考試、期末考試請假如何辦理？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='期中考試或期末考試如何申請補考？期中考試、期末考試請假如何辦理？ @A12-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='請假、補考',
                                text='我沒有參加期中考怎麼辦，可以補救嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我沒有參加期中考怎麼辦，可以補救嗎？ @A05-09'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='請假、補考',
                                text='我沒有參加期末考怎麼辦？該如何補救？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我沒有參加期末考怎麼辦？該如何補救？ @A05-10'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="8": #action=MessageAction(label="考試相關其他資訊",text="@L2-6_7")  level='3' and and par_id='35'
                message = TemplateSendMessage(
                    alt_text='考試、成績、獎學金',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='考試相關其他資訊',
                                text='我是身心障礙人士，可以申請以特殊方式考試嗎？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我是身心障礙人士，可以申請以特殊方式考試嗎？ @A05-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='考試相關其他資訊',
                                text='什麼是二次考查，怎麼申請？二次考查如何申請？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='什麼是二次考查，怎麼申請？二次考查如何申請？ @A12-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='考試相關其他資訊',
                                text='考試若忘了帶學生證怎麼辦？考試若忘了帶身分證怎麼辦？考試應攜帶什麼證件﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='考試若忘了帶學生證怎麼辦？考試若忘了帶身分證怎麼辦？考試應攜帶什麼證件﹖ @A12-07'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
        if inxlv2=='7' : ##action=MessageAction(label="學分抵免",text="@L2-7") --學分抵免13
            if inxlv3=="1": #action=MessageAction(label="抵免辦理",text="@L2-7_1")  level='3' and and par_id='36'
                message = TemplateSendMessage(
                    alt_text='學分抵免',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='抵免辦理',
                                text='學分抵免何時辦理？如何辦理學分抵免﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學分抵免何時辦理？如何辦理學分抵免﹖ @A13-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='抵免辦理',
                                text='學分抵免辦理資格？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學分抵免辦理資格？ @A13-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='抵免辦理',
                                text='學分抵免總共可抵免多少學分？學分抵免數量上限﹖學分抵免總額是多少﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='學分抵免總共可抵免多少學分？學分抵免數量上限﹖學分抵免總額是多少﹖ @A13-10'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="2": #action=MessageAction(label="相關身分辦理",text="@L2-7_2")  level='3' and and par_id='37'
                message = TemplateSendMessage(
                    alt_text='學分抵免',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='相關身分辦理',
                                text='大學以上畢業學歷可以抵免多少學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='大學以上畢業學歷可以抵免多少學分？ @A13-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='專科畢業學歷可以抵免多少學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='專科畢業學歷可以抵免多少學分？ @A13-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='專科肄業可以抵免多少學分？大學肄業可以抵免多少學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='專科肄業可以抵免多少學分？大學肄業可以抵免多少學分？ @A13-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='有外語證書可否抵免學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='有外語證書可否抵免學分？ @A13-06'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='在空大推廣教育中心修的學分可否抵免？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='在空大推廣教育中心修的學分可否抵免？ @A13-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='在他校的推廣教育中心修的學分是否可以抵免？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='在他校的推廣教育中心修的學分是否可以抵免 @A13-08'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='相關身分辦理',
                                text='社區大學的學分是否可以抵免？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='社區大學的學分是否可以抵免？ @A13-09'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
        if inxlv2=='8' : ##action=MessageAction(label="學生社團活動",text="@L2-8") --學生社團13
            if inxlv3=="1": #action=MessageAction(label="社團活動",text="@L2-8_1")  level='3' and and par_id='26'
                message = TemplateSendMessage(
                    alt_text='學生社團活動',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='社團活動',
                                text='空大學生有沒有學生社團活動？ ',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='空大學生有沒有學生社團活動？ @A08-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='社團活動',
                                text='如何加入學生社團？ ',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何加入學生社團？ @A08-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='社團活動',
                                text='一般社會大眾可以參加空大的社團活動嗎？ ',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='一般社會大眾可以參加空大的社團活動嗎？ @A08-03'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="2": #action=MessageAction(label="學生會",text="@L2-8_2")  level='3' and and par_id='27'
                message = TemplateSendMessage(
                    alt_text='學生社團活動',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='學生會',
                                text='如何加入學生會？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何加入學生會？ @A08-04'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
        if inxlv2=='9' : ##action=MessageAction(label="面授(含視訊)",text="@L2-9") --面授(含視訊)14
            if inxlv3=="1": #action=MessageAction(label="面授上課",text="@L2-9_1")  level='3' and and par_id='38'
                message = TemplateSendMessage(
                    alt_text='面授(含視訊)',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='面授上課',
                                text='空大的上課方式有哪些？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='空大的上課方式有哪些？ @A14-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授上課',
                                text='我要如何聯絡面授老師﹖我要如何聯絡班代？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我要如何聯絡面授老師﹖我要如何聯絡班代？ @A14-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授上課',
                                text='我錯過面授上課，怎麼辦﹖我錯過視訊面授課，怎麼辦﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我錯過面授上課，怎麼辦﹖我錯過視訊面授課，怎麼辦﹖ @A14-05'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授上課',
                                text='如何得知上課日期、時間、地點？/如何查詢上課時間及地點？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何得知上課日期、時間、地點？/如何查詢上課時間及地點？ @A14-06'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="2": #action=MessageAction(label="面授問題",text="@L2-9_2")  level='3' and and par_id='39'
                message = TemplateSendMessage(
                    alt_text='面授(含視訊)',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='面授問題',
                                text='如何進入視訊面授教室？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何進入視訊面授教室？ @A14-09'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='我的瀏覽器為什麼不能進入視訊面授教室？為什麼我用Webex App沒辦法登入視訊面授課程﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我的瀏覽器為什麼不能進入視訊面授教室？為什麼我用Webex App沒辦法登入視訊面授課程﹖@A14-10'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='視訊面授課程會不會點名？視訊面授當日要上班，是否要請假？如何請假？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='視訊面授課程會不會點名？視訊面授當日要上班，是否要請假？如何請假？ @A14-18'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='為什麼視訊面授聽不到老師的聲音？為什麼視訊面授時我沒辦法發言﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='為什麼視訊面授聽不到老師的聲音？為什麼視訊面授時我沒辦法發言﹖ @A14-11'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='視訊面授時為何無法下載檔案？（老師說同學們可以下載檔案，但無法下載？）',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='視訊面授時為何無法下載檔案？（老師說同學們可以下載檔案，但無法下載？） @A14-12'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='為什麼我無法登入視訊面授教室？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='為什麼我無法登入視訊面授教室？ @A14-13'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='視訊面授中，為什麼老師聲音或影像斷斷續續不順暢？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='視訊面授中，為什麼老師聲音或影像斷斷續續不順暢？ @A14-14'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='連線音訊一直轉圈無法連線音訊？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='連線音訊一直轉圈無法連線音訊？ @A14-15'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='視訊面授時，電腦下載安裝webex.exe或加入會議顯示「在下載會議元件時無法獲取正確的參數」錯誤訊息',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='視訊面授時，電腦下載安裝webex.exe或加入會議顯示「在下載會議元件時無法獲取正確的參數」錯誤訊息 @A14-16'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授問題',
                                text='視訊面授Webex系統如何變更成中文？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='視訊面授Webex系統如何變更成中文？ @A14-17'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="3": #action=MessageAction(label="面授相關其他資訊",text="@L2-9_3")  level='3' and and par_id='40'
                message = TemplateSendMessage(
                    alt_text='面授(含視訊)',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='面授相關其他資訊',
                                text='如何查詢作業題目？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何查詢作業題目？ @A14-03'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授相關其他資訊',
                                text='我的電子郵件信箱怎麼進入？我的信箱怎麼進入？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='我的電子郵件信箱怎麼進入？我的信箱怎麼進入？ @A14-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授相關其他資訊',
                                text='數位學習平台怎麼進入？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='數位學習平台怎麼進入 @A14-07'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='面授相關其他資訊',
                                text='如何進入留言版？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何進入留言版？ @A14-08'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
        if inxlv2=='10' : ##action=MessageAction(label="其他",text="@L2-10") --其他11
            if inxlv3=="1": #action=MessageAction(label="公務人員終身學習認證",text="@L2-10_1")  level='3' and and par_id='31'
                message = TemplateSendMessage(
                    alt_text='其他',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='公務人員終身學習認證',
                                text='如何申請公務人員終身學習認證？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如何申請公務人員終身學習認證？ @A11-01'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='公務人員終身學習認證',
                                text='如果有心理困擾想尋求諮商輔導，應如何申請？請問我要如何申請諮商？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='如果有心理困擾想尋求諮商輔導，應如何申請？請問我要如何申請諮商？ @A11-02'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='公務人員終身學習認證',
                                text='請問我要如何申請班代感謝狀？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='請問我要如何申請班代感謝狀？ @A11-03'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="2": #action=MessageAction(label="心理諮商輔導",text="@L2-10_2")  level='3' and and par_id='32'
                message = TemplateSendMessage(
                    alt_text='其他',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='心理諮商輔導',
                                text='空大學生可以到其他大學修課嗎？空大學生可以跨校選課嗎﹖',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='空大學生可以到其他大學修課嗎？空大學生可以跨校選課嗎﹖ @A11-04'
                                    ),                            
                                ]
                            ),
                            CarouselColumn(
                                title='心理諮商輔導',
                                text='請問學校上班時間是幾點？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text=' 請問學校上班時間是幾點？ @A01-01'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
            if inxlv3=="3": #action=MessageAction(label="其他問題",text="@L2-10_3")  level='3' and and par_id='41'
                message = TemplateSendMessage(
                    alt_text='其他',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='其他問題',
                                text='大學以上畢業學歷可以抵免多少學分？',
                                actions=[
                                    MessageTemplateAction(
                                        label='我要看解答',
                                        text='大學以上畢業學歷可以抵免多少學分？ @A013-03'
                                    ),                            
                                ]
                            ),
                        ]
                    )
                ) 
        
        line_bot_api.reply_message(event.reply_token,message)
    except:              
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def retAns(event,ansInx):    
    try:        
        message=TextSendMessage(text = ansInx)

        # DB connect section 
        DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a noutest').read()[:-1]
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
       
        query_string = "select qa_dtl from qadata_tbl where qa_id=%(qaid)s"
        cursor.execute(query_string,{ 'qaid': ansInx})        

        myfetrecords = cursor.fetchall()                          
                                
        for row in myfetrecords:
            text1 = row[0]       
        
        cursor.close()
        conn.close() 
    
        message=TextSendMessage(text = text1)
           
        line_bot_api.reply_message(event.reply_token,message)
    except:              
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def retExtQue(event,ansInx):
    try:        
        
        # DB connect section 
        
        DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a noutest').read()[:-1]
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
       
        #query_string = "select ext_qa_id,ex_hints from extend_tbl where ans_qa_id=%(qaid)s"
        #cursor.execute(query_string,{ 'qaid': ansInx})        
        
        query_string = "select ext_qa_id,ext_hints from extend_tbl where ans_qa_id=%(qaid)s"
        cursor.execute(query_string,{ 'qaid': ansInx})

        #找到對應的延伸問題才執行回應程式段落
        rtnmessage_text = cursor.fetchone()                          
        text=''

        if (not rtnmessage_text is None):   
            rows = cursor.fetchall()
            cursor.close()
            conn.close() 
            
            thr=[]
            #for row in rows:              
            thr.append(
                MessageTemplateAction(
                    label='123',
                    text='456',
                ),  
            )

            #程式範例 https://ithelp.ithome.com.tw/articles/10269304
            #程式範例2 https://ithelp.ithome.com.tw/articles/10221847

            '''                        
            text1 = TemplateSendMessage(                                      
                alt_text='延伸問題',
                template=CarouselTemplate (
                    columns=[
                        CarouselColumn(
                            #thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                            title='常見問題-引導式問答',
                            text='由系統引導，逐步找到問題方向，並提供解答',
                            actions=[
                                thr                            
                            ]                            
                        )
                    ]                    
                )
            )
            '''

            #rtnresult.append({'ext_id':row[0],'ext_hints':row[1]})
            #print(row[0], '(' + row[1] + ')')                   
          
        if (not thr is None):  
            text1="".join(thr)
            message = TextSendMessage(text= text1)             
            line_bot_api.reply_message(event.reply_token,message)                               
    except:              
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
