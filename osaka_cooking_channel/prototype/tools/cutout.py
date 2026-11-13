import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src='/home/user/Sunplaza-supermarket/osaka_cooking_channel/assets/catherine_george_reference.png'
im=np.asarray(Image.open(src).convert('RGB')).astype(float)
H,W,_=im.shape
edge=np.concatenate([im[:,:15],im[:,-15:]],axis=1)
bgrow=np.median(edge,axis=1)
d=np.sqrt(((im-bgrow[:,None,:])**2).sum(-1))
def fgmask(th):
    lab,n=ndimage.label(d<th)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    return ~np.isin(lab,list(border))
loose=fgmask(22); strict=fgmask(11)
box=np.zeros_like(loose); box[540:900,540:860]=True
fg=loose|(strict&box)
fg=ndimage.binary_opening(fg,iterations=2)
fg=ndimage.binary_fill_holes(fg)
lab2,n2=ndimage.label(fg); sizes=ndimage.sum(fg,lab2,range(1,n2+1))
fg=np.isin(lab2,[i+1 for i,s in enumerate(sizes) if s>20000])
alpha=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))
rgba=Image.open(src).convert('RGBA'); rgba.putalpha(alpha)
rgba.save('both.png')
