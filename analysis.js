/* Real browser-side operations; input geometries remain the original 2017 dataset. */
const params=new URLSearchParams(location.search);if(params.has('export'))document.body.classList.add('export');
let center=[121.5170,25.0478];let radius=Number(params.get('radius'))||20;let revision=0;
window.analysisErrors=[];
const map=new maplibregl.Map({container:'map',style:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#0c1c2b'}}]},center:[121.52,25.04],zoom:9.45,preserveDrawingBuffer:true,attributionControl:false});
window.map=map;
map.addControl(new maplibregl.AttributionControl({compact:false,customAttribution:'© OpenStreetMap contributors · geoBoundaries (2017)'}));
map.addControl(new maplibregl.ScaleControl({maxWidth:100,unit:'metric'}),'bottom-left');
map.on('error',e=>{window.analysisErrors.push(String(e.error));});
function calculate(){
 const start=performance.now();const buffer=turf.buffer(turf.point(center),radius,{units:'kilometers',steps:128});
 const pieces=[];const areas=[];
 for(const f of COUNTIES.features){
  if(!turf.booleanIntersects(f,buffer))continue;
  const piece=turf.intersect(turf.featureCollection([f,buffer]));
  if(piece){const km2=turf.area(piece)/1e6;piece.properties={name:f.properties.name_zh,shapeName:f.properties.shapeName,area_km2:km2};pieces.push(piece);areas.push({name:f.properties.name_zh,area_km2:km2});}
 }
 areas.sort((a,b)=>b.area_km2-a.area_km2);
 const elapsed=performance.now()-start;
 window.analysisResult={schema_version:1,revision:++revision,center:[...center],radius_km:radius,buffer_area_km2:turf.area(buffer)/1e6,intersection_area_km2:areas.reduce((s,a)=>s+a.area_km2,0),county_count:areas.length,areas,calculation_ms:elapsed,buffer,intersections:turf.featureCollection(pieces),input_count:COUNTIES.features.length,turf_version:'7.4.0',maplibre_version:'5.24.0',source_year:2017};
 return window.analysisResult;
}
function update(){
 const r=calculate();map.getSource('buffer').setData(r.buffer);map.getSource('pieces').setData(r.intersections);map.getSource('center').setData(turf.point(center));
 document.getElementById('radiusLabel').textContent=radius+' km';document.getElementById('radius').value=radius;
 document.getElementById('summary').textContent=`${radius} km 緩衝區 · 與 ${r.county_count} 個行政區相交`;
 const stats=document.getElementById('stats');stats.replaceChildren();
 for(const row of r.areas){const d=document.createElement('div');d.className='stat';d.textContent=row.name;const small=document.createElement('small');small.textContent=row.area_km2.toFixed(1)+' km²';d.append(small);stats.append(d)}
 document.getElementById('evidence-json').textContent=JSON.stringify(r,null,2);
 window.analysisReady=true;
}
map.on('load',()=>{
 map.addSource('counties',{type:'geojson',data:COUNTIES});map.addLayer({id:'county-fill',type:'fill',source:'counties',paint:{'fill-color':'#344b62','fill-opacity':0.6}});
 map.addSource('pieces',{type:'geojson',data:turf.featureCollection([])});map.addLayer({id:'pieces-fill',type:'fill',source:'pieces',paint:{'fill-color':'#60d4c4','fill-opacity':0.65}});
 map.addLayer({id:'county-lines',type:'line',source:'counties',paint:{'line-color':'#abc1c8','line-width':1.1}});
 map.addSource('buffer',{type:'geojson',data:turf.featureCollection([])});map.addLayer({id:'buffer-line',type:'line',source:'buffer',paint:{'line-color':'#ffbf69','line-width':2,'line-dasharray':[3,2]}});
 map.addSource('center',{type:'geojson',data:turf.point(center)});map.addLayer({id:'center-dot',type:'circle',source:'center',paint:{'circle-radius':5,'circle-color':'#ffbf69','circle-stroke-color':'#0c1c2b','circle-stroke-width':2}});
 for(const [name,xy] of [['台北市',[121.545,25.09]],['新北市',[121.59,24.95]],['桃園市',[121.29,24.98]],['基隆市',[121.73,25.13]]]){const el=document.createElement('div');el.className='map-label';el.textContent=name;new maplibregl.Marker({element:el}).setLngLat(xy).addTo(map)}
 map.on('click',e=>{if(params.has('export'))return;center=[e.lngLat.lng,e.lngLat.lat];update()});
 const popup=new maplibregl.Popup({closeButton:false,closeOnClick:false});
 map.on('mousemove','pieces-fill',e=>{if(!e.features.length)return;const p=e.features[0].properties;const el=document.createElement('div');el.textContent=p.name+'：'+Number(p.area_km2).toFixed(2)+' km²';popup.setLngLat(e.lngLat).setDOMContent(el).addTo(map)});map.on('mouseleave','pieces-fill',()=>popup.remove());
 update();map.fitBounds(turf.bbox(window.analysisResult.buffer),{padding:24,duration:0});map.once('idle',()=>window.mapRendered=true);
});
document.getElementById('radius').addEventListener('input',e=>{radius=Number(e.target.value);update()});
document.getElementById('reset').onclick=()=>{center=[121.5170,25.0478];radius=20;document.getElementById('radius').value=20;map.jumpTo({center:[121.52,25.04],zoom:9.45});update()};
document.getElementById('download').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(window.analysisResult,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='geomni-turf-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
