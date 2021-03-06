import os
import xbmc, xbmcgui, mc
import ConfigParser
import common

available_providers = ['Addic7ed', 'BierDopje', 'OpenSubtitles', 'SubsWiki', 'Subtitulos', 'Undertexter']

# Set some default values for the subtitles handling
def register_defaults():
    subtitle_provider("get", "default")
    subtitle_provider("get", "tv")
    subtitle_provider("get", "movie")

    xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,%s)" % get_subtitles_language_filter() )
    xbmc.executebuiltin("Skin.SetString(subtitles-plugin,%s)" % get_subtitles_enabled() )
    xbmc.executebuiltin("Skin.SetString(featured-feed,%s)" % get_featured_feed() )
    xbmc.executebuiltin("Skin.SetString(featured-name,%s)" % get_featured_name() )
    xbmc.executebuiltin("Skin.SetString(browser-homepage,%s)" % "".join(get_browser_homepage().split("http://")) )

    if not os.path.exists("/data/etc/.subtitles"):
        common.file_put_contents("/data/etc/.subtitles", """[DEFAULT]
lang = All
movieplugins = OpenSubtitles,Undertexter
tvplugins = BierDopje,OpenSubtitles,Addic7ed,Subtitulos,SubsWiki,Undertexter
plugins = BierDopje,OpenSubtitles,Subtitulos,SubsWiki,Addic7ed,Undertexter

[BierDopje]
key = C2FAFCBE34610608
""")
    
    set_home_enabled_strings()

    version_local = get_local_version()
    if version_local != "":
        xbmc.executebuiltin("Skin.SetString(boxeeplus-version,%s)" % version_local )

def get_home_enabled_default_list():
    return "-,friends,watchlater,shows|Built-in,movies|Built-in,music|Built-in,apps,files,web"
    
def set_home_enabled_strings():
    homeitems = get_home_enabled_default_list().split(",")

    for item in homeitems:
        item = item.split("|")[0]
        xbmc.executebuiltin("Skin.SetString(homeenabled-%s,%s)" % (item, get_homeenabled(item)))
        xbmc.executebuiltin("Skin.SetString(home-%s-replacement,%s)" % (item, get_homereplacement(item)))

def get_jump_to_last_unwatched_value():
    jumpenabled = common.file_get_contents("/data/etc/.jump_to_unwatched_enabled")
    if jumpenabled == "":
        jumpenabled = "0"
    return jumpenabled

def toggle_jump_to_last_unwatched():
    jumpenabled = get_jump_to_last_unwatched_value()
    
    if jumpenabled == "1":
        jumpenabled = "0"
    else:
        jumpenabled = "1"

    common.file_put_contents("/data/etc/.jump_to_unwatched_enabled", jumpenabled)
    xbmc.executebuiltin("Skin.SetString(jump-to-unwatched,%s)" % jumpenabled)

def get_homeenabled_value():
    homeenabled = common.file_get_contents("/data/etc/.home_enabled")
    if homeenabled == "":
        homeenabled = get_home_enabled_default_list()
    return homeenabled.split("\n")[0]

def get_homereplacement(section):
    homeenabled = get_homeenabled_value().split(",")
    
    replacement = ""
    for item in homeenabled:
        item = item.split("|")
        if item[0] == section:
            if len(item) > 1:
                replacement = item[1]
            else:
                replacement = "Built-in"
                
    if replacement == "":
        replacement = "Off"
                
    return replacement
    
def get_homeenabled(section):
    homeenabled = get_homeenabled_value().split(",")
    
    section = "%s" % section
    for item in homeenabled:
        item = item.split("|")[0]
        if item == section:
            return "1"

    return "0"

def toggle_homeenabled(section, action):
    homeenabled = get_homeenabled_value().split(",")

    if section in ["shows","movies","music"]:
        if section == "shows":
            types = ["Built-in", "BBC iPlayer", "Revision3", "Crunchyroll", "Off"]
        if section == "movies":
            types = ["Built-in", "Netflix", "Vudu", "Navi-X", "Off"]
        if section == "music":
            types = ["Built-in", "Spotify", "Grooveshark", "Off"]

        replacement = get_homereplacement(section)
        
        for item in homeenabled:
            itemname = item.split("|")[0]
            if itemname == section:
                homeenabled.remove(item)
        
        pos = types.index(replacement)
        if action == "next":
            pos = pos + 1
        if action == "previous":
            pos = pos - 1
            
        if pos >= len(types):
            pos = 0
        if pos < 0:
            pos = len(types) - 1
        
        if types[pos] != "Off":
            homeenabled.append("%s|%s" % (section, types[pos]))
    
    else:
        found = 0
        for item in homeenabled:
            itemname = item.split("|")[0]
            if itemname == section:
                homeenabled.remove(item)
                found = 1
    
        if found == 0:
            homeenabled.append(section)

    common.file_put_contents("/data/etc/.home_enabled", ",".join(homeenabled))
    set_home_enabled_strings()

def get_browser_homepage():
    homepage = common.file_get_contents("/data/etc/.browser_homepage")

    if homepage == "":
        homepage = "http://www.myfav.es/boxee"

    return homepage

def set_browser_homepage():
    homepage = get_browser_homepage()

    kb = xbmc.Keyboard('default', 'heading', True)
    kb.setDefault(homepage)
    kb.setHeading('Enter homepage URL') # optional
    kb.setHiddenInput(False) # optional
    kb.doModal()

    if kb.isConfirmed():
        homepage = kb.getText()

        common.file_put_contents("/data/etc/.browser_homepage", homepage)

        template = common.file_get_contents("/data/hack/apps/browser2/template.xml")
        template = homepage.join(template.split("$URL$"))
        common.file_put_contents("/data/hack/apps/browser2/descriptor.xml", template)

        os.system("sh /data/hack/apps.sh")

        xbmc.executebuiltin("Skin.SetString(browser-homepage,%s)" % "".join(get_browser_homepage().split("http://")) )

# Set the password for the telnet functionality    
def set_telnet_password():
    passwd = common.file_get_contents("/data/etc/passwd")
    kb = xbmc.Keyboard('default', 'heading', True)
    kb.setDefault(passwd) # optional
    kb.setHeading('Enter telnet password') # optional
    kb.setHiddenInput(True) # optional
    kb.doModal()
    if kb.isConfirmed():
        passwd = kb.getText()

        if passwd == "":
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Telnet', 'The telnet password must not be empty.')
        else:
            common.file_put_contents("/data/etc/passwd", passwd)    

# Determine whether subtitle functionality is enabled/enabled
def get_subtitles_enabled():
    subtitles = common.file_get_contents("/data/etc/.subtitles_enabled")
    if subtitles == "":
        subtitles = "0"
    return subtitles

def get_subtitles_language_filter():
    config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })
    if os.path.exists("/data/etc/.subtitles"):
        config.read("/data/etc/.subtitles")
    langs_config = config.get("DEFAULT", "lang")
    if(langs_config.strip() == "" or langs_config.strip() == "All"):
        return "0"
    else:
        return "1"

def featured_next():
    replace = get_featured_feed_value()
    num = int(replace) + 1
    if num > 4: num = 0

    replace = "%s" % num

    common.file_put_contents("/data/etc/.replace_featured_enabled", replace)
    xbmc.executebuiltin("Skin.SetString(featured-feed,%s)" % get_featured_feed() )
    xbmc.executebuiltin("Skin.SetString(featured-name,%s)" % get_featured_name() )

def featured_previous():
    replace = get_featured_feed_value()
    num = int(replace) - 1
    if num < 0: num = 4

    replace = "%s" % num

    common.file_put_contents("/data/etc/.replace_featured_enabled", replace)
    xbmc.executebuiltin("Skin.SetString(featured-feed,%s)" % get_featured_feed() )
    xbmc.executebuiltin("Skin.SetString(featured-name,%s)" % get_featured_name() )

def get_featured_feed():
    replace = get_featured_feed_value()
    feed = "feed://featured/?limit=15"

    if replace == "1": feed = "boxeedb://recent/?limit=15"
    if replace == "2": feed = "rss://vimeo.com/channels/staffpicks/videos/rss"
    if replace == "3": feed = "rss://gdata.youtube.com/feeds/api/standardfeeds/recently_featured?alt=rss"
    if replace == "4": feed = "about:blank"

    return feed

def get_featured_name():
    replace = get_featured_feed_value()
    name = "Boxee Featured"

    if replace == "1": name = "Recently added"
    if replace == "2": name = "Vimeo staff picks"
    if replace == "3": name = "Youtube featured"
    if replace == "4": name = "Fanart"

    return name

def get_featured_feed_value():
    replace = common.file_get_contents("/data/etc/.replace_featured_enabled")
    if replace == "":
        replace = "0"
    return replace

# Enable/disable the subtitle functionality
def toggle_subtitles(mode, current):
    if mode == "all":
        subtitles = get_subtitles_enabled()

        if subtitles == "1":
            subtitles = "0"
        else:
            subtitles = "1"

        common.file_put_contents("/data/etc/.subtitles_enabled", subtitles)
        os.system("sh /data/hack/subtitles.sh")
        xbmc.executebuiltin("Skin.SetString(subtitles-plugin,%s)" % subtitles)

    if mode == "language":
        if get_subtitles_language_filter() == "0" and current != "1":
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,1)")
        else:
            config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })
            if os.path.exists("/data/etc/.subtitles"):
                config.read("/data/etc/.subtitles")
            config.set("DEFAULT", "lang", "All")

            if os.path.exists("/data/etc/.subtitles"):
                configfile = open("/data/etc/.subtitles", "w")
                config.write(configfile)
                configfile.close()

            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,0)")

# Edit the subtitle providers
def subtitle_provider(method, section, provider=None):
    config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })

    if os.path.exists("/data/etc/.subtitles"):
        config.read("/data/etc/.subtitles")

    plugins = config.get("DEFAULT", "plugins")	
    plugin_section = "default"
    config_section = "plugins"

    if section == "tv":
        plugins = config.get("DEFAULT", "tvplugins")
        plugin_section = "tv"
        config_section = "tvplugins"

    if section == "movie":
        plugins = config.get("DEFAULT", "movieplugins")
        plugin_section = "movie"
        config_section = "movieplugins"

    enabled_providers = plugins.split(',')
    if method == "get":
        if provider != None:
            if provider in enabled_providers:
                return 1
            else:
                return 0

        for checkprovider in available_providers:
            result = 0
            if checkprovider in enabled_providers:
                result = 1
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, checkprovider, result))

    if method == "set":
        provider_status = 1
        if provider in enabled_providers:
            provider_status = 0

        if provider_status == 1:
            enabled_providers.append(provider)
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, provider, 1))
        else:
            enabled_providers.remove(provider)
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, provider, 0))
        config.set("DEFAULT", config_section, ",".join(enabled_providers).strip(','))
        if os.path.exists("/data/etc/.subtitles"):
            configfile = open("/data/etc/.subtitles", "w")
            config.write(configfile)
            configfile.close()

# Get the remote version number from github
def get_remote_version():
    import urllib2
    u = urllib2.urlopen('https://raw.github.com/boxeehacks/boxeehack/master/hack/version')
    version_remote = "%s" % u.read()
    return version_remote

# Get the version number for the locally installed version
def get_local_version():
    version_local = common.file_get_contents("/data/hack/version")
    return version_local

# Check for newer version
def check_new_version():
    version_remote = get_remote_version()
    version_local = get_local_version()
    
    version_remote_parts = version_remote.split(".")
    version_local_parts = version_local.split(".")

    hasnew = 0
    if version_remote_parts[0] > version_local_parts[0]:
        hasnew = 1
    elif version_remote_parts[0] == version_local_parts[0]:
        if version_remote_parts[1] > version_local_parts[1]:
            hasnew = 1
        elif version_remote_parts[1] == version_local_parts[1]:
            if version_remote_parts[2] > version_local_parts[2]:
                hasnew = 1
    issame = 0
    if version_remote_parts[0] == version_local_parts[0]:
        if version_remote_parts[1] == version_local_parts[1]:
            if version_remote_parts[2] == version_local_parts[2]:
                issame = 1

    dialog = xbmcgui.Dialog()
    if hasnew:
        if dialog.yesno("BOXEE+HACKS Version", "A new version of BOXEE+ is available. Upgrade to %s now?" % (version_remote)):
            os.system("sh /data/hack/upgrade.sh")
    elif issame:
        dialog.ok("BOXEE+HACKS Version", "Your BOXEE+ version is up to date.")
    else:
        dialog.ok("BOXEE+HACKS Version", "Hi there Doc Brown. How's the future?")

if (__name__ == "__main__"):
    command = sys.argv[1]

    if command == "telnet": set_telnet_password()
    if command == "subtitles": toggle_subtitles(sys.argv[2], sys.argv[3])
    if command == "version": check_new_version()
    if command == "defaults": register_defaults()
    if command == "subtitles-provider": subtitle_provider("set", sys.argv[2], sys.argv[3])
    if command == "featured_next": featured_next()
    if command == "featured_previous": featured_previous()
    if len(sys.argv) == 4:
        if command == "homeenabled": toggle_homeenabled(sys.argv[2], sys.argv[3])
    else:
        if command == "homeenabled": toggle_homeenabled(sys.argv[2], "")
        
    if command == "browser-homepage": set_browser_homepage()
    if command == "toggle-jump-to-last-unwatched": toggle_jump_to_last_unwatched()