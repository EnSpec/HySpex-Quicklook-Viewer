import numpy as np
import os
from matplotlib import pyplot as plt
import scipy.misc 

#adapted from https://github.com/StrawsonDesign/hyspex_viewer/
def bands_from_hyspex(fname,bands):
    
    hyspex_f = open(fname,"rb")
    header = hyspex_f.read(8)
    assert header == b'HYSPEX\x00\x00'
    head_size = np.fromstring(hyspex_f.read(4),'int32')[0]
    
    hyspex_f.seek(1949,os.SEEK_CUR)
    #number of channels and pixels
    spectral,spatial = np.fromstring(hyspex_f.read(8),'int32')
    hyspex_f.seek(4*26,os.SEEK_CUR)
    #number of lines in image
    number = np.fromstring(hyspex_f.read(4),'int32')[0]
    hyspex_f.seek(head_size,os.SEEK_SET)

    if isinstance(bands,list):
        out_arr = np.empty([spatial,number,len(bands)],dtype='uint16')
        #number of pixels we must step through to get from one channel to the next
        final_step = spectral-bands[-1]
        curr_pos = head_size
        for i in range(number):
            #mmap the whole row
            mapped = np.memmap(hyspex_f,'r',)
        '''
        for i in range(number):
            if(i%100==0):print("Reading line %d At positions"%i,end=' ')
            for b,step in enumerate(band_cycle):
                pos = hyspex_f.seek(2*(step)*spatial,os.SEEK_CUR)
                if(i%100==0):print(pos,end=', ')
                out_arr[:,i,b] = np.fromstring(hyspex_f.read(spatial*2),dtype='uint16');    
            if(i%100==0):print()    
            hyspex_f.seek(2*(final_step)*spatial,os.SEEK_CUR)
        '''
    else:
        out_arr = np.zeros([spatial,number],dtype='uint16')
        print(number)
        for i in range(number):
            if(i%100==0):print("Reading line %d"%i,end=' ')
            if i==0:
               pos= hyspex_f.seek(2*spatial*(bands-1),os.SEEK_CUR)
               print("At position %d"%pos)
            else:
                pos = hyspex_f.seek(2*(spectral-1)*spatial,os.SEEK_CUR)
                if(i%100==0):print("At position %d"%pos)
            out_arr[:,i] = np.fromstring(hyspex_f.read(spatial*2),dtype='uint16');    
    hyspex_f.close()
    return out_arr


    


if __name__=='__main__':
    import sys
    bands = bands_from_hyspex(sys.argv[1],[19,46,75])
    #bands = bands_from_hyspex(sys.argv[1],75)
    #bands = bands.astype('float32')/np.max(bands)
    print(bands.shape)
    bands=bands.astype('float32')
    max_color = (np.median(bands))+2*np.std(bands)
    bands[bands>max_color]=max_color
    #it looks a bit yellow
    bands[:,:,2]*=.9
    bands[:,:,1]*=.9
    bands[:,:,0]*=1.1
    scipy.misc.toimage(bands[:,:,[2,1,0]]).save('bands.png')

