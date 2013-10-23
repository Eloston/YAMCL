'''
YAMCL is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

YAMCL is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with YAMCL.  If not, see {http://www.gnu.org/licenses/}.
'''

import json
import urllib.request
import os
import os.path
import configparser
import shutil

class internetinterface:
    def joinurl(self, urltype, iterpath):
        '''
        Returns full url based off of the type specified
        urltype is either download or resource
        '''
        if urltype == "download":
            selectedpath = ["https://s3.amazonaws.com/Minecraft.Download"]
        elif urltype == "resource":
            selectedpath = ["https://s3.amazonaws.com/Minecraft.Resources"]
        else:
            raise Exception("Invalid path type "+str(urltype))
        return '/'.join(selectedpath+list(iterpath))

    def geturlobject(self, urlpath):
        return urllib.request.urlopen(urlpath)

    def savefile(self, urlpath, filepath):
        with self.geturlobject(urlpath) as response, open(filepath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            out_file.close()

class filesysteminterface:
    def __init__(self):
        self.m_textencoding = 'UTF-8'

    def readmainconfig(self):
        '''
        Reads config.ini placed with the server manager script.
        Returns list of parameters containing config information
        '''
        currentscriptdiralias = "***CurrentScriptDirectory***"
        config = configparser.ConfigParser()
        config.read(self.getconfigpath())
        if len(config.sections()) == 1 and config.sections()[0] == "YAMCL":
            datapath = config["YAMCL"]["LauncherDataPath"]
            javapath = config["YAMCL"]["JavaPath"]
            defaultargs = config["YAMCL"]["DefaultJavaParams"]

            datapath = os.path.normpath(datapath) # Converts forward slashes to back slashes on Windows
            datapath = datapath.replace(currentscriptdiralias, currentscriptdir)
            datapath = os.path.abspath(datapath)

            javapath = os.path.normpath(javapath) # Converts forward slashes to back slashes on Windows
            javapath = javapath.replace(currentscriptdiralias, currentscriptdir)
            javapath = os.path.abspath(javapath)

            self.setdatapath(datapath)

            return [datapath, javapath, defaultargs]
        else:
            raise Exception("Invalid YAMCL configuration file")

    def getconfigpath(self):
        currentscriptdir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(currentscriptdir, 'config.ini')

    def setdatapath(self, datadirpath):
        if os.path.isfile(datadirpath):
            raise Exception(datadirpath+" is an existing file")
        self.m_datapath = datadirpath

    def getabsolutepath(self, iterpath):
        '''
        Returns a full path by joining the datapath with the parts of the new path in the iterable
        '''
        tmppath = self.m_datapath
        for pathitem in iterpath:
            tmppath = os.path.join(tmppath, pathitem)
        return tmppath

    '''
    def deletefile(self, iterpath):
        #Delete a file with a path relative to the YAMCL data directory
        #Will not work with directories
        os.remove(self.getabsolutepath(iterpath))

    def deleterecursively(self, iterpath):
        #Delete a directory recursively relative to the YAMCL data directory
        shutil.rmtree(self.getabsolutepath(iterpath))
    '''

    def initfilestructure(self):
        '''
        Initialize launcher and Minecraft data at specified path
        '''
        os.mkdir(self.getabsolutepath(list()))
        os.mkdir(self.getabsolutepath(["lib"]))
        tmpfile = open(self.getabsolutepath(["lib", "index.json"]), "w")
        tmpfile.write(str(list()))
        tmpfile.close()
        os.mkdir(self.getabsolutepath(["bin"]))
        tmpfile = open(self.getabsolutepath(["bin", "index.json"]), "w")
        tmpfile.write(str(list()))
        tmpfile.close()
        os.mkdir(self.getabsolutepath(["bin", "vanilla"]))
        os.mkdir(self.getabsolutepath(["bin", "custom"]))
        os.mkdir(self.getabsolutepath(["instances"]))

class jsontools:
    def __init__(self):
        self.m_textencoding = "UTF-8"

    def readjsondata(self, data):
        '''
        Decodes and returns JSON data
        '''
        return json.JSONDecoder().decode(data)

    def readjsonfile(self, path):
        '''
        Reads JSON file and returns JSON data
        '''
        jsonfileobj = open(path, encoding=self.m_textencoding)
        jsonfile = jsonfileobj.read()
        jsonfileobj.close()
        return self.readjsondata(jsonfile)

    def writejsonfile(self, data, path):
        '''
        Write JSON information data to JSON file
        '''
        jsonbytes = json.JSONEncoder(indent=2).encode(data).encode(self.m_textencoding)
        jsonfileobj = open(path, "wb")
        jsonfileobj.write(jsonbytes)
        jsonfileobj.close()

class libmanager:
    def readindex(self):
        '''
        Reads index.json for the libraries
        '''
        self.m_index = g_jsontools.readjsonfile(g_filesystem.getabsolutepath(["lib", "index.json"]))

    def getindex(self):
        return self.m_index

class binmanager:
    def readindex(self):
        '''
        Reads index.json for the binaries
        '''
        self.m_index = g_jsontools.readjsonfile(g_filesystem.getabsolutepath(["bin", "index.json"]))

    def getindex(self):
        return self.m_index

    def addindexentry(self, value):
        '''
        Add a dictionary to the index
        '''
        self.m_index.append(value)
        g_jsontools.writejsonfile(self.m_index, g_filesystem.getabsolutepath(["bin", "index.json"]))

    def removeindexentry(self, nameid):
        '''
        Remove a dictionary entry by ID
        '''
        foundmatch = False
        for entry in self.m_index:
            if entry['id'] == nameid:
                foundmatch = True
                self.m_index.remove(entry)
                g_jsontools.writejsonfile(self.m_index, g_filesystem.getabsolutepath(["bin", "index.json"]))
                break
        if not foundmatch:
            raise Exception("Specified ID does not refer to an existing Minecraft")

    def addvanillaversion(self, versionid):
        '''
        Downloads and adds a vanilla minecraft version from Mojang
        '''
        jsonurl = g_internet.joinurl("download", ["versions", versionid, versionid+".json"])
        jarurl = g_internet.joinurl("download", ["versions", versionid, versionid+".jar"])
        versiondir = g_filesystem.getabsolutepath(["bin", "vanilla", versionid])
        jsonpath = os.path.join(versiondir, versionid+".json")
        jarpath = os.path.join(versiondir, versionid+".jar")
        if os.path.exists(versiondir):
            raise Exception("Path "+versiondir+" already exists")
        else:
            os.mkdir(versiondir)
        g_internet.savefile(jsonurl, jsonpath)
        g_internet.savefile(jarurl, jarpath)
        jsonentry = dict()
        jsonentry['id'] = versionid
        jsonentry['baseversion'] = versionid
        jsonentry['type'] = "vanilla"
        jsonentry['params'] = '-Xmx512M'
        jsonentry['notes'] = ""
        self.addindexentry(jsonentry)

class instancemanager:
    pass

class versionjsonparser:
    def __init__(self):
        self.m_versionspath = g_filesystem.getabsolutepath(["bin", "versions.json"])

    def readcachedlist(self):
        '''
        Reads the version.json stored locally
        '''
        self.m_versionsjson = g_jsontools.readjsonfile(self.m_versionspath)

    def updatelist(self):
        '''
        Downloads and stores the latest versions.json file. Returns True if successful, otherwise returns False
        '''
        # TODO: Split try-except into multiple parts with different error codes
        jsonfile = g_internet.geturlobject(g_internet.joinurl("download", ["versions", "versions.json"])).read().decode("UTF-8")
        jsonfile = json.JSONDecoder().decode(jsonfile)
        print(type(jsonfile))
        g_jsontools.writejsonfile(jsonfile, self.m_versionspath)
        self.m_versionsjson = jsonfile
        return True

    def getlatest(self):
        '''
        Gets the latest versions of Minecraft according to the parsed file
        '''
        return self.m_versionsjson['latest']

    def getsnapshotlist(self):
        '''
        Gets a list of all snapshots available
        '''
        versionlist = list()
        for version in self.m_versionsjson['versions']:
            if version['type'] == 'snapshot':
                versionlist.append(version['id'])
        return versionlist

    def getreleaselist(self):
        '''
        Gets a list of all releases available
        '''
        versionlist = list()
        for version in self.m_versionsjson['versions']:
            if version['type'] == 'release':
                versionlist.append(version['id'])
        return versionlist

    def getbetalist(self):
        '''
        Gets a list of all beta versions avaiable
        '''
        versionlist = list()
        for version in self.m_versionsjson['versions']:
            if version['type'] == 'old_beta':
                versionlist.append(version['id'])
        return versionlist

    def getalphalist(self):
        '''
        Gets a list of all alpha versions avaiable
        '''
        versionlist = list()
        for version in self.m_versionsjson['versions']:
            if version['type'] == 'old_alpha':
                versionlist.append(version['id'])
        return versionlist

class main:
    def initializelauncher(self):
        pass

# The implemented launcher version is 8. TODO: Store this value and do checking in a class

g_filesystem = filesysteminterface()
g_internet = internetinterface()
g_jsontools = jsontools()
