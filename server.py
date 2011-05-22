from pymongo import Connection
import cherrypy
import urllib2
import pymongo

connection = Connection()
db = connection.persistence

class Index(object):
    def index(self):
        facebook_str = "https://www.facebook.com/dialog/oauth?client_id=205743116130375&redirect_uri=127.0.0.1:8080/facebook/"
        hunch_str = "http://hunch.com/authorize/v1/?app_id=3144094&next=http://127.0.0.1:8080/hunch/"
#        hunch_str = "http://hunch.com/authorize/v1/?app_id=3144094"
        return "<a href=" + facebook_str + ">Facebook</a><br />" + "<a href=" + hunch_str + ">Hunch</a>"
    index.exposed = True

    def facebook(self,code=""):
        return code
    facebook.exposed = True

    def hunch(self,auth_token_key="",user_id="",next=""):
        #hunch api is broken
        stri = "http://api.hunch.com/api/v1/get-auth-token/?app_id=3144094&auth_sig=37634482be7952e68fadb5b3550a4a1ad814eed1&auth_token_key=" + auth_token_key
#        req = urllib2.urlopen(stri)
        return stri
    hunch.exposed = True

cherrypy.quickstart(Index())
