# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2018 Blazej Rypak
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import sys
import xbmcgui
import xbmcplugin
import urllib
import urlparse
from bs4 import BeautifulSoup
import requests
import urlresolver
import xbmc
from selenium import webdriver

driver = webdriver.PhantomJS()

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

server_url = 'https://www.topserialy.to'

def resolve_url(url):
    duration = 7500   #in milliseconds
    message = "Cannot Play URL"
    stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    # If urlresolver returns false then the video url was not resolved.
    if not stream_url:
        dialog = xbmcgui.Dialog()
        dialog.notification("URL Resolver Error", message, xbmcgui.NOTIFICATION_INFO, duration)
        return False
    else:
        return stream_url

def play_video(path):
    """
    Play a video by the provided path.
    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    vid_url = play_item.getfilename()
    stream_url = resolve_url(vid_url)
    if stream_url:
        play_item.setPath(stream_url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def get_movie_url(movie_url):
    results = []
    re = requests.get(server_url+movie_url)
    soup = BeautifulSoup(re.content, "html5lib")
    link = soup.find('a', {'class': 'play-movie'})
    if link and link['data-loc']:
        url = 'http://stream-a-ams1xx2sfcdnvideo5269.cz/'
        url += 'okno.php?movie='
        url += link['data-loc']
        url += '&new_way'
        re = requests.get(url)
        soup = BeautifulSoup(re.content, "html5lib")
        containers = soup.findAll("div", {'class': 'center--inner'})
        for container in containers:
            stream = container.find("div", {'class': 'player-container'})
            stream_link = stream.find("iframe")['src']
            results.append(stream_link)
        return results

def list_series(search_string, tag):
    url = '/serialy'
    driver.get(server_url + url)
    soup = BeautifulSoup(driver.page_source, "html5lib")
    content = soup.find('div', {"class": "vysledky-hladania"})
    results = content.findAll('a')
    for result in results:
        if search_string in result['data-altname'] or search_string in result['data-name']:
            title = result['data-name']
            url_movie = result['href']
            url_img = result.find('img')['data-original']
            url = build_url({'mode': 'series', 'foldername': title, 'urlname': url_movie})
            li = xbmcgui.ListItem(title, iconImage=str(server_url + url_img))
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_seasons(in_url):
    re = requests.get(server_url + in_url)
    soup = BeautifulSoup(re.content, "html5lib")
    content = soup.find("div", {"id": "allseries"})
    genres = content.find("div", {"class": "buts"}).findAll('a')
    for genre in genres:
        foldername = genre.text.encode('utf-8')
        urlname = genre['href'].encode('utf-8')
        url = build_url({'mode': 'folder_category', 'foldername': foldername, 'urlname': urlname})
        li = xbmcgui.ListItem(foldername, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def getusersearch():
    kb = xbmc.Keyboard('default', 'heading')
    kb.setDefault('')
    kb.setHeading('Search')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        search_term = kb.getText()
        return(search_term)
    else:
        return

if mode is None:
    url = build_url({'mode': 'search'})
    li = xbmcgui.ListItem('Search', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'search':
    search_string = getusersearch()
    list_series(search_string, 'search')


elif mode[0] == 'series':
    urlname = args['urlname'][0]
    list_seasons(urlname)


elif mode[0] == 'folder_category':
    urlname = args['urlname'][0]
    list_movies(urlname, '')


elif mode[0] == 'movie':
    title = args['foldername'][0]
    url_movie = args['urlname'][0]
    video_play_urls = get_movie_url(url_movie)
    for index, video_play_url in enumerate(video_play_urls):
        url = build_url({'mode': 'play', 'playlink': video_play_url})
        li = xbmcgui.ListItem('Play source ' + str(index), iconImage='DefaultVideo.png')
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'next_page':
    urlname = args['urlname'][0]
    list_movies(urlname, '')

elif mode[0] == 'play':
    final_link = args['playlink'][0]
    play_video(final_link)