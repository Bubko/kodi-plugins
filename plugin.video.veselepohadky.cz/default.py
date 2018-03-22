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

# _addon = xbmcaddon.Addon()
# _icon = _addon.getAddonInfo('icon')/

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

server_url = 'https://www.veselepohadky.cz'

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

def get_episode_url(movie_url):
    results = []
    req = requests.get(movie_url)
    soup = BeautifulSoup(req.content, "html5lib")
    videoId = str(soup.find("div", {"class": "video-overlay-replay"}).find('img')['src'])
    s = videoId.find('vi/')
    e = videoId.find('/0.')
    # link = "https://www.youtube.com/embed/" + videoId[s + 3:e]
    link = videoId[s+3:e]
    results.append(str(link))
    return results

def list_movies(in_url, tag):
    re = requests.get(in_url)
    soup = BeautifulSoup(re.content, "html5lib")
    content = soup.find("div", {"class": "media-index category-media"})
    items = content.findAll("div", {"class": "media-img"})
    for item in items:
        title = item.find('h2').text.encode('utf-8')
        url_movie = item.find('a')['href'].encode('utf-8')
        url_img = item.find('img')['src']
        url = build_url({'mode': 'movie', 'foldername': title, 'urlname': url_movie})
        li = xbmcgui.ListItem(title, iconImage=str(url_img))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_episodes(in_url):
    re = requests.get(in_url)
    soup = BeautifulSoup(re.content, "html5lib")
    content = soup.find("div", {"class": "media-index"})
    items = content.findAll("div", {"class": "media-img"})
    for item in items:
        title = item.find('h2').text.encode('utf-8')
        url_movie = item.find('a')['href'].encode('utf-8')
        url_img = item.find('img')['src']
        url = build_url({'mode': 'episode', 'urlname': url_movie})
        li = xbmcgui.ListItem(title, iconImage=str(url_img))
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_categories(in_url):
    re = requests.get(server_url + in_url)
    soup = BeautifulSoup(re.content, "html5lib")
    content = soup.find("div", {"class": "all-tags"}).children
    main_categories = []
    categories = []
    for category in content:
        if category.name == 'h2':
            main_categories.append(category)
            categories.append([])
        else:
            s = str(category).find('http')
            e = str(category).find('/\"')
            url = str(category)[s:e]
            if url:
                url = build_url({'mode': 'folder_category', 'foldername': category.string.encode('utf-8'), 'urlname': url})
                li = xbmcgui.ListItem(category.string.encode('utf-8'), iconImage='DefaultFolder.png')
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

if mode is None:
    url = build_url({'mode': 'list_categories', 'urlname': '/vsechny-kategorie/'})
    li = xbmcgui.ListItem('Všetky kategorie', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'list_categories':
    urlname = args['urlname'][0]
    list_categories(urlname)


elif mode[0] == 'folder_category':
    urlname = args['urlname'][0]
    list_movies(urlname, '')


elif mode[0] == 'movie':
    urlname = args['urlname'][0]
    list_episodes(urlname)

elif mode[0] == 'episode':
    url_episode = args['urlname'][0]
    video_play_urls = get_episode_url(url_episode)
    link = 'https://www.youtube.com/watch?v=' + video_play_urls[0]
    url = build_url({'mode': 'play', 'playlink': link})
    li = xbmcgui.ListItem('Play!', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    video_play_url = "https://www.youtube.com/watch?v=6QdIoO02QWU"
    url = build_url({'mode': 'play', 'playlink': video_play_url})
    li = xbmcgui.ListItem('Play Video 2', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    video_play_url = "https://youtube.com/watch?v=6QdIoO02QWU"
    url = build_url({'mode': 'play', 'playlink': video_play_url})
    li = xbmcgui.ListItem('Play Video 3', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'play':
    final_link = args['playlink'][0]
    play_video(final_link)

