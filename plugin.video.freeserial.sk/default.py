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
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os

# Set the MOZ_HEADLESS environment variable which casues Firefox to start in headless mode.
# os.environ['MOZ_HEADLESS'] = '1'
#
# # Select your Firefox binary.
# binary = FirefoxBinary('/usr/bin/firefox', log_file=sys.stdout)
#
# # Start selenium with the configured binary.
# driver = webdriver.Firefox(firefox_binary=binary)
driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')

# driver = webdriver.PhantomJS(executable_path='/home/pi/phantomjs/bin/phantomjs')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

server_url = 'https://www.freeserial.sk'

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
    driver.get(server_url + movie_url)
    soup = BeautifulSoup(driver.page_source, "html5lib")
    containers = soup.findAll("div", {'class': 'videoBlok'})
    for container in containers:
        stream = container.find("div", {'class': 'videoID'})
        stream_url = str(stream.find('iframe')['src']).replace("//open", "https://open")
        results.append(stream_url)
    return results


def list_search(url, tag):
    req = requests.get(server_url + url)
    soup = BeautifulSoup(req.content, "html5lib")
    results = soup.findAll('a')
    for result in results:
        title = result.find("span", {"class": "name-search"}).text.encode('utf-8')
        urlname = result['href'].encode('utf-8')
        img_url = result.find("img")['src'].encode('utf-8')
        url = build_url({'mode': 'list_series_of_movie', 'foldername': title, 'urlname': urlname})
        li = xbmcgui.ListItem(title, iconImage=str(server_url + img_url))
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)


def zoznam_serialov(url):
    driver.get(server_url + url)
    soup = BeautifulSoup(driver.page_source, "html5lib")
    content = soup.find("div", {"class": "zoznamserialov"})
    all = content.findAll('a')
    for a in all:
        title = a.text.encode('utf-8')
        urlname = a['href'].encode('utf-8')
        url = build_url({'mode': 'epizody_serie', 'foldername': title, 'urlname': urlname})
        li = xbmcgui.ListItem(title, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_epizod(url):
    driver.get(server_url + url)
    soup = BeautifulSoup(driver.page_source, "html5lib")
    content = soup.find("div", {"class": "vypis1"})
    serialy = content.findAll("div", {"class": "item"})
    for serial in serialy:
        title = serial.find("a", {"class": "name"}).text.encode('utf-8')
        urlname = serial.find("a", {"class": "name"})['href'].encode('utf-8')
        url_img = serial.find('img')['src'].encode('utf-8')
        url = build_url({'mode': 'epizoda', 'foldername': title, 'urlname': urlname})
        li = xbmcgui.ListItem(title, iconImage=str(server_url + url_img))
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    ul = content.findAll("ul", {"class": "pager"})
    li = content.findAll('li')
    url = build_url({'mode': 'next_page', 'foldername': 'Next Page', 'urlname': li[-2].find('a')['href']})
    li = xbmcgui.ListItem('Next Page', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_serialov(url):
    driver.get(server_url + url)
    soup = BeautifulSoup(driver.page_source, "html5lib")
    content = soup.find("div", {"class": "vypis1"})
    serialy = content.findAll("div", {"class": "item"})
    for serial in serialy:
        title = serial.find("a", {"class": "name"}).text.encode('utf-8')
        urlname = serial.find("a", {"class": "name"})['href'].encode('utf-8')
        url_img = serial.find('img')['src'].encode('utf-8')
        url = build_url({'mode': 'epizody_serie', 'foldername': title, 'urlname': urlname})
        li = xbmcgui.ListItem(title, iconImage=url_img)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def epizody_serie(url):
    req = requests.get(server_url + url)
    soup = BeautifulSoup(req.content, "html5lib")
    serial = soup.find("div", {"class": "vypisserial"})
    list_epizod = serial.findAll("a")
    for index, epizoda in enumerate(list_epizod):
        title = str(epizoda.text.encode('utf-8'))
        urlname = epizoda['href'].encode('utf-8')
        url = build_url({'mode': 'epizoda', 'foldername': title, 'urlname': urlname})
        li = xbmcgui.ListItem(title, iconImage='DefaultFolder.png')
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

    url = build_url({'mode': 'zoznam_serialov', 'urlname': '/zoznam-serialov/'})
    li = xbmcgui.ListItem('Serialy', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'newly_list', 'urlname': "/vyhladat-serial?q=&qw=&sd=&st=&z=najnovsie-pridane&stranka=1/"})
    li = xbmcgui.ListItem('Nedavno pridane', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'search':
    search_string = getusersearch()
    list_serialov("/?q=" + search_string)


elif mode[0] == 'newly_list':
    urlname = args['urlname'][0]
    list_epizod(urlname)


elif mode[0] == 'epizody_serie':
    urlname = args['urlname'][0]
    epizody_serie(urlname)


elif mode[0] == 'zoznam_serialov':
    urlname = args['urlname'][0]
    zoznam_serialov(urlname)


elif mode[0] == 'epizoda':
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
    list_epizod(urlname)

elif mode[0] == 'play':
    final_link = args['playlink'][0]
    play_video(final_link)

driver.close()
