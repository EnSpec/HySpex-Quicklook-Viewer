import sys
import os
import re
try:
    import win32api
except ImportError:
    print("Error: Expected Windows-based Filesystem")
    sys.exit(1)

DRIVE = "R:\\"
class FileNavigator(object):
    def __init__(self,drive):
        #get all accessible drive letters
        self._drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        if drive in self._drives:
            self._drive = drive
        else:
            self._drive = self._drives[0]

    def findLatest(self,matches='.*',path=None,max_depth=2):
        """Call recursive file finder and return result with latest mtime"""
        self.matching_files = [] 
        if path is None:
            path = self._drive
        self._find_latest(matches,path,max_depth,1)
        return min(self.matching_files,key=os.path.getmtime)

    def setDrive(self,drive):
        if drive in self._drives:
            self._drive = drive
        else:
            raise IOError("Unknown drive: {}".format(drive))

    def _find_latest(self,matches='.*',path=None,max_depth=2,curr_depth=1):
        """Recursively search for files in drive self._drive up to recursion 
        depth max_depth
        """
        files = []
        try:
            for f in os.listdir(path):
                full_path = os.path.join(path,f)
                os.path.getmtime(full_path)
                files.append(full_path)
        except PermissionError:
                pass
        #we need to look in all directories since we don't know if the latest 
        #matching file is in the latest updated path
        for f in files:
            if os.path.isdir(f) and curr_depth < max_depth:
                self._find_latest(matches,f,max_depth,curr_depth+1)
            else:
                if re.match(matches,f):
                    self.matching_files.append(f)
                





if __name__=='__main__':
    f = FileNavigator(DRIVE)
    print(f.findLatest('.*VNIR.*hyspex$'))
