


from _util.util_v1 import * ; import _util.util_v1 as uutil
from _util.pytorch_v1 import * ; import _util.pytorch_v1 as utorch
from _util.twodee_v1 import * ; import _util.twodee_v1 as u2d

import bs4

DEBUG = False


rdn = '/dev/shm' if DEBUG else './_data/lustrous/raw/fandom'
fn_meta = f'{rdn}/genshin-impact/metadata.json'
dn_images = mkdir(f'{rdn}/genshin-impact/images')

url_base = 'https://genshin-impact.fandom.com'


######## save metadata ########

resp = requests.get(f'{url_base}/wiki/Character/List')
soup = bs4.BeautifulSoup(resp.content)
tabs = soup.select('table.article-table.sortable')
charpgs = []

# programatically add characters
seen = set()
for tab in tabs:
    for row in tab.find_all('tr'):
        td = row.find('td')
        if not td: continue
        a = td.find('a')
        if not a: continue
        if a['href'] in seen:
            continue
        img = a.find('img')
        charpgs.append({
            'agency': 'genshin',
            'name': a['href'].split('/')[-1],
            'url_page': f'{url_base}{a["href"]}',
            'portrait': {
                k: img[k if not img[k].startswith('data:') else 'data-src']
                for k in ['alt', 'data-image-key', 'data-image-name', 'src']
            },
        })
        seen.add(a['href'])

# save metadata
uutil.jwrite(charpgs, mkfile(fn_meta))


######## download images ########

metas = uutil.jread(fn_meta)
ext_allowed = {
    'jpg',
    'png',
    'jpeg',
    'gif',
    'webp',
}
def _get_image_url(c):
    if 'src' not in c: return None
    if '/revision' not in c['src']: return None
    url = c['src'].split('/revision')[0]
    ext = fnstrip(url,1).ext.lower()
    if ext not in ext_allowed: return None
    return Dict(url=url, ext=ext)
for meta in tqdm(metas if not DEBUG else metas[:8]):
    franch = meta['agency']
    name = meta['name']
    if franch.startswith('.'):
        franch = f'dot{franch[1:]}'  # fuck this man
    opn = f'{dn_images}/{franch}/{name}'
    
    # download portrait
    if 'portrait' in meta:
        m = meta['portrait']
        iurl = _get_image_url(m)
        if iurl==None: continue
        ofn = f'{opn}/0000.{iurl.ext}'
        if os.path.isfile(ofn): continue
        try:
            urllib.request.urlretrieve(iurl.url, mkfile(ofn))
        except Exception as e:
            tbs = traceback.format_exc()
            write(f'{isonow()}\n{tbs}', mkfile(f'{ofn}.txt'))


######## transform + segment images ########

bns = [
    f'daredemoE/fandom_align/{bn}/front'
    for bn in uutil.read_bns('./_data/lustrous/subsets/daredemoE_test.csv')
    if 'genshin' in bn
]
aligndata = pload('./_data/lustrous/renders/daredemoE/fandom_align_alignment.pkl')
def _apply_M(img, M, size=512):
    return I(kornia.geometry.transform.warp_affine(
        img.convert('RGBA').bg('w').convert('RGB').t()[None],
        torch.tensor(M).float()[[1,0,2]].T[[1,0,2]].T[None,:2],
        (size,size),
        mode='bilinear',
        padding_mode='fill',
        align_corners=True,
        fill_value=torch.ones(3),
    )).alpha_set(I(kornia.geometry.transform.warp_affine(
        img['a'].t()[None],
        torch.tensor(M).float()[[1,0,2]].T[[1,0,2]].T[None,:2],
        (size,size),
        mode='bilinear',
        padding_mode='fill',
        align_corners=True,
        fill_value=torch.zeros(3),
    ))['r'])
for bn in bns:
    try:
        a = aligndata[bn]
        fan,franch,idx,view = a['source'].split('/')
        img_src = I(f'{rdn}/{fan}/images/{franch}/{idx}/{view}.png')
        img_seg = I(f'./_data/lustrous/renders/{bn.replace("fandom_align","fandom_align_seg")}.png')
        out = _apply_M(img_src, a['transformation']).alpha_set(img_seg)
        if DEBUG:
            out.save(mkfile(f'/dev/shm/renders/{bn}.png'))
        else:
            out.save(mkfile(f'./_data/lustrous/renders/{bn}.png'))
    except:
        print(f'skipped: {bn}')






