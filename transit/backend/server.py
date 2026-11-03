"""Local service: no credentials or raw GTFS are served to the browser."""
from pathlib import Path
import datetime,threading,time,json,uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from engine import Engine
ROOT=Path(__file__).resolve().parents[1];app=FastAPI();state={'status':'building','message':'正在載入路網與班表'};engine=None
pool=ThreadPoolExecutor(max_workers=1);jobs={};cache={};guard=threading.Lock()
def initialize():
 global engine
 try:engine=Engine();state.update(status='ready',message='路網與班表已就緒',destinations=len(engine.destinations))
 except Exception as e:state.update(status='error',message='路網載入失敗，請查看伺服器紀錄');print(type(e).__name__,str(e),flush=True)
@app.on_event('startup')
def startup():pool.submit(initialize)
@app.get('/api/status')
def status():return {**state,'date_min':'2026-11-03','date_max':'2026-12-03','grid_m':300,'scope':'台北市起點；雙北市區公車＋台北捷運＋步行；不含臺鐵、高鐵、機場捷運及環狀線'}
class Query(BaseModel):
 lon:float=Field(ge=121,le=122)
 lat:float=Field(ge=24,le=26)
 departure:datetime.datetime
 walk_kmh:float=Field(default=4.8,ge=3,le=6)
 max_rides:int=Field(default=3,ge=1,le=4)
def execute(key,job,q):
 try:
  r=engine.compute(q.lon,q.lat,q.departure,q.walk_kmh,q.max_rides)
  with guard:
   cache[key]=r
   if len(cache)>32:cache.pop(next(iter(cache)))
   jobs[job]={'status':'complete','result':r}
 except ValueError as e:jobs[job]={'status':'error','message':str(e)}
 except Exception as e:jobs[job]={'status':'error','message':'計算失敗；請調整位置或稍後再試。'};print(type(e).__name__,str(e),flush=True)
@app.post('/api/isochrone')
def query(q:Query):
 if state['status']!='ready':raise HTTPException(503,state['message'])
 if q.departure.tzinfo is not None:raise HTTPException(422,'請使用台灣當地時間，不附時區。')
 if not datetime.date(2026,11,3)<=q.departure.date()<=datetime.date(2026,12,3):raise HTTPException(422,'查詢日期超出公車班表有效期間。')
 if q.departure.hour<5:raise HTTPException(422,'本版暫不支援凌晨跨服務日查詢；請選擇 05:00–23:59。')
 key=q.model_dump_json()
 with guard:
  if key in cache:return {'status':'complete','result':cache[key],'cached':True}
  if any(j['status']=='running' for j in jobs.values()):raise HTTPException(429,'已有查詢計算中，請稍候。')
  job=uuid.uuid4().hex;jobs[job]={'status':'running'}
  if len(jobs)>64:
   for old in list(jobs)[:-32]:jobs.pop(old,None)
 pool.submit(execute,key,job,q);return {'status':'running','job_id':job}
@app.get('/api/jobs/{job}')
def get_job(job:str):
 if job not in jobs:raise HTTPException(404,'查詢已過期')
 return jobs[job]
app.mount('/',StaticFiles(directory=ROOT/'web',html=True),name='web')
if __name__=='__main__':
 import uvicorn
 uvicorn.run(app,host='127.0.0.1',port=8773)
