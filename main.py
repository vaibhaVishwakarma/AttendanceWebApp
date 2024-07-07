from typing import List
from fastapi import FastAPI, Form, Request 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from datetime import datetime
import pickle
from mangum import Mangum
from dependencies import uvicorn


app=FastAPI()
handler = Mangum(app)
# Allow all origins for simplicity (configure this appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataItem(BaseModel):
    values: List[List[str]]

class ResponseModel(BaseModel):
    status: str
    data_received: List[List[str]]
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory = "templates")

@app.get("/",response_class = HTMLResponse)
async def getpage(request : Request):
    with open("./static/counter.pkl" , "rb") as f:
        num = pickle.load(f)
        
    with open("./static/counter.pkl" , "wb") as f:
        print(num)
        pickle.dump(num+1 , f)
    return templates.TemplateResponse("./index.html",{"request":request,"viewCount":num}) 




    
@app.post("/submit" , response_model=ResponseModel)
async def handle_form_submission(data:DataItem):
    print(data.values)
    tt,abtt=None , None 
    try:
        days = ['mon','tue','wed','thu','fri','sat','sun']
        months = {
            1:31, 2:29 , 3:31 , 4:30 , 5:31 , 6 :30 , 7:31 , 8:31 , 9:30,10:31 , 11:30,12:31
        }
        class ll :
            def __init__(self,val=None , node = None):
                self.val = val
                self.next =node
        daysll = ll(days[0],ll(days[1],ll(days[2],ll(days[3],ll(days[4],ll(days[5],ll(days[6])))))))
        ptr = daysll
        while ptr.next:
            ptr=ptr.next
        else:
            ptr.next = daysll
        ptrdays = daysll
        day_obj_list={}
        ptr = daysll
        for i in days+['sun']:
            day_obj_list[ptr.val] = ptr
            ptr=ptr.next    
        schedule=dict()
        subjects=set()
        for i in range(7):
            schedule[days[i]] = []
            for ind in range(12):
                if data.values[i][ind] == "" : continue
                data.values[i][ind] = str.upper(data.values[i][ind])
                subjects.add(data.values[i][ind])
        for i in range(7):
            for ind in range(12):
                if data.values[i][ind] == "" : continue
                schedule[days[i]].append(list(subjects).index(data.values[i][ind])+1)

        subjects={i+1 : list(subjects)[i] for i in range(len(subjects))}


        dates = data.values[7]
        start , end = [[datetime.strptime(dates[0], "%Y-%m-%d").strftime("%A").lower()[:3],int(dates[0][8:]),int(dates[0][5:7]) ], [int(dates[1][8:] ),int(dates[1][5:7])] ]
        special_days = data.values[8:]
        idays, absdays , hdays = [],[],[]
        for i in special_days:
            if i[0] == "Instructional" and("" not in i ) and "--Order--" not in i :idays.append([int(i[1][8:]),int(i[1][5:7]),i[2][:3].lower()])
            if i[0] == "Absent" and("" not in i ): absdays.append([int(i[1][8:]),int(i[1][5:7])])
            if i[0] == "Holiday"and( "" not in i) : hdays.append([int(i[1][8:]),int(i[1][5:7])])

        
        def next_date_day (dayptr, d , m):
            l = months[m]
            dayptr = dayptr.next
            if d < l :
                return [dayptr,d+1,m]
            elif d == l :
                return [dayptr , 1 , m+1]
            else:
                return ll('wrong_key'),'wrongkey','wrong key'
            

        #we are making data for all dates in form [day , date , month] # MUTABLE
        daylist = []
        ptr = day_obj_list[start[0]]
        curr = [ptr]+start[1:]
        while True :
            app = [curr[0].val,curr[1],curr[2]]
            if curr[1:] == end :
                daylist.append(app)
                break
            elif curr[0] == None :
                break
            daylist.append(app)
            curr = next_date_day(ptr,curr[1],curr[2])
            ptr=ptr.next

        for k in hdays :
            for i in range(len(daylist)):
                ob = daylist[i]
                if ob[1:] == k :
                    daylist[i][0] = 'holi'
        
        for i in idays:
            d1,m1,da=i
            for i in range(len(daylist)):
                ob = daylist[i]
                if ob[1:] == [d1,m1]:
                    daylist[i][0] = da


        daycount = {
            i:sum([1 if j[0] == i else 0 for j in daylist ]) for i in days
        }

        totalsubclass = {
            subjects[i] :sum([daycount[j]*schedule[j].count(i) for j in schedule])  for i in subjects
        }

        tt = totalsubclass

        daycount = {
            i:sum([1 if (j[0] == i and j[1:] not in absdays) else 0 for j in daylist ]) for i in days
        }

        totalsubclass = {
            subjects[i] :sum([daycount[j]*schedule[j].count(i) for j in schedule])  for i in subjects
        }

        abtt = totalsubclass
        result = dict()
        debbared = False
        for i in tt:
            if tt[i] ==0 : 
                result[i] = 100
                continue
            result[i] = round((abtt[i]/tt[i])*100,2)
            if result[i] < 75.00  : debbared=True
        result = { k : i for k,i in zip(result.keys(),zip(result.values() , tt.values() , abtt.values()))}
        print(daylist,hdays,idays,absdays,schedule)
        return JSONResponse({"status":"success" , "result":result , "isdebar":debbared})
    except Exception as e:
        print(type(e).__name__)
        print(e.__traceback__.tb_lineno)
        print(dates if dates else "\n" , subjects if subjects else "\n" , schedule if schedule else "\n")
        
        if tt :
            print(tt)
        if abtt:
            print(abtt)
        print("returning=> " ,JSONResponse({"status":"failed"}))
        return JSONResponse({"status":"failed"})
    

if __name__ =="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=55333, reload=True)