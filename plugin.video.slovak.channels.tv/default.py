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
import xbmc


channels = {
    "hudobne" : {
        "ocko": "https://ocko-live-dash.ssl.cdn.cra.cz/cra_live2/ocko.stream.1.smil/chunklist_b.m3u8",
        "ocko_star": "https://ocko-live-dash.ssl.cdn.cra.cz/cra_live2/ocko_gold.stream.1.smil/chunklist_b.m3u8",
        "ocko_express": "https://ocko-live-dash.ssl.cdn.cra.cz/cra_live2/ocko_expres.stream.1.smil/chunklist_b.m3u8",
        "retro_music": "http://stream.mediawork.cz/retrotv/retrotvHQ1/chunklist_w.m3u8",
    },
    "sportove": {
        "real_madrid": "http://rmtv24hweblive-lh.akamaihd.net/i/rmtv24hwebes_1@300661/index_3_av-p.m3u8",
        "tv213": "http://s4.media-planet.sk/liverepeater/tv213/chunklist_w.m3u8",
    },
    "zahranicne": {
        "axn": "http://213.81.153.240/live001/channel046_p5.stream/chunklist_w.m3u8",
        "axn_black": "http://213.81.153.243/live003/channel042_p5.stream/chunklist_w.m3u8",
        "axn_white": "http://213.81.153.243/live003/channel041_p5.stream/chunklist_w.m3u8",
        "film_europe": "http://213.81.170.239/live002/channel008_p5.stream/chunklist_w.m3u8",
        "filmbox": "http://213.81.153.240/live001/channel018_p5.stream/chunklist_w.m3u8",
        "filmbox_plus": "http://213.81.153.243/live003/channel043_p5.stream/chunklist_w.m3u8",
        "spektrum": "http://213.81.153.240/live001/channel054_p5.stream/chunklist_w.m3u8",
        "spektrum_home": "http://213.81.153.240/live001/channel056_p5.stream/chunklist_w.m3u8",
        "viasat_explorer": "http://213.81.153.243/live003/channel039_p5.stream/chunklist_w.m3u8",
        "viasat_history": "http://213.81.153.243/live003/channel038_p5.stream/chunklist_w.m3u8",
        "viasat_nature": "http://213.81.153.243/live003/channel009_p5.stream/chunklist_w.m3u8",
        "tv_paprika": "http://213.81.153.243/live003/channel055_p5.stream/chunklist_w.m3u8",
    },
    "ceske": {
        "ct24": "http://213.81.153.240/live001/channel033_p5.stream/chunklist_w.m3u8",
        "ct1": "http://213.81.153.240/live001/channel031_p5.stream/chunklist_w.m3u8",
        "ct2": "http://213.81.153.240/live001/channel032_p5.stream/chunklist_w.m3u8",
    },
    "slovenske": {
        "tv_lux": "http://live.tvlux.sk:1935/lux/lux.stream_360p/chunklist_w.m3u8",
        "ta3": "https://e8.gts.livebox.cz/ta3/1.smil/chunklist_w.m3u8",
        "wau": "https://nn.geo.joj.sk/hls/wau-540.m3u8",
        "doma": "http://213.81.153.243/live003/channel011_p5.stream/chunklist_w.m3u8",
        "dajto": "http://213.81.153.243/live003/channel004_p5.stream/chunklist_w.m3u8",
        "stv2": "http://213.81.153.240/live001/channel002_p5.stream/chunklist_w.m3u8",
        "stv1": "http://213.81.153.240/live001/channel001_p5.stream/chunklist_w.m3u8",
        "joj_family": "https://nn.geo.joj.sk/hls/family-360.m3u8",
        "joj_plus": "https://nn.geo.joj.sk/hls/jojplus-540.m3u8",
        "joj": "https://nn.geo.joj.sk/hls/joj-720.m3u8",
        "markiza": "http://213.81.153.243/live003/channel003_p5.stream/chunklist_w.m3u8"
    }
}

channels_names = {
    "hudobne" : {
        "ocko": "ÓČKO",
        "ocko_star": "ÓČKO STAR",
        "ocko_express": "ÓČKO EXPRESS",
        "retro_music": "RETRO MUSIC",
    },
    "sportove": {
        "real_madrid": "REAL MADRID",
        "tv213": "TV213",
    },
    "zahranicne": {
        "axn": "AXN",
        "axn_black": "AXN BLACK",
        "axn_white": "AXN WHITE",
        "film_europe": "FILM EUROPE",
        "filmbox": "FILM BOX",
        "filmbox_plus": "FILMBOX PLUS",
        "spektrum": "SPEKTRUM",
        "spektrum_home": "SPEKTRUM HOME",
        "viasat_explorer": "VIASAT EXPLORER",
        "viasat_history": "VIASAT HISTORY",
        "viasat_nature": "VIASAT NATURE",
        "tv_paprika": "TV PAPRIKA",
    },
    "ceske": {
        "ct24": "ČT 24",
        "ct1": "ČT 1",
        "ct2": "ČT 2",
    },
    "slovenske": {
        "tv_lux": "TV LUX",
        "ta3": "TA3",
        "wau": "WAU",
        "doma": "DOMA",
        "dajto": "DAJTO",
        "stv2": "STV 2",
        "stv1": "STV 1",
        "joj_family": "JOJ FAMILY",
        "joj_plus": "JOJ PLUS",
        "joj": "JOJ",
        "markiza": "MARKÍZA"
    }
}

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'tvshows')

mode = args.get('mode', None)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def channels_of_category(category_name):
    for name in channels[category_name]:
        url = build_url({'mode': 'play', 'url': channels[category_name][name]})
        li = xbmcgui.ListItem(channels_names[category_name][name])
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


if mode is None:
    url = build_url({'mode': 'kategoria', 'name': 'slovenske'})
    li = xbmcgui.ListItem('Slovenské', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'kategoria', 'name': 'ceske'})
    li = xbmcgui.ListItem('Česke', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'kategoria', 'name': 'zahranicne'})
    li = xbmcgui.ListItem('Zahraničné', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'kategoria', 'name': 'hudobne'})
    li = xbmcgui.ListItem('Hudobné', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'kategoria', 'name': 'sportove'})
    li = xbmcgui.ListItem('Športové', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'kategoria':
    name = args['name'][0]
    channels_of_category(name)


elif mode[0] == 'play':
    url = args['url'][0]
    xbmc.Player().play(url)