"""R5 schedule-based one-to-many routing; cells are an explicit approximation."""
import datetime,json,time,os
from pathlib import Path
import geopandas as gpd
import numpy as np
from shapely.geometry import Point,box,mapping,shape
from shapely.ops import unary_union
import r5py
DATA=Path(os.environ.get('GEOMNI_TRANSIT_DATA','work/transit')).resolve()
WEB=Path(__file__).resolve().parents[1]/'web'
GRID=300
BOUNDS=(121.35,24.90,121.75,25.25)
class Engine:
 def __init__(self):
  self.network=r5py.TransportNetwork(DATA/'taipei.osm.pbf',[DATA/'taipei-bus.gtfs.zip',DATA/'trtc.gtfs.zip'])
  self.boundary=shape(json.loads((WEB/'taipei-boundary.geojson').read_text())['features'][0]['geometry'])
  area=gpd.GeoSeries([box(*BOUNDS)],crs=4326).to_crs(3826).total_bounds
  pts=[Point(x,y) for x in np.arange(area[0],area[2],GRID) for y in np.arange(area[1],area[3],GRID)]
  grid=gpd.GeoDataFrame({'id':np.arange(len(pts)).astype(str),'geometry':pts},crs=3826)
  grid['cell']=grid.geometry.map(lambda p:box(p.x-GRID/2,p.y-GRID/2,p.x+GRID/2,p.y+GRID/2))
  self.cells=dict(zip(grid.id,grid.cell));dest=grid.drop(columns='cell').to_crs(4326)
  snapped=self.network.snap_to_network(dest.geometry,radius=150)
  dest=dest.loc[~snapped.is_empty & snapped.notna()].copy()
  self.destinations=dest;self.last_evidence=None
 def compute(self,lon,lat,departure,walking=4.8,rides=3):
  point=Point(lon,lat)
  if not self.boundary.covers(point):raise ValueError('請選擇台北市界內的位置。')
  if not datetime.date(2026,11,3)<=departure.date()<=datetime.date(2026,12,3):raise ValueError('目前班表可查日期為 2026-11-03 至 2026-12-03。')
  origin=gpd.GeoDataFrame({'id':['origin'],'geometry':[point]},crs=4326)
  snapped=self.network.snap_to_network(origin.geometry,radius=150)
  if snapped.is_empty.any() or snapped.isna().any():raise ValueError('此位置 150 公尺內沒有可連接的步行路網，請改選道路或站點附近。')
  t=time.monotonic()
  result=r5py.TravelTimeMatrix(self.network,origins=origin,destinations=self.destinations,departure=departure,departure_time_window=datetime.timedelta(minutes=5),percentiles=[50],transport_modes=[r5py.TransportMode.TRANSIT,r5py.TransportMode.WALK],access_modes=[r5py.TransportMode.WALK],egress_modes=[r5py.TransportMode.WALK],max_time=datetime.timedelta(minutes=60),max_time_walking=datetime.timedelta(minutes=20),speed_walking=walking,max_public_transport_rides=rides)
  features=[]; counts={}
  for cutoff in [15,30,45,60]:
   ids=result.loc[result.travel_time.notna() & (result.travel_time<=cutoff),'to_id'].astype(str).tolist();counts[str(cutoff)]=len(ids)
   if not ids:continue
   geom=unary_union([self.cells[i] for i in ids]);area=geom.area/1e6
   geom=gpd.GeoSeries([geom],crs=3826).to_crs(4326).iloc[0]
   features.append({'type':'Feature','properties':{'minutes':cutoff,'cells':len(ids),'grid_area_km2':round(area,3)},'geometry':mapping(geom)})
  meta={'origin':[lon,lat],'departure':departure.isoformat(),'timezone':'Asia/Taipei','window_minutes':5,'percentile':50,'walk_kmh':walking,'max_public_transport_rides':rides,'walking_limit_minutes':20,'grid_m':GRID,'destination_bounds':BOUNDS,'destinations':len(self.destinations),'reachable_cells':counts,'compute_seconds':round(time.monotonic()-t,2),'feeds':['TDX Taipei/New Taipei bus subset','TRTC 20260906'],'bus_intermediate_times':'missing values interpolated by R5','source_dates':['2026-11-03','2026-12-03'],'live_traffic':False}
  self.last_evidence=result
  return {'type':'FeatureCollection','features':features,'metadata':meta}
