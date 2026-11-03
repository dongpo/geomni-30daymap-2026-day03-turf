const $=id=>document.getElementById(id);let origin=[121.517,25.0478],boundary,lastResult,ready=false,mapReady=false,busy=false,revision=0;
const map=new maplibregl.Map({container:'map',style:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#0b1926'}}]},center:[121.53,25.06],zoom:10.7});
map.addControl(new maplibregl.NavigationControl());map.addControl(new maplibregl.ScaleControl({unit:'metric'}));map.addControl(new maplibregl.AttributionControl({customAttribution:'路網 © OpenStreetMap contributors / Overture Maps · 班表 TDX / TRTC · 市界 geoBoundaries 2017'}));
const marker=new maplibregl.Marker({color:'#ffffff'}).setLngLat(origin).addTo(map);
map.on('load',async()=>{try{boundary=await(await fetch('taipei-boundary.geojson')).json();map.addSource('boundary',{type:'geojson',data:boundary});map.addLayer({id:'boundary',type:'line',source:'boundary',paint:{'line-color':'#a3bac6','line-width':1.5,'line-dasharray':[4,3]}});map.addSource('result',{type:'geojson',data:{type:'FeatureCollection',features:[]}});map.addLayer({id:'result-fill',type:'fill',source:'result',paint:{'fill-color':['match',['get','minutes'],15,'#65d6c4',30,'#51a6da',45,'#a69be7','#e9b968'],'fill-opacity':.6}});map.addLayer({id:'result-outline',type:'line',source:'result',paint:{'line-color':['match',['get','minutes'],15,'#65d6c4',30,'#51a6da',45,'#a69be7','#e9b968'],'line-width':1}});const r=await fetch('roads.geojson.gz');if(!r.ok)throw Error('道路資料載入失敗');const data=await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).json();map.addSource('roads',{type:'geojson',data});mapReady=true;map.addLayer({id:'roads',type:'line',source:'roads',paint:{'line-color':'#44616f','line-width':.7}},'boundary');await showExample();}catch(e){$('status').textContent='地圖資料載入失敗：'+e.message}});

async function showExample(){
 $('example').disabled=true;$('download').disabled=true;$('status').textContent='正在載入已計算的情境…';
 try{
 const key=$('example').value;const r=await fetch('examples/'+key+'.geojson');if(!r.ok)throw Error('情境載入失敗，請重新選擇或重新整理。');
 const result=await r.json();result.features.sort((a,b)=>b.properties.minutes-a.properties.minutes);
 map.getSource('result').setData(result);lastResult=result;
 const m=result.metadata;marker.setLngLat(m.origin);
 $('status').textContent='已顯示預先運算結果';
 $('result').textContent=[$('example').selectedOptions[0].textContent,m.departure.replace('T',' ')+'（台灣）','步行 '+m.walk_kmh+' km/h · 最多搭乘 '+m.max_public_transport_rides+' 次','300 公尺格網中心可達數：',...[15,30,45,60].map(t=>t+' 分鐘：'+m.reachable_cells[t]+' 格')].join('\n');
 $('download').disabled=false;map.fitBounds(turf.bbox(result),{padding:35,maxZoom:13});
 }catch(e){$('status').textContent=e.message}finally{$('example').disabled=false}
}
$('example').onchange=showExample;
$('download').onclick=()=>{if(!lastResult)return;const u=URL.createObjectURL(new Blob([JSON.stringify(lastResult)],{type:'application/geo+json'}));const a=document.createElement('a');a.href=u;a.download=$('example').value+'.geojson';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
