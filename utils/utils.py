#SQL Helper Class
import os
import pymssql
from utils import config

class response:

    def __init__(self, otype, oid, withChildren):
        self.withChildren = withChildren
        self.type = otype
        self.oid = oid
        self.childType = config.getCnf().getChildType(self.type)
        self.childJoin = config.getCnf().getChildJoin(self.type)
        self.fields = config.getCnf().getFields(self.type)
        self.modifier = config.getCnf().getModifier(self.type)
        self.response = []

    def packChildren(self):
        if self.childType != "null":
            childObject = response(self.childType, "all", False)
            allChildren = childObject.generate()
            parentField = self.childJoin[0]
            childField = self.childJoin[1]
            targetChildren = []

            i = 0
            for p in self.response[self.type]:

                targetParent = self.response[self.type][i]
                targetChildren = []
                i += 1

                for c in allChildren[self.childType]:
                    
                    if c[childField] == targetParent[parentField]:
                        targetChildren.append(c)

                targetParent[self.childType] = (targetChildren)


    def pack(self):
        print("Packing " + self.type)
        queryString = config.getCnf().getQuery(self.type)
        results = getConn().runQuery(queryString)
        self.format(results)

    def format(self, results):
        for row in results:
            rdict = {}
            i = 0
            for f in self.fields:
                rdict[f] = row[i]
                if (f.lower() == "timestamp"):
                    #This is a timestamp.  Convert it to something.  ANYTHING
                    rdict[f] = self.toEpoch(row[i])
                i += 1
            self.response.append(rdict)

        if self.oid != "all":
            newResponse = []
            for r in self.response:
                if str(r[self.modifier]) == self.oid:
                    newResponse.append(r)
            self.response = { self.type : newResponse }
        else:
            self.response = {self.type : self.response }

    def generate(self):
        self.pack()
        if (self.withChildren):
            self.packChildren()
        return self.response

    def toEpoch(self, time):
        return time * 5 + 946684800

    def getHistory(self, n):
        history = []
        for i in range(0, n):
            history.append(response(self.type, self.oid, False))


class sql:

    def __init__(self):
        self.dbname = config.getCnf().getDB()
        self.server = config.getCnf().getServer()
        conn = pymssql.connect(self.server)
        self.cursor = conn.cursor()
        self.setDB()

    def setDB(self):
        self.cursor.execute("USE " + self.dbname + ";")

    def runQuery(self, q):
        #print("Running " + q)
        self.cursor.execute(q)
        return self.cursor

    def getDevice(self, oid):
        response = None
        if oid == "all":
            response = self.getObject("device", oid, 0)
            i = 0 
            for r in response["device"]:
                r.update(self.getConnection(str(r["ID"])))
                i +=1
        elif len(oid) < 10:
            response = self.getObject("device", oid, 1)
        else:
            response = self.getObject("device", oid, 0)
        return response   

# These are static classes.  1 per cutomer please.
connection = sql()
def getConn():
    return connection

