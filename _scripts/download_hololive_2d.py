


from _util.util_v1 import * ; import _util.util_v1 as uutil
from _util.pytorch_v1 import * ; import _util.pytorch_v1 as utorch
from _util.twodee_v1 import * ; import _util.twodee_v1 as u2d


DEBUG = False

rdn = '/dev/shm' if DEBUG else './_data/lustrous/raw/fandom'
fn_meta = f'{rdn}/virtualyoutuber/metadata.json'
dn_images = mkdir(f'{rdn}/virtualyoutuber/images')

url_base = 'https://virtualyoutuber.fandom.com'


######## load metadata ########

bns = [
    f'daredemoE/fandom_align/{bn}/front'
    for bn in uutil.read_bns('./_data/lustrous/subsets/daredemoE_test.csv')
    if 'hololive' in bn
]
aligndata = pload('./_data/lustrous/renders/daredemoE/fandom_align_alignment.pkl')
metas = jread(fn_meta)
asrc2url = {}
for meta in metas:
    franch = meta['agency']
    name = meta['name']
    if franch.startswith('.'):
        franch = f'dot{franch[1:]}'  # fuck this man
    if 'portrait' in meta:
        asrc2url[f'virtualyoutuber/{franch}/{name}/0000'] = meta['portrait']
    if 'gallery_items' in meta:
        for i,item in enumerate(meta['gallery_items']):
            asrc2url[f'virtualyoutuber/{franch}/{name}/{i+1:04d}'] = item


######## download images ########

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
for bn in bns:
    try:
        a = aligndata[bn]
        asrc = a['source']
        m = asrc2url[a['source']]
        _,franch,name,idx = asrc.split('/')
        idx = int(idx)
        opn = f'{dn_images}/{franch}/{name}'

        if idx==0:
            # download portrait
            iurl = _get_image_url(m)
            if iurl==None: continue
            ofn = f'{opn}/0000.{iurl.ext}'
            if os.path.isfile(ofn): continue
            try:
                urllib.request.urlretrieve(iurl.url, mkfile(ofn))
            except Exception as e:
                tbs = traceback.format_exc()
                write(f'{isonow()}\n{tbs}', mkfile(f'{ofn}.txt'))
        else:
            # download from gallery
            iurl = _get_image_url(m)
            if iurl==None: continue
            ofn = f'{opn}/{idx:04d}.{iurl.ext}'
            if os.path.isfile(ofn): continue
            try:
                urllib.request.urlretrieve(iurl.url, mkfile(ofn))
            except Exception as e:
                tbs = traceback.format_exc()
                write(f'{isonow()}\n{tbs}', mkfile(f'{ofn}.txt'))
        # break
    except:
        print(f'skipped: {bn}')


######## transform + segment images ########

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




