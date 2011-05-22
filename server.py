from pymongo import Connection
import cherrypy
import urllib2
import pymongo
import json

import hashlib, urllib

connection = Connection()
db = connection.persistence

class Index(object):
    def index(self):
        facebook_str = "https://www.facebook.com/dialog/oauth?client_id=205743116130375&redirect_uri=127.0.0.1:8080/facebook/"
        hunch_str = "http://hunch.com/authorize/v1/?app_id=3145924"
        foursq_str = "http://foursquare.com/oauth2/authenticate?client_id=SSBHFHA21BL5IWNK1SIKUMNXH05GJOUYV2R3JTQEOVEV5OQW&response_type=code&redirect_uri=http://127.0.0.1:8080/foursq/"
        return "<a href=" + facebook_str + ">Facebook</a><br />" + "<a href=" + hunch_str + ">Hunch</a><br /><a href="+ foursq_str + ">foursquare</a>"
    index.exposed = True

    def facebook(self,code=""):
        return code
    facebook.exposed = True

    def foursq(self,code=""):
        authDict = {}
        authDict["client_id"] = "SSBHFHA21BL5IWNK1SIKUMNXH05GJOUYV2R3JTQEOVEV5OQW"
        authDict["client_secret"] = "3GDIK0DL5EAEZAJ0VIHM1FK4IX3CCIGHP4NBY3AIIUFT5KEY"
        authDict["grant_type"] = "authorization_code"
        authDict["redirect_uri"] = "http://127.0.0.1:8080/foursq/"
        authDict["code"] = code
        urlencoding = urllib.urlencode(authDict)
        req = urllib2.urlopen("https://foursquare.com/oauth2/access_token",urlencoding)

        dicty = json.load(req)
        token = dicty["access_token"]
        
        
        get_user_dict = {"oauth_token":token}
        urlencoding = urllib.urlencode(get_user_dict)
        
        req = urllib2.urlopen("https://api.foursquare.com/v2/users/self?"+urlencoding)

        dicty = json.load(req)
        user_id = dicty["response"]["user"]["id"]
        try:
            query_dict = self.query_gen()
            if not query_dict:
                self.login("foursq.user_id",user_id)
                query_dict["foursq.user_id"]=user_id
            user_collection = db.Users
            if user_collection.find_one(query_dict):
                user_collection.update(query_dict,{"$set":{"foursq":{"token":token,"user_id":user_id}}},upsert=True,safe=True)
            else:
                user_collection.insert({"foursq":{"token":token,"user_id":user_id}},safe=True)
        except pymongo.errors.OperationFailure:
            return "Did not insert or update correctly."
        except:
            return "Did not insert or update correctly."

        return "Inserted or updated Correctly!"

        return req
    foursq.exposed = True

    def hunch(self,auth_token_key="",user_id="",next=""):
        stri = "http://api.hunch.com/api/v1/get-auth-token/?app_id=3145924&auth_sig=" + self.sign_request({"auth_token_key":auth_token_key,"app_id":3145924}) + "&auth_token_key=" + auth_token_key
#        req = json.loads(urllib2.urlopen(stri))
#        return str(json.dumps(req))
        req = urllib2.urlopen(stri)
        dicty = json.loads(req.read())

        req.close()
        user_collection = db.Users
        try:
            query_dict = self.query_gen()
            if not query_dict:
                self.login("hunch.user_id",user_id)
                query_dict["hunch.user_id"]=user_id

            if user_collection.find_one(query_dict):
                user_collection.update(query_dict,{"$set":{"hunch":{"token":dicty["auth_token"],"user_id":user_id}}},upsert=True,safe=True)
            else:
                user_collection.insert({"hunch":{"token":dicty["auth_token"],"user_id":user_id}},safe=True)
        except pymongo.errors.OperationFailure:
            return "Did not insert or update correctly."
        except:
            return "Did not insert or update correctly."

        return "Inserted or updated Correctly!"
    hunch.exposed = True

    def user(self):
        query_dict = self.query_gen()
        if query_dict:
            group_collection = db.Users
            group = group_collection.find_one(query_dict)
            grp_dict = {}
            for key in group.keys():
                if not key == "_id":
                    grp_dict[key] = group[key]
            return json.dumps(grp_dict)
        else:
            return "Log in first."
    user.exposed = True

    def query_gen(self):
        query_dict = {}
        cookie = cherrypy.request.cookie
        for name in cookie.keys():
            query_dict[name] = cookie[name].value
        return query_dict

    def login(self,variety,value):
        cookie = cherrypy.response.cookie
        cookie[variety] = value
        cookie[variety]['max-age'] = 3600
        cookie[variety]['path'] = '/'
        return True

    def logout(self):
        req_cookie = cherrypy.request.cookie
        resp_cookie = cherrypy.response.cookie

        for name in req_cookie.keys():
            resp_cookie[name]['expires'] = 0
        return "Logged out."

    def sign_request(self,query_dict):
        queries = sorted( (unicode(k).encode('utf-8'), unicode(v).encode('utf-8'))
                          for k,v in query_dict.iteritems() )
        data = urllib.urlencode(queries) + "bea75fd900ff3957688c12875399521ba52c6a05"
        return hashlib.sha1(data).hexdigest()



cherrypy.quickstart(Index())
