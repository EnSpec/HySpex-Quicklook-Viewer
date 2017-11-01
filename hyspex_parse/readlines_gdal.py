import gdal
import scipy.misc
import numpy as np
gdal.GetDriverByName('EHdr').Register()


def readBIL(fname,band_idxs):
    '''Read the RGB bands from a BIL file, yielding occasionally so
    the caller can guess at the progress
    '''
    img = gdal.Open(fname)
    bands = []
    for b in band_idxs:
        bands.append(img.GetRasterBand(b))
        print("got band {}".format(b))

    out_arrs=[]
    for b in bands:
        out_arrs.append(b.ReadAsArray())
        print("Array'd Band")
        yield None
    out = np.array(out_arrs)
    yield out

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
    print(rows,cols,bands)
    out = driver.Create(fname,cols,rows,bands,gdal.GDT_UInt16,
            options = ['PHOTOMETRIC=RGB','PROFILE=GeoTIFF',])
    for b in range(bands):
        out.GetRasterBand(b+1).WriteArray(processBand(rgb_arr[b,:,:],b))
        out.GetRasterBand(b+1).FlushCache()

if __name__ == '__main__':
    import sys
    data=(readBIL(sys.argv[1],[int(arg) for arg in sys.argv[2:]]))
    toGeoTiff("test.tiff",data)
