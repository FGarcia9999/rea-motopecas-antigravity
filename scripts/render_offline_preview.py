"""Capturas VISUAIS offline: API simulada, não substituem testes end-to-end reais. Requer playwright + chromium."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from app.catalog import BIKES,PRODUCTS
from playwright.sync_api import sync_playwright
import json,base64

h=(root/'static/index.html').read_text()
css=(root/'static/styles.css').read_text()
js=(root/'static/app.js').read_text()
img_base=lambda f:'data:image/svg+xml;base64,'+base64.b64encode((root/'static/img'/f).read_bytes()).decode()
icons={p.stem:img_base(p.name) for p in (root/'static/img').glob('*.svg')}
h=h.replace('<link rel="stylesheet" href="/static/styles.css" />','<style>'+css+'</style>')
h=h.replace('<script defer src="/static/app.js"></script>','')
h=h.replace('/static/img/moto.svg',icons['moto'])
js=js.replace("const img = (p) => `/static/img/${imgTypes.has(p.image)?p.image:'filtro'}.svg`;",'const img = (p) => IMG_MAP[p.image] || IMG_MAP.filtro;')
products=[dict(id=i+1,sku=p[0],name=p[1],category=p[2],image=p[3],price_cents=p[4],stock=p[5],description=p[6],bikes=p[7]) for i,p in enumerate(PRODUCTS)]
payload={'/api/bikes':BIKES,'/api/categories':sorted(set(p['category'] for p in products))}
mock='const IMG_MAP = '+json.dumps({k:v for k,v in icons.items() if k not in ('moto','favicon')})+';\n'
mock+='const DEMO_PRODUCTS = '+json.dumps(products,ensure_ascii=False)+';\n'
mock+='const DEMO_DATA = '+json.dumps(payload,ensure_ascii=False)+';\n'
mock+='''window.fetch=async (url,opts={})=>{
 const u=new URL(url,'https://rota2.local'); let data=DEMO_DATA[u.pathname];
 if(u.pathname==='/api/products'){
  const q=(u.searchParams.get('q')||'').toLowerCase(); const c=u.searchParams.get('category')||'';
  const b=u.searchParams.get('bike')||''; const y=u.searchParams.get('year')||'';
  data=DEMO_PRODUCTS.filter(p => (!q || p.name.toLowerCase().includes(q)) && (!c || p.category===c) && (!b || p.bikes.includes(b)));
 }
 if(u.pathname==='/api/orders') data={order_id:'DEMO-PREVIEW',status:'SIMULADO',total_cents:4590,payment_processed:false};
 return new Response(JSON.stringify(data??[]),{status:200,headers:{'Content-Type':'application/json'}});
};'''
Path('/tmp/moto_mock.js').write_text(mock)
Path('/tmp/moto_appjs.js').write_text(js)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
 for width,height,name in [(1440,900,'desktop-preview.png'),(390,844,'mobile-preview.png')]:
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  errs=[]
  page.on('pageerror',lambda exc:errs.append(str(exc)))
  page.set_content(h,wait_until='load',timeout=30000)
  page.add_script_tag(content=mock)
  page.add_script_tag(content=js)
  page.evaluate('main()')
  page.wait_for_timeout(800)
  cards=page.locator('.product-card').count()
  print(name,'cards',cards,'overflow',page.evaluate('document.documentElement.scrollWidth>innerWidth'),'errors',errs)
  page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
  page.wait_for_timeout(350)
  page.evaluate("document.documentElement.style.scrollBehavior='auto';window.scrollTo({top:0,behavior:'instant'})")
  page.wait_for_timeout(250)
  # Congela o header relativo somente para a captura full-page offline.
  page.evaluate("document.querySelector('.site-header').style.position='relative'")
  page.screenshot(path=str(root/'docs/evidence'/name),full_page=True)
  if name.startswith('desktop') and cards:
   page.get_by_role('button',name='Adicionar Pastilha de freio dianteira ao carrinho').click()
   page.get_by_role('button',name='Abrir carrinho').click()
   print('UI cart',page.locator('#cart-subtotal').inner_text())
  page.close()
 b.close()
