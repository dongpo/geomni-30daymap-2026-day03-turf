"""Create a bus-only Taipei/New Taipei subset. Keep TRTC feed separate to avoid duplicates."""
import csv,io,json,zipfile,collections,sys
from pathlib import Path
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
z=zipfile.ZipFile(src)
def rows(n):return csv.DictReader(io.TextIOWrapper(z.open(n),encoding='utf-8-sig'))
routes=[r for r in rows('routes.txt') if r['route_type']=='3' and r['route_id'].startswith(('TPE','NWT'))]
rids={r['route_id'] for r in routes};agencies={r['agency_id'] for r in routes}
trips=[r for r in rows('trips.txt') if r['route_id'] in rids];tids={r['trip_id'] for r in trips};services={r['service_id'] for r in trips}
shapes={r.get('shape_id') for r in trips}-{None,''}
report={'scope':'TPE and NWT bus routes only; TRTC loaded separately','source_file':src.name,'counts':{},'omitted_tables':'fares and translations; not used for travel-time calculation','checks':{}}
stops=set();missing_times=0;bad_times=0;last={};times_count=0
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dest:
 def write(n,rs):
  rs=iter(rs)
  try:first=next(rs)
  except StopIteration:return
  with dest.open(n,'w') as f:
   w=io.TextIOWrapper(f,encoding='utf-8',newline='');c=csv.DictWriter(w,fieldnames=list(first));c.writeheader();c.writerow(first);count=1
   for r in rs:c.writerow(r);count+=1
   w.flush()
  report['counts'][n]=count
 write('routes.txt',routes);write('trips.txt',trips);write('agency.txt',(r for r in rows('agency.txt') if r['agency_id'] in agencies))
 def stop_times():
  global bad_times,times_count,missing_times
  for r in rows('stop_times.txt'):
   if r['trip_id'] not in tids:continue
   stops.add(r['stop_id']);times_count+=1
   try:
    def sec(s):h,m,s=map(int,s.split(':'));return h*3600+m*60+s
    a=sec(r['arrival_time']);d=sec(r['departure_time']);seq=int(r['stop_sequence'])
    if d<a:bad_times+=1
   except (ValueError,TypeError):
    if not r['arrival_time'] or not r['departure_time']:missing_times+=1
    else:bad_times+=1
   yield r
 write('stop_times.txt',stop_times())
 allstops=list(rows('stops.txt'));lookup={r['stop_id']:r for r in allstops}
 parents={lookup[s].get('parent_station','') for s in stops if s in lookup};stops|=parents-{''}
 write('stops.txt',(r for r in allstops if r['stop_id'] in stops))
 write('shapes.txt',(r for r in rows('shapes.txt') if r['shape_id'] in shapes))
 cal=[r for r in rows('calendar.txt') if r['service_id'] in services]
 write('calendar.txt',cal);write('calendar_dates.txt',(r for r in rows('calendar_dates.txt') if r['service_id'] in services))
 freq=[r for r in rows('frequencies.txt') if r['trip_id'] in tids];write('frequencies.txt',freq)
 report['calendar_start']=min(r['start_date'] for r in cal);report['calendar_end']=max(r['end_date'] for r in cal)
 report['calendar_date_ranges']=dict(collections.Counter(r['start_date']+'..'+r['end_date'] for r in cal))
 report['headway_seconds_distribution']=dict(collections.Counter(r['headway_secs'] for r in freq))
 report['checks']={'duplicate_route_ids':len(routes)-len(rids),'duplicate_trip_ids':len(trips)-len(tids),'unresolved_stop_ids':len(stops-set(lookup)),'invalid_time_fields':bad_times,'missing_intermediate_time_rows':missing_times}
report['output_bytes']=out.stat().st_size
(out.parent/'bus-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
