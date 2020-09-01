# -*- coding: utf-8 -*-
# Module: main
# Author: moedje
# Github: https://github.com/moedje/
# Updated on: August 2019
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import ssl, re, os, sys
try:
    import xbmc, xbmcplugin
except:
    import Kodistubs.xbmc as xbmc
    import Kodistubs.xbmcplugin as xbmcplugin
from resources import lib

handle = int(sys.argv[1])
path = os.path
ssl._create_default_https_context = ssl._create_unverified_context
plugin = lib.Plugin() #simpleplugin.Plugin()
__datadir__ = xbmc.translatePath('special://profile/addon_data/{0}/'.format(plugin.id))
__cookie__ = path.join(__datadir__, 'cookies.lwp')
__next__ = path.join(xbmc.translatePath('special://home/addons/{0}/resources/'.format(plugin.id)), 'next.png')
__search__ = __next__.replace('next', 'search')

API = lib.newTumbl(datadir=__datadir__)
urlquick = lib.urlquick
#API = newtumbl.newTumbl(datadir=__datadir__)
VIEWLIST = 51
VIEWTHUMB = 500

@plugin.action()
def root():
    plugin.set_setting('nosearch', "false")
    tagnamelast = plugin.get_setting('lastsearch')
    pagenum = 0
    pagenum = plugin.get_setting('startpagenum')
    if pagenum is None or pagenum == '':
        pagenum = 0
    rootmenu = {
        "Home": [
            {'label': 'Dashboard', 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="get_dashboard", page=pagenum)},
            {'label': 'Dashboard (Public)', 'is_folder': True, 'is_playable': False,
             'url': plugin.get_url(action="get_dashboard", page=pagenum, tag='public')},
            {'label': 'Liked/Favorites', 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="get_liked")},
            {'label': 'Blogs Followed', 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="get_blogs_followed")},
            {'label': 'Blogs Search', 'thumb': __search__, 'icon': __search__, 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="find_blogs")},
            {'label': 'Tags Followed', 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="get_tags_followed")},
            {'label': 'Tagged Gay', 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="get_tag", tagname='gay')},
            {'label': 'Search By Tag', 'thumb': __search__, 'icon': __search__, 'is_folder': True, 'is_playable': False, 'url': plugin.get_url(action="prompt_tag")}
        ]
    }
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWLIST)))
    return rootmenu["Home"]


@plugin.action()
def view_blog(params):
    blogix = 0
    if params.blogid is not None:
        blogix = params.blogid
    litems = []
    blogposts = []
    blogposts = API.getBlogPosts(blogid=blogix, pagenum=0)
    for item in blogposts:
        litems.append(add_ContextDL(item))
    #for post in blogposts:
    #    postid = post.get('properties', {}).get('postix', 0)
    #    ctx = [("Like Post", 'RunPlugin("{0}")'.format(plugin.url(action='like_post', postix=postid)))]
    #    post.update({"context_menu": ctx})
    #    litems.append(post)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    plugin.set_setting('nosearch', "true")
    return litems


@plugin.action()
def get_blogs_followed():
    litems = []
    blogs = []
    blogs = API.getFollowedBlogs()
    for item in blogs:
        blogix = item.get("properties", {}).get("blogix", "")
        url = plugin.get_url(action="view_blog", blogid=blogix)
        item.update({'url': url})
        litems.append(item)
    return litems


@plugin.action()
def find_blogs():
    litems = []
    txt = ''
    txt = get_input(settingid='lastblogsearch')
    bloglist = API.SearchForBlog(keyword=txt)
    for item in bloglist:
        blogix = item.get("properties", {}).get("blogix", "")
        url = plugin.get_url(action="view_blog", blogid=blogix)
        ctx = [('Follow Blog', 'RunPlugin("{0}")'.format(plugin.get_url(action='follow_blog', blogid=blogix)),)]
        item.update({"context_menu": ctx, "url": url})
        litems.append(item)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    plugin.set_setting('nosearch', "true")
    return litems


@plugin.action()
def get_liked():
    litems = []
    items = API.getLikedPosts(pagenum=0)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    for item in items:
        litems.append(add_ContextDL(item))
    return litems


@plugin.action()
def get_dashboard(params):
    pagenum = 0
    tag=''
    if params.page is not None:
        pagenum = int(params.page)
    if params.tag is not None:
        tag = params.tag
    litems = []
    items = []
    try:
        litems = API.getDashPosts(page=pagenum, tag=tag)
    except Exception as e:
        showMessage(e.__context__.__str__(), e.__str__())
        print(e.__str__())
    for item in items:
        litems.append(add_ContextDL(item))
    if len(litems) >= 99:
        nextitem = {'label': "Next Page", 'icon': __next__, 'thumb': __next__, 'url': plugin.get_url(action='get_dashboard', page=(pagenum+100), tag=tag), 'is_folder': True}
        litems.append(nextitem)
    try:
        xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))   
    except Exception as e:
        showMessage(e.__context__.__str__(), e.__str__())
        print(e.__str__())
    return litems


@plugin.action()
def get_tag(params):
    litems = []
    if params.tagname is not None:
        tag = params.tagname
    else:
        tag = "gay"
    items = API.getVidsForTag(tagname=tag)
    for item in items:
        litems.append(add_ContextDL(item))
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    #plugin.log(msg=str(items[:]), level=xbmc.LOGINFO)
    plugin.set_setting('nosearch', "true")
    return litems


@plugin.action()
def get_tags_followed():
    litems = []
    items = API.getFollowedTags()
    for item in items:
        path = plugin.get_url(action='get_tag', tagname=item.get('url', ''))
        item.update({'url': path})
        litems.append(item)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    return litems


@plugin.action()
def tag_search():
    txt = ''
    txt = get_input(settingid='lastsearch')
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    plugin.set_setting('nosearch', "true")
    return API.getVidsForTag(tagname=txt)


@plugin.action()
def search_blogs():
    txt = get_input(settingid='lastblogsearch')
    plugin.set_setting('nosearch', "true")
    return dofind_blogs(txt)


def dofind_blogs(keyword=""):
    litems = []
    bloglist = API.SearchForBlog(keyword=keyword)
    for item in bloglist:
        blogix = item.get("properties", {}).get("blogix", "")
        url = plugin.get_url(action="view_blog", blogid=blogix)
        ctx = [('Follow Blog', 'RunPlugin("{0}")'.format(plugin.get_url(action='follow_blog', blogid=blogix)),)]
        item.update({"context_menu": ctx, "url": url})
        litems.append(item)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    plugin.set_setting('nosearch', "true")
    return litems


@plugin.action()
def follow_blog(params):
    blogix = 0
    if params.blogid is not None:
        blogix = params.blogid
    API.FollowBlog(blogix)
    showMessage(header="NewTumbl", msg="Blog Followed: " + str(blogix))


@plugin.action()
def like_vid(params):
    vidid = 0
    if params.vidid is not None:
        vidid = params.vidid
    if API.LikeVid(vidid):
        showMessage(header="NewTumbl", msg="Added Video to Liked: " + str(vidid))
    else:
        showMessage(header="NewTumbl", msg="Failed to Like Video :( " + str(vidid))




def add_ContextDL(item={}):
    ctxlist = []
    ctxlist = item.get('context_menu', [])
    name = item.get('label', item.get('label2', ''))
    vurl = urlquick.unquote(item.get('url', ''))
    ctx = ("[COLOR green]Download[/COLOR]", 'RunPlugin("{0}")'.format(plugin.get_url(action="download", video=vurl)),)
    ctxlist.append(ctx)
    ctx = ("[COLOR orange]Like[/COLOR]", 'RunPlugin("{0}")'.format(plugin.get_url(action="like_vid", vidid=vurl)),)
    ctxlist.append(ctx)
    item.update({"context_menu": ctxlist})
    return item


@plugin.action()
def download(params):
    vurl = ''
    if params.video is not None:
        vurl = params.video
    else:
        return None
    try:
        from YDStreamExtractor import getVideoInfo
        from YDStreamExtractor import handleDownload
        info = getVideoInfo(vurl, resolve_redirects=True)
        dlpath = plugin.get_setting('downloadpath')
        if not path.exists(dlpath):
            dlpath = xbmc.translatePath("home://")
        handleDownload(info, bg=True, path=dlpath)
    except:
        showMessage(msg=vurl, header="Download Failed")


def showMessage(header='', msg=''):
    try:
        header = str(header.encode('utf-8', 'ignore'))
        msg = str(msg.encode('utf-8', 'ignore'))
        xbmc.executebuiltin('Notification({0},{1})'.format(header, msg))
    except:
        print(header + '\n' + msg)


def get_input(default='', settingid='lastsearch'):
    if default=='':
        default = plugin.get_setting(settingid)
    if bool(plugin.get_setting('nosearch')):
        return default
    kb = xbmc.Keyboard(default, 'Search NewTumbl')
    kb.setDefault(default)
    kb.setHeading('NewTumbl')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        search_term = kb.getText()
        plugin.set_setting(settingid, search_term)
        return(search_term)
    else:
        return None

if __name__ == '__main__':
    # Run our plugin
    xbmcplugin.setContent(handle, 'movies')
    userid = plugin.get_setting('userid')
    usertoken = plugin.get_setting('usertoken')
    VIEWTHUMB = plugin.get_setting('viewthumb')
    VIEWLIST = plugin.get_setting('viewlist')
    API.UserId = userid
    API.UserToken = usertoken
    plugin.run()
    xbmcplugin.setPluginCategory(handle, 'porn')
    xbmc.executebuiltin("Container.SetViewMode({0})".format(str(VIEWTHUMB)))
    #xbmc.executebuiltin('Skin.SetBool(SkinHelper.EnableAnimatedPosters)')