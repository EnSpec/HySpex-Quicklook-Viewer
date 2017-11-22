import numpy as np
import gdal
import os

#adapted from https://github.com/StrawsonDesign/hyspex_viewer/
def readBIL(fname,bands,readmode='lines',update_arr = None,step=1):
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
    if update_arr:
        update_arr[1] = int(number/step)
    hyspex_f.seek(head_size,os.SEEK_SET)

    if isinstance(bands,list):
        out_arr = np.empty([len(bands),spatial//step,number//step],dtype='uint16')
        #number of pixels we must step through to get from one channel to the next
        final_step = spectral-bands[-1]
        curr_pos = head_size
        band_cycle = [bands[0]-1]+list(np.diff(bands)-1)
        if readmode == 'mmap':
            #mmap the whole file
            mmaped_data = np.memmap(hyspex_f,dtype='uint16',mode='r',offset=curr_pos)
            mmaped_data.shape = (number,spectral,spatial)
            #extract the appropriate bands
            for i in range(0,number,step):
                if(i/step>=out_arr.shape[2]):
                    break
                if(int(i/step)%100==0):
                    if update_arr:
                        update_arr[0]=int(i/step)
                        #check for poison pill
                        if update_arr[1]==-1:
                            raise RuntimeError("I've been poisoned!")
                for b,band in enumerate(bands):
                    out_arr[b,:,i//step]=mmaped_data[i,band-1,::step]
            return out_arr[::-1,:,:]

        for i in range(number):
            #or iteratively load the file into memory
            if readmode=='lines':
                #fread the chunk with the right bands - current winner
                hyspex_f.seek(2*(bands[0]-1)*spatial,os.SEEK_CUR)
                if(i%100==0):
                    if update_arr:
                        update_arr[0]=i
                    print("Reading line %d at position %d"%(i,hyspex_f.tell()))
                line = np.fromfile(hyspex_f,'uint16',(spatial)*(bands[-1]-bands[0]+1))
                for b,band in enumerate(bands):
                    out_arr[b,:,i] = line[(band-bands[0])*spatial:(band-bands[0]+1)*spatial]
                hyspex_f.seek(2*(final_step)*spatial,os.SEEK_CUR)

            elif readmode=='bands':
                #seek around the line to get the right bands
                for b,step in enumerate(band_cycle):
                    pos = hyspex_f.seek(2*(step)*spatial,os.SEEK_CUR)
                    if(i%100==0):print(pos,end=', ')
                    out_arr[b,:,i] = np.fromfile(hyspex_f,'uint16',spatial)
                if(i%100==0):print()    
                hyspex_f.seek(2*(final_step)*spatial,os.SEEK_CUR)
        hyspex_f.close()
        return out_arr[::-1,:,:]
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
            out_arr[:,i] = np.fromfile(hyspex_f,'uint16',spatial)    
        hyspex_f.close()
        return out_arr

def processBand(band,idx):
    #adjust band to appear as true-color as possible
    band = band.astype('float32')
    old_max = band.max()
    band *= [5.,5.,7.][idx]
    band[band>old_max] = old_max
    return band

def toGeoTiff(fname,rgb_arr):
    driver = gdal.GetDriverByName("GTiff")
    bands,rows,cols= rgb_arr.shape
    out = driver.Create(fname,cols,rows,bands,gdal.GDT_UInt16,
            options = ['PHOTOMETRIC=RGB','PROFILE=GeoTIFF',])
    for b in range(bands):
        out.GetRasterBand(b+1).WriteArray(processBand(rgb_arr[b,:,:],b))
        out.GetRasterBand(b+1).FlushCache()
    


if __name__=='__main__':
    import sys
    if sys.argv[2] == '1':
        bands = readBIL(sys.argv[1],[19,46,75],sys.argv[3])
        toGeoTiff("test.tiff",bands)
    else:
        bands = readBIL(sys.argv[1],75)

