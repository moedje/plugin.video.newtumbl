import urlquick
import json
import hashlib
import re
import os
from collections import namedtuple

media = namedtuple("media", ['VIDEO', 'PHOTO', 'ALL'])(*[7,5,0])

class newTumbl(object):

    def __init__(self, datadir='', usertoken='FzCWMJIw6mi8gl6pU6LgpGMcncAg75JIqnqBsiGK2tytG76I', userid=391932):
        self.BASEURL = "https://api-ro.newtumbl.com/sp/NewTumbl/"
        self.headerdict = {'Host': 'api-ro.newtumbl.com',
                      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0',
                      'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br',
                      'Referer': 'https://newtumbl.com/feed',
                      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Pragma': 'no-cache',
                      'Cache-Control': 'no-cache', 'Origin': 'https://newtumbl.com'}
        self.userToken = usertoken
        self.userIx = userid
        self.maxResults = 99
        if datadir == '':
            datadir = os.path.join(os.path.abspath(os.path.expanduser("~")), '.kodi/temp')
        if os.path.exists(datadir) and os.path.isdir(datadir):
            urlquick.CACHE_LOCATION = datadir
        else:
            try:
                os.mkdir(datadir)
            except:
                print("Could not find data directory or create it: " + datadir)
        self.aResultSet = None

    @property
    def NumResults(self):
        return self.maxResults

    @NumResults.setter
    def NumResults(self, value):
        self.maxResults = value

    @property
    def MediaType(self):
        return namedtuple("media", ['VIDEO', 'PHOTO', 'ALL'])(*[7,5,0])

    @property
    def UserToken(self):
        return self.userToken

    @UserToken.setter
    def UserToken(self, value):
        self.userToken = value

    @property
    def UserId(self):
        return self.userIx

    @UserId.setter
    def UserId(self, value):
        self.userIx = value

    @staticmethod
    def GetImageUrl(imgpath="", **kwargs):
        '''
        Parameters:
        BlogID
        PostID
        PartNum (nPartIz)
        MediaID (qwPartIx)
        or imgpath in form of imgpath="/blogid/postid/partid/mediaid" or as much as imgpath="https://dn0.newtumbl.com/img/blogid/postid/partid/mediaid/nT_"
        blogid=265936 postid=6180659 npartiz=1 mediaID=qwPartIx 9257871
        Returns:
        URL to image in format of:
        https://dn0.newtumbl.com/img/{BlogID}/{PostID}/{PartID}/{MediaID}/nT_{Base32(SHA256("/{blogid}/{postid}/{partiz}/{partix}/nT_"))}.jpg or _600|300|150.jpg
        Example: https://dn0.newtumbl.com/img/265936/6180659/1/9257871/nT_bjkrnkq6tjk8j62a05hrzks0.jpg
        '''
        ids = {}
        ids.update(kwargs)
        postid = kwargs.get('qwPostIx', kwargs.get('qwPostIx_From', kwargs.get('qwPostIx_Orig', 0)))
        blogid = kwargs.get('dwBlogIx', kwargs.get('dwBlogIx_From', kwargs.get('dwBlogIx_Orig', kwargs.get('dwBlogIx_Submit', '0'))))
        mediaid = kwargs.get('qwMediaIx', kwargs.get('qwMediaIx_Icon', '0'))
        partid = kwargs.get('nPartIz', 1)
        partix = kwargs.get('qwPartIx', kwargs.get('qwPartIx_Icon', kwargs.get('qwPartIx_Banner', kwargs.get('qwPartIx_Background', mediaid))))
        ids.update({'mediaid': partix, 'partid': partid, 'postid': postid, 'blogid': blogid})
        sMap = "abcdefghijknpqrstuvxyz0123456789"
        sOutput = ""
        i = -1
        b = 0
        c = 0
        d = None
        shalist = []
        abInput = []
        BASEIMGURL = "https://dn0.newtumbl.com/img"
        if imgpath is not "":
            try:
                if imgpath.startswith('http') or imgpath.find('img/') != -1:
                    ids['blogid'],ids['postid'],ids['partid'],ids['mediaid'] = imgpath.split('img/',1)[-1].rpartition('/nT_')[0].split('/',4)
                else:
                    if not imgpath.startswith('/'):
                        imgpath = "/" + imgpath
                    if not imgpath.endswith('/') and not imgpath.endswith('nT_'):
                        imgpath = imgpath + '/nT_'
                    if not imgpath.endswith('nT_'):
                        imgpath = imgpath + 'nT_'
                    imgpath = imgpath.replace('/nT_', '').replace('/nT','')
                    ids['blogid'],ids['postid'],ids['partid'],ids['mediaid'] = imgpath.partition('/')[-1].strip('/').split('/',4)
            except:
                return None
        ids['partid'] = 1
        #sPath = "/" + ids['blogid'].__str__() + "/" + str(ids['postid']) + "/" + str(ids['partid']) + "/" + str(ids['mediaid']) + "/nT_"
        sPath = "/{0}/{1}/{2}/{3}/nT_".format(ids['blogid'].__str__(), ids['postid'].__str__(), ids['partid'].__str__(), ids['mediaid'].__str__())
        sha = hashlib.sha256(sPath.encode('utf-8'))
        hexdigest = sha.hexdigest()
        for t in range(0,len(hexdigest),2): shalist.append(hexdigest[t:t+2])
        for num in shalist: abInput.append(int(num,16))
        # Based on Base32 Javascript method from newtumbl original function runs on a WordArray of 16 pairs of HEX digits returned from SHA256
        # https://newtumbl.com/v1.6.22/js/common.js
        while (i < len(abInput) or b > 0):
            if b < 5:
                i = i+1
                if i < len(abInput):
                    c = (c << 8) + int(abInput[i])
                    b += 8
            d = c % 32
            c = c >> 5
            b = b - 5
            sOutput += sMap[d]
        sOutput = sOutput[0:24]
        imgurl = BASEIMGURL + sPath + sOutput + ".jpg"
        return imgurl


    def getImage(self, **kwargs):
        if not kwargs.get('qwMediaIx', None):
            if kwargs.get('qwMediaIx_Icon', None):
                kwargs.update({'qwMediaIx': kwargs['qwMediaIx_Icon']})
            else:
                kwargs.update(self.getPostMedia(post=kwargs))
        return newTumbl.GetImageUrl(imgpath='', **kwargs)


    def getLikedPosts(self, pagenum=0):
        apiurlfav = 'search_User_Posts_Favorite'
        apiurllike = 'search_User_Posts_Like'
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,'
        reqdatalike=reqdata + str(self.UserId) + ',null,null,0,'+str(self.maxResults)+',' + str(pagenum) + ',null,0,"",1,5,7,0,0,null,null]}'
        litems = []
        dashitems = []
        postitems = []
        tags = []
        likelist = []
        favlist = []
        apiurl = self.BASEURL + apiurlfav
        resp = urlquick.post(url=apiurl, data=reqdatalike, headers=self.headerdict)
        likeresult = resp.json().get('aResultSet', [])
        apiurl = self.BASEURL + apiurllike
        resp = urlquick.post(url=apiurl, data=reqdatalike, headers=self.headerdict)
        faveresult = resp.json().get('aResultSet', [])
        self.aResultSet = likeresult
        if len(likeresult) > 1:
            likelist = likeresult[3].get('aRow', [])
        if len(faveresult) > 1:
            favlist = faveresult[3].get('aRow', [])
        for post in favlist:
            postitems.append(self.makePost(post, faveresult))
        for post in likelist:
            postitems.append(self.makePost(post, likeresult))
        for item in postitems:
            litems.append(self.makePostItem(post=item))
        return litems


    def makePost(self, post={}, postresults=[]):
        postid = post.get('qwPostIx', post.get('qwPostIx_From', post.get('qwPostIx_Orig', 0)))
        blogid = post.get('dwBlogIx', post.get('dwBlogIx_From', post.get('dwBlogIx_Orig', 0)))
        partid = post.get('qwPartIx', 0)
        npart = post.get('nPartIz', 1)
        mediaid = post.get('qwMediaIx', post.get('qwPartIx', 0))
        blogdict = self.getPostBlog(blogid=blogid, results=postresults)
        blogdetails = self.getBlogDetails(blogid)
        post.update(blogdetails)
        post.update(blogdict)
        tags = self.getPostTags(postid)
        #postdict = self.getPost(postid=post.get('qwPostIx', 0), results=dashresult)
        fullpost = self.getPostMedia(post=post, results=postresults)
        if mediaid == 0:
            mediaid = fullpost.get('qwMediaIx', fullpost.get('qwPartIx', 0))
        fullpost.update({"tags": ','.join(tags), "postid": postid, "blogid": blogid, "mediaid": mediaid, "partid": partid, "partnum": npart})
        fullpost.update({'szBody': post.get('szBody', ''), 'szTitle': post.get('szTitle', '')})
        return fullpost


    def makePostItem(self, post={}):
        litem = {}
        about = ""
        label = ""
        label2 = ""
        blogname = ""
        body = ""
        title = ""
        thumb = post.get("thumb", "")
        vurl = post.get("video", "")
        if len(thumb) < 1 or thumb.find('/img/0/0/') != -1:
            thumb = newTumbl.GetImageUrl(**post)
            vurl = thumb.rpartition('.')[0] + ".mp4"
            post.update({"thumb": thumb, "video": vurl})
        blogname = post.get('szBlogId', post.get('szTitle',  ''))
        descrip = post.get('szDescription', '')
        title = post.get('szTitle', descrip)
        about = post.get('szDescription', title)
        body = post.get('szBody', '')
        if len(body) > 1:
            title += " " + body
        #else:
        #    label = post.get('tags', '')
        idlist = dict([[u'{0}'.format(k), u'{0}'.format(v)] for k, v in post.items() if k.lower().find('ix') != -1])
        #about += str(idlist).replace("u'", "'").replace("), (", ",").replace("', ", "':")
        label = title
        label2 = about + u"\n{0}".format(idlist.__str__())
        label = label.replace(',,','')
        infotag = {'plot': label + ' ' + label2}
        infolabel = {'video': infotag}
        litem = {'label': label, 'label2': label2, 'thumb': thumb, 'icon': thumb, 'url': vurl, 'is_folder': False, 'is_playable': True, 'info': infolabel}
        return litem


    def getDashPosts(self, page=0, tag=""):
        litems = []
        dashresult = []
        tags = []
        postitems = []
        dashlist = []
        apiurl = self.BASEURL + "search_Dash_Posts"
        if page > 0:
            if page < 99:
                page = page * 100
        if tag is not "":
            tag = "#{0}".format(tag)
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,'
        reqdatalike=reqdata + str(self.UserId) + ',null,null,0,'+str(self.maxResults)+',' + str(page) + ',null,0,"{0}",1,5,7,0,0,null,null]'.format(tag) +'}'
        resp = urlquick.post(url=apiurl, data=reqdatalike, headers=self.headerdict)
        dashresult = resp.json().get('aResultSet', [])
        self.aResultSet = dashresult
        if len(dashresult) > 1:
            dashlist = dashresult[3].get('aRow', [])
        for post in dashlist:
            postitems.append(self.makePost(post, dashresult))
        for item in postitems:
            litems.append(self.makePostItem(post=item))
        return litems

        '''
        itemoffset = 100 * (page + 1)
        #reqdata = 'json: {"Params":["[{IPADDRESS}]","FzCWMJJMC0WMVF0rLB80CFLEHTy35KKWuPYOWFnL16p2kCv1",null,"474518682472378200",652167258595817300,391932,null,null,0,50,0,null,0,"",0,0,7,0,0,null,null]}'
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',null,null,' + str(itemoffset) + ',100,' + str(itemoffset) + ',null,0,"",0,0,7,0,0,null,null]}'
        resp = urlquick.post(url=apiurl, data=reqdata, headers=self.headerdict)
        jsonobj = resp.json(strict=False)
        print(repr(jsonobj))
        print(str(len(jsonobj)))
        dashresult = jsonobj.get('aResultSet', [])
        self.aResultSet = dashresult
        if len(dashresult) > 1:
            dashlist = dashresult[3].get('aRow', [])
            for post in dashlist:
                try:
                    postid = post.get('qwPostIx', post.get('qwPostIx_From', post.get('qwPostIx_Orig', 0)))
                    blogid = post.get('dwBlogIx', post.get('dwBlogIx_From', post.get('dwBlogIx_Orig', 0)))
                    partid = post.get('qwPartIx', 0)
                    npart = post.get('nPartIz', 1)
                    mediaid = post.get('qwMediaIx', post.get('qwPartIx', 0))
                    #mediadict = self.getPostMedia(postid=postid, results=dashresult)
                    blogdict = self.getPostBlog(blogid=blogid, results=dashresult)
                    tags = self.getPostTags(postid)
                    #postdict = self.getPost(postid=post.get('qwPostIx', 0), results=dashresult)
                    post.update(blogdict)
                    fullpost = self.getPostMedia(post=post, results=dashresult)
                    if mediaid == 0:
                        mediaid = fullpost.get('qwMediaIx', 0)
                    if partid == 0:
                        partid = fullpost.get('qwPartIx', 0)
                    fullpost.update({"tags": ','.join(tags), "postid": postid, "blogid": blogid, "mediaid": mediaid, "partid": partid, "partnum": npart})
                    dashitems.append(fullpost)
                except:
                    pass
        else:
            return []
        about = ""
        label = ""
        label2 = ""
        blogname = ""
        title = ""
        for post in dashitems:
            try:
                assert isinstance(post, dict)
                thumb = post.get("thumb", "")
                vurl = post.get("video", "")
                if len(thumb) < 1 or thumb.find('/img/0/0/') != -1:
                    thumb = newTumbl.GetImageUrl(**post)
                    vurl = thumb.rpartition('.')[0] + ".mp4"
                    post.update({"thumb": thumb, "video": vurl})
                blogname = post.get('szBlogId', '')
                title = post.get('szTitle', '')
                about = post.get('szDescription', blogname)
                if len(title) > 1:
                    label = label + "\n" + post.get('tags', '')
                else:
                    label = post.get('tags', '')
                idlist = dict([[unicode(k), unicode(v)] for k, v in post.items() if k.lower().find('ix') != -1])
                about = str(idlist).replace("u'", "'").replace("), (", ",").replace("', ", "':")
                label2 = blogname + ' ' + title + "\n" + unicode(about)
                infotag = {'plot': about}
                infolabel = {'video': infotag}
                litem = {'label': label, 'label2': label2, 'thumb': thumb, 'icon': thumb, 'url': vurl, 'is_folder': False, 'is_playable': True, 'info': infolabel}
                litems.append(litem)
            except Exception as e:
                pass
        return litems
        '''


    def FollowBlog(self, blogix=0):
        apiurl = self.BASEURL + 'set_FollowBlog_Insert'
        apiurl = apiurl.replace('-ro', '-rw')
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',' + str(blogix) + ']}'
        resp = urlquick.post(apiurl, data=reqdata, headers=self.headerdict)


    def LikeVid(self, vidid=0):
        apiurl = self.BASEURL + 'set_Like_Insert'
        apiurl = apiurl.replace('-ro', '-rw')
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,'+ str(self.userIx) + ',' + str(vidid) + ']}'
        resp = urlquick.post(apiurl, data=reqdata, headers=self.headerdict)
        return resp.ok


    def getPost(self, postid=0, results=None):
        if results is None:
            if self.aResultSet is None:
                return None
            else:
                results = self.aResultSet
        postlist = []
        postlist = results[3].get('aRow', [])
        for post in postlist:
            if post.get('qwPostIx', 0) == postid:
                return post
        return {}


    def getPostBlog(self, blogid=0, results=None):
        if results is None:
            if self.aResultSet is None:
                return None
            else:
                results = self.aResultSet
        bloglist = []
        bloglist = results[2].get('aRow', [])
        for blog in bloglist:
            if blog.get('qwBlogIx', 0) == blogid:
                return blog
        return {}


    def getPostMedia(self, post={}, results=None):
        if results is None:
            if self.aResultSet is None:
                return None
            else:
                results = self.aResultSet
        postid = post.get('qwPostIx', post.get('qwPostIx_From', post.get('qwPostIx_Orig', 0)))
        partid = post.get('qwPartIx', 0)
        if postid == 0:
            return post
        medialist = []
        if partid == 0:
            medialist = results[4].get('aRow', [])
            for media in medialist:
                mpostid = media.get('qwPostIx', media.get('qwPostIx_From', media.get('qwPostIx_Orig', 0)))
                if mpostid == postid:
                    post.update(media)
                    partid = media.get('qwPartIx', media.get("qwPartIx_Icon", media.get("qwPartIx_Banner", media.get("qwPartIx_Background", 0))))
                    break
        medialist = results[1].get('aRow', [])
        for media in medialist:
            if partid == media.get('qwPartIx', 0) and media.get('qwMediaIx', None):
                post.update(media)
                thumb = newTumbl.GetImageUrl(**post)
                vurl = thumb.rpartition('.')[0] + ".mp4"
                post.update({'thumb': thumb, 'video': vurl})
        return post


    def getPostTags(self, postid=0, results=None):
        if results is None:
            if self.aResultSet is None:
                return None
            else:
                results = self.aResultSet
        alltagslist = []
        posttags = []
        alltagslist = results[5].get('aRow', [])
        for tag in alltagslist:
            tagpostid = tag.get('qwPostIx', tag.get('qwPostIx_From', tag.get('qwPostIx_Orig', 0)))
            if tagpostid == postid:
                posttags.append(tag.get('szTag', ''))
        return posttags


    def getBlogDetails(self, blogid=0):
        blogdict = {}
        apiurlblog = self.BASEURL + "get_Blog_Marquee"
        blogresult = []
        blogreqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,'+ str(self.userIx) + ',' + str(blogid) + ']}'
        resp = urlquick.post(url=apiurlblog, data=blogreqdata, headers=self.headerdict)
        #resp = urlquick.request(method="POST", url=apiurlblog, data=blogreqdata, headers=self.headerdict)
        if not resp.ok:
            resp = urlquick.post(url=apiurlblog, data=blogreqdata, headers=self.headerdict)
            if not resp.ok:
                resp = urlquick.post(url=apiurlblog, data=blogreqdata, headers=self.headerdict)
        if resp.ok:
            blogresult = resp.json().get('aResultSet', [])
        if len(blogresult) > 2:
            detresults = blogresult[2].get('aRow', [])
            if len(detresults) > 0:
                blogdict = detresults[0]
            ablog = newTumbl.Blog(**blogdict)
            return ablog
        else:
            return []


    def getVidsForTag(self, tagname="", page=0):
        apiurl = self.BASEURL+"search_Site_Posts"
        litems = []
        tags = []
        postitems = []
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',null,null,0,'+str(self.maxResults)+',' + str(page) + ',null,0,"#'+tagname+'",1,5,7,0,0,null,null]}'
        resp = urlquick.post(url=apiurl, data=reqdata, headers=self.headerdict)
        #resp = urlquick.request(method="POST", url=apiurl, data=reqdata, headers=self.headerdict)
        results = resp.json().get('aResultSet', [])
        self.aResultSet = results
        items = results[3].get('aRow', [])
        for post in items:
            postitems.append(self.makePost(post, results))
        for item in postitems:
            litems.append(self.makePostItem(post=item))
        return litems


    def getBlogPosts(self, blogid=0, pagenum=0, filterby=media.VIDEO, filterdate=""):
        apiurl = self.BASEURL + "search_Blog_Posts"
        litems = []
        postitems = []
        ablog = None
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,'+ str(self.userIx) + ',null,null,0,'+str(self.maxResults)+',' + str(pagenum) + ',null,0,"",1,5,7,0,0,' + str(blogid) + ',null]}'
        resp = urlquick.post(url=apiurl, data=reqdata, headers=self.headerdict)
        results = resp.json().get('aResultSet', [])
        self.aResultSet = results
        if len(results) == 0:
            return []
        else:
            items = results[3].get('aRow', [])
            for post in items:
                postitems.append(self.makePost(post, results))
            for item in postitems:
                litems.append(self.makePostItem(post=item))
        return litems
        '''
            items = results[4]['aRow']
            posts = results[3]['aRow']
            for item in items:
                label = ""
                label2 = ""
                posturl = ""
                blogname = ""
                thumb = newTumbl.GetImageUrl(**item)
                vidurl = thumb.rpartition('.')[0] + ".mp4"
                postid = item.get('qwPostIx', item.get('qwPostIx_From', item.get('qwPostIx_Orig', 0)))
                blogid = item.get('dwBlogIx', item.get('dwBlogIx_From', item.get('dwBlogIx_Orig', item.get('dwBlogIx_Submit'))))
                tags = self.getPostTags(postid)
                item.update({'tags': ','.join(tags)})
                ablog = self.getBlogDetails(blogid)
                if ablog is not None:
                    item.update(ablog.__dict__)
                    if ablog.has_key('szBlogId'):
                        blogname = ablog.get('szBlogId', '')
                label = item.get('szTitle', '') # + " " + item.get('szBody', '')
                if len(label) > 1:
                    label += '\n[I]' + item.get('tags', '') + '[/I]'
                else:
                    label = item.get('tags', '')
                if len(blogname) > 0:
                    label2 = "https://" + blogname + ".newtumbl.com/"
                    posturl = label2 + "post/" + str(postid)
                litems.append({'label': label, 'label2': label2, 'thumb': thumb, 'icon': thumb, 'url': vidurl, 'is_folder': False, 'is_playable': True})
        return litems
        '''


    def makeBlogItem(self, blog):
        litem = {}
        blogix = blog.get('dwBlogIx', '')
        mediaix = blog.get('qwPartIx_Icon', '')
        blogid = blog.get('szBlogId', '')
        blogname = blog.get('szTitle', blogid)
        partid = blog.get('qwPartIx', 0)
        npart = blog.get('nPartIz', 1)
        blogurl = "https://{0}.newtumbl.com/{1}".format(blogid, str(blogix))
        about = blog.get('szDescription', '')
        idlist = dict([[unicode(k), unicode(v)] for k, v in blog.items() if k.lower().find('ix') != -1])
        dictstr = str(idlist).replace("u'", "'").replace("), (", ",").replace("', ", "':") #[i for i in blog if i[0].find('Ix') != -1]).replace("u'", "'").replace("), (", ",").replace("', ", "':")
        if len(about) > 0:
            about = about + "\n" + blogname + " (" + blogid + ") " + blogurl + "\n" + dictstr
        else:
            about = blogname + " (" + blogid + ") " + blogurl + "\n" + dictstr
        idargs = {'blogid': blogix, 'partid': 0, 'postid': 0, 'mediaid': mediaix}
        img = self.getImage(**idargs)
        try:
            label = "[COLOR yellow]{0}[/COLOR] [I]({1})[/I]".format(blogname.encode('uff-8', 'ignore'), blogid.encode('uff-8', 'ignore'))
        except:
            label = blogname
        label2 = about
        infolabel = {'video': {'plot': about}}
        litem = {'label': label, 'label2': label2, 'thumb': img, 'icon': img, 'url': blogurl, 'is_folder': True,
                 'info': infolabel, 'properties': idlist} #{'blogix': str(blogix), 'mediaix': str(mediaix, "partid": partid, "partnum": npart)}
        return litem


    def getFollowedBlogs(self):
        apiurl = self.BASEURL + 'search_User_Blogs_Follow'
        litems = []
        headers = self.headerdict
        headers.update({'Referer': 'https://newwtumbl.com/follow-hide'})
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',null,null,0,25,0,null,1]}'
        resp = urlquick.post(url=apiurl, data=reqdata, headers=headers)
        try:
            aResultSet = resp.json()
        except:
            aResultSet = {}
        if aResultSet.get('aResultSet', []):
            results = aResultSet.get('aResultSet', [])
            self.aResultSet = results
        if len(results) > 0:
            blogs = results[2]['aRow']
            for blog in blogs:
                litems.append(self.makeBlogItem(blog))
        return litems


    def getFollowedTags(self):
        apiurl = self.BASEURL + 'search_User_Tags_Follow'
        litems = []
        aResultSet = {}
        headers = self.headerdict
        headers.update({'Referer': 'https://newwtumbl.com/follow-hide'})
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',null,null,0,100,0,null,1]}'
        resp = urlquick.post(url=apiurl, data=reqdata, headers=headers)
        try:
            aResultSet = resp.json()
        except:
            aResultSet = {}
        results = aResultSet.get('aResultSet', [])
        self.aResultSet = results
        if len(results) > 0:
            tags = results[8].get('aRow',[])
            for tag in tags:
                tagcat = tag.get('szCateogry', "")
                if tagcat is None: tagcat = ""
                tagname = tag.get('szTagId_Dst', tag.get('szTag_Dst', tag.get('szTagId', '')))
                tagnameonly = tagname
                if len(tagcat) > 1:
                    tagname += " ({0})".format(tagcat)
                tagid = str(tag.get('dwTagIx_Dst', tag.get('dwTagIx','')))
                if len(tagname) < 4:
                    tagname += " #" + tagid
                tagitem = {'label': tagname.title(), 'label2': tagid, 'url': tagnameonly, 'is_folder': True, 'is_playable': False}
                litems.append(tagitem)
        return litems


    def SearchForBlog(self, keyword="", pagenum=0):
        # blog icon format: https://dn0.newtumbl.com/img/163769/0/0/4545774/nT_5huakyb46vui0z09rin7ptgi_150.jpg
        # https://dn0.newtumbl.com/img/{blogid}/0/0/{qwMediaIx_Icon}/nT_{Base32(Sha256(path))}.jpg
        # Blogs List aResultSet[0][2]['aRow']
        # Blog Icons aResultSet[0][1]['aRow']
        # curl 'https://api-ro.newtumbl.com/sp/NewTumbl/search_Site_Blogs' -H 'Accept: */*' -H 'Referer: https://newtumbl.com/search' -H 'DNT: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36' -H 'Sec-Fetch-Mode: cors' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data 'json=%7B%22Params%22%3A%5B%22%5B%7BIPADDRESS%7D%5D%22%2C%22FzCWMJIw6mi8gl6pU6LgpGMcncAg75JIqnqBsiGK2tytG76I%22%2C391932%2Cnull%2Cnull%2C0%2C25%2C0%2C%22public%22%2C0%2C0%5D%7D' --compressed
        litems = []
        litem = {}
        headers = self.headerdict
        headers.update({'Referer': 'https://newwtumbl.com/search'})
        reqdata = 'json={"Params":["[{IPADDRESS}]","' + self.userToken + '",null,"474518682472378200",652167258595817300,' + str(self.userIx) + ',null,null,0,25,' + str(pagenum) + ',"' + keyword + '",0,0]}'
        apiurl = self.BASEURL + "search_Site_Blogs"
        resp = urlquick.post(url=apiurl, data=reqdata, headers=headers)
        try:
            aResultSet = resp.json()
        except:
            aResultSet = {}
        results = aResultSet.get('aResultSet', [])
        self.aResultSet = results
        if len(results) > 0:
            blogs = results[2]['aRow']
            for blog in blogs:
                litems.append(self.makeBlogItem(blog))
        return litems


    class Params(dict):

        def __init__(self, **kwargs):
            super(newTumbl.Params, self).__init__(**kwargs)
            usertoken = kwargs.get('usertoken')
            userid = kwargs.get('userid')
            if not kwargs.get('usertoken', None):
                kwargs.update({'usertoken': usertoken})
            if not kwargs.get('userid', None):
                kwargs.update({'userid': userid})
            self.update({"usertoken": usertoken, "userid": userid})
            self.ipaddress= '"[{IPADDRESS}]"'
            self.usertoken= '"{0}"'
            if len(usertoken) > 0:
                self.usertoken = self.usertoken.format(usertoken)
            self.userid=0
            if userid != 0:
                self.userid = userid
            self.blogid= 'null'
            self.field4= 'null'
            self.field5=0
            self.maxnum=99
            self.pagenum=0
            self.field8= 'null'
            self.field9=0
            self.tag= '"#{0}'
            self.field11=0
            self.field12=0
            self.mediatype=media.VIDEO
            self.field13=0
            self.field14=0
            self.category= 'null'
            self.field16= 'null'
            for k, v in kwargs.iteritems():
                try:
                    self.__setattr__(k, v)
                except:
                    pass
                #super.__setattr__(self, k, v)

        def __str__(self):
            return self.Params

        def NextPageParams(self):
            self.pagenum = int(self.pagenum) + int(self.maxnum)
            return self.Params

        @property
        def Tag(self):
            return self.tag

        @Tag.setter
        def Tag(self, value):
            self.tag = "#{0}".format(str(value).strip('#'))

        @property
        def Media(self):
            return self.mediatype

        @Media.setter
        def Media(self, value):
            self.mediatype = value

        @property
        def UserId(self):
            return self.userid

        @UserId.setter
        def UserId(self, value):
            self.userid = value

        @property
        def BlogId(self):
            return self.blogid

        @BlogId.setter
        def BlogId(self, value):
            self.blogid = value

        @property
        def Category(self):
            return self.category

        @Category.setter
        def Category(self, value):
            self.category = value

        @property
        def Token(self):
            return self.usertoken

        @Token.setter
        def Token(self, value):
            self.usertoken = value

        @property
        def Page(self):
            return self.pagenum

        @Page.setter
        def Page(self, value):
            self.pagenum = value

        @property
        def MaxResults(self):
            return self.maxnum

        @MaxResults.setter
        def MaxResults(self, value):
            self.maxnum = value

        @property
        def Params(self):
            return 'json={"Params":[{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}]}'.format(self.ipaddress, self.usertoken, self.userid, self.blogid, self.field4, self.field5, self.maxnum, self.pagenum, self.field8, self.field9, self.tag, self.field11, self.field12, self.mediatype, self.field13, self.field14, self.category, self.field16)


    class Blog(dict):

        def _init__(self, **kwargs):
            """
            : attribute bPrimary : float
            : attribute dwBlogIx : float
            : attribute bStatus : float
            : attribute qwMediaIxIcon : float
            : attribute qwMediaIxBackground : float
            : attribute bHide : float
            : attribute bPrivate : float
            : attribute bRatingIx : float
            : attribute szTitle : string
            : attribute bFollow : float
            : attribute szBlogId : string
            : attribute qwMediaIxBanner : float
            : attribute szDescription : string
            : attribute bIconShape : float
            : attribute dwColorForeground : float
            : attribute bBlock : float
            : attribute dtCreated : string
            : attribute dwUserIx : float
            : attribute dwColorBackground : float
            : attribute bNoIndex : float
            """
            super(newTumbl.Blog, self).__init__(**kwargs)
            self.bPrimary = None
            self.dwBlogIx = None
            self.bStatus = None
            self.qwMediaIxIcon = None
            self.qwMediaIxBackground = None
            self.bHide = None
            self.bPrivate = None
            self.bRatingIx = None
            self.szTitle = None
            self.bFollow = None
            self.szBlogId = None
            self.qwMediaIxBanner = None
            self.szDescription = None
            self.bIconShape = None
            self.dwColorForeground = None
            self.bBlock = None
            self.dtCreated = None
            self.dwUserIx = None
            self.dwColorBackground = None
            self.bNoIndex = None
            for k, v in kwargs.iteritems():
                try:
                    self.__setattr__(k, v)
                except:
                    pass

    class Post(dict):

        def _init__(self, **kwargs):
            """
            : attribute szSource : string
            : attribute dwBlogIx : float
            : attribute dwBlogIxSubmit : float
            : attribute nCountComment : float
            : attribute dtActive : string
            : attribute dwBlogIxFrom : float
            : attribute dwBlogIxOrig : float
            : attribute bTier : float
            : attribute bStatus : float
            : attribute szExternal : string
            : attribute bRatingIx : float
            : attribute szURL : string
            : attribute bPostTypeIx : float
            : attribute dtLike : string
            : attribute qwPostIx : float
            : attribute nCountPost : float
            : attribute dwChecksum : float
            : attribute dtScheduled : string
            : attribute nCountLike : float
            : attribute qwPostIxFrom : float
            : attribute dtCreated : string
            : attribute dtFavorite : string
            : attribute nCountMark : float
            : attribute qwPostIxOrig : float
            : attribute bState : float
            : attribute tags : list PostTag
            """
            super(newTumbl.Post, self).__init__(**kwargs)
            self.dtFlag = None
            self.szSource = None
            self.dwBlogIx = None
            self.dwBlogIxSubmit = None
            self.nCountComment = None
            self.dtActive = None
            self.dwBlogIxFrom = None
            self.dwBlogIxOrig = None
            self.bTier = None
            self.bStatus = None
            self.szExternal = None
            self.dtModified = None
            self.bRatingIx = None
            self.szURL = None
            self.bPostTypeIx = None
            self.dtLike = None
            self.qwPostIx = None
            self.nCountPost = None
            self.dwChecksum = None
            self.dtScheduled = None
            self.nCountLike = None
            self.qwPostIxFrom = None
            self.dtCreated = None
            self.dtFavorite = None
            self.nCountMark = None
            self.qwPostIxOrig = None
            self.bState = None
            self.dtDeleted = None
            for k, v in kwargs.iteritems():
                try:
                    self.__setattr__(k, v)
                except:
                    pass
            self.tags = []
            self.PostIx = kwargs.get('qwPostIx', kwargs.get('qxPostIxFrom', kwargs.get('qwPostIxOrig','0')))
            self.BlogIx = kwargs.get('dwBlogIx', kwargs.get('dwBlogIxFrom', kwargs.get('dwBlogIxOrig', kwargs.get('dwBlogIxSubmit', '0'))))
            self.MediaIx = "{0}"
            self.mediapath = "/{0}/{1}/0/{2}/nT_".format(self.BlogIx, self.PostIx, self.MediaIx)
            self.thumb = ""
            self.movie = ""
            self.Media = newTumbl.PostMedia
            self.tags = []

        def setMedia(self, medialist=[]):
            for media in medialist:
                if not isinstance(media, newTumbl.PostMedia):
                    media = newTumbl.PostMedia(**media)
                if media.PostIx == self.PostIx:
                    self.MediaIx = media.qwMediaIx
                    self.Media = media
                    self.thumb = media.Thumb()
                    self.movie = media.Movie()
                    break

        def setTags(self, taglist=[]):
            for tag in taglist:
                assert isinstance(tag, newTumbl.PostTag)
                if tag.qwPostIx == self.PostIx:
                    self.tags.append(tag)

        def getTagString(self):
            tagstring = ""
            for tag in self.tags:
                tagstring += "," + tag.Name
            tagstring = tagstring.strip(",")
            return tagstring

        @property
        def Tags(self):
            return self.tags

    class PostMedia(dict):

        def _init__(self, **kwargs):
            """
            : attribute bPartTypeIx : float
            : attribute bOrder : float
            : attribute nPartIz : float
            : attribute dtScheduled : string
            : attribute qwMediaIx : float
            : attribute qwPostIx : float
            : attribute dwBlogIxFrom : float
            : attribute qwPostIxFrom : float
            """
            super(newTumbl.PostMedia, self).__init__(**kwargs)
            self.bPartTypeIx = None
            self.bOrder = None
            self.nPartIz = None
            self.dtScheduled = None
            self.qwMediaIx = None
            self.qwPostIx = None
            self.dwBlogIxFrom = None
            self.qwPostIxFrom = None
            for k, v in kwargs.iteritems():
                try:
                    self.__setattr__(k, v)
                except:
                    pass
            self.PostIx = kwargs.get('qwPostIx', kwargs.get('qwPostIxFrom', '0'))
            self.BlogIx = kwargs.get('dwBlogIxFrom', '0')
            self.MediaIx = kwargs.get('qwMediaIx', '0')
            self.thumbnail = ''
            self.movie = ''
            self.Thumb()


        def Thumb(self):
            if self.thumbnail == '':
                self.thumbnail = newTumbl.GetImageUrl(**self.__dict__)
                self.movie = self.thumbnail.replace('.jpg', '.mp4')
            return self.thumbnail


        def Movie(self):
            if self.movie == '':
                self.Thumb()
            return self.movie

    class PostTag(dict):

        def _init__(self, **kwargs):
            """
            : attribute szTag : string
            : attribute qwPostIx : float
            : attribute bOrder : float
            """
            super(newTumbl.PostTag, self).__init__(**kwargs)
            self.szTag = kwargs.get('szTag', '')
            self.qwPostIx = kwargs.get('qwPostIx', '0')
            self.bOrder = kwargs.get('bOrder', 0)
            self.Name = self.szTag.title()
            self.PostIx = self.qwPostIx
            for k, v in kwargs.iteritems():
                try:
                    self.__setattr__(k, v)
                except:
                    pass