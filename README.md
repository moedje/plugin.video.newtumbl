# plugin.video.newtumbl 
(31/08/2020)

Kodi/XBMC Addon for Newtumbl.com (Adult Content Ok)

I originally created plugin.video.tumblrv as a Kodi addon for watching adult content that was all over Tumblr but then they turned into prudes and started to disallow adult content.

## NewTumbl.Com
http://newtumbl.com

Of the many new Tumblr style sites that got created after this adult content ban, this was the one I was most impressed with.

![](https://github.com/moedje/plugin.video.newtumbl/blob/master/resources/screenshot-01.jpg?raw=true)

![](https://github.com/moedje/plugin.video.newtumbl/blob/master/resources/screenshot-02.jpg?raw=true)

Unlike Tumblr though which provided a fully open API to build on top of it, NewTumbl has not yet made this available. However, I looked at the web page in Chrome's developer tools and found most of the API call's that I needed and was able to backwards engineer an addon for it.

The only thing I can't easily do yet is make it easier for you to login.

The details needed to make this addon pull your own NewTumbl Dashboard and content is able to be set in the settings of the addon but you need to manually get these details from your web browsers Developer Tools I will show you where to find the required *UserToken* and *UserId*

- In **Developer Tools** go to **Network**
- Select **XHR**
- Login to http://newtumbl.com
- Look in the Developer Tools area (while under Network and selected on XHR) for **Search_Dash_Posts** and click on it (If you don't see this then click the Feed icon again on NewTumbl and you should see more things load in the Network section and **search_Dash_Posts** will be there.
- Scroll down in the panel to the right which should have **Headers** selected and scroll to very bottom
- Under Form Data the last entry is json: {"Params":["[{IPADDRESS}]","**1-YourUserToken-LotsOfRandomCharacters**",null,"somenumbers","somenumbers",**2-YourUSERIDNUMBER**,null,null...
- In the settings for this addon you will see a field for **user Token**, this is the first entry after IPADDRESS that you need to copy and paste
- The second bolded entry above is your userid, probably 6 to 8 numbers and paste that in the addon settings.
- This should then allow the addon to pull up your own Dashoard, Liked Videos, Saved Tags, etc

I'm sorry I can't find an easier way to get these two values but if anyone else knows one by all means let me know. If you don't the addon will still open but it will be pulling an account I control on NewTumbl that all versions of this addon point to.

## Gay Addons Repo for Kodi
For more of my addons check out my Repo
https://github.com/moedje/kodi-repo-gaymods/

The direct download for the ZIP file to install in Kodi is located at https://github.com/moedje/kodi-repo-gaymods/blob/master/repository.kodi-repo-gaymods/repository.kodi-repo-gaymods-2.0.69.zip?raw=true

####Jeremy Becoedsway
alljer@gmail.com
