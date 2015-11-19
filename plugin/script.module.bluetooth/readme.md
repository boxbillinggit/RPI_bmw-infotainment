## Preparation

Before you can run this script you'll need to install following packets:

```sh
# Install bluetooth stack
>> sudo apt-get install bluez-???

# install gammu
>> sudo apt-get install gammu python-gammu
```



## structure

The XML-files must be in this folder structure, because XBMC/KODI adds this to it's path when looking for the file.


# Development environment

During development it's convenient to be able to reload, minimize XBMC/KODI, hence place a keymap.xml here:

/home/<username>/.kodi/userdata/keymaps

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
Ref: http://kodi.wiki/view/First_skin_tutorial
     http://kodi.wiki/view/Keymap#Location_of_keymaps
-->

<keymap>
    <global>
        <keyboard>
	    <F4>Minimize</F4>
            <F5>RestartApp</F5>
            <F6>Quit</F6>
            <F7>Skin.ToggleSetting(HideDebugInfo)</F7>
            <F8>XBMC.ReloadSkin()</F8>
        </keyboard>
    </global>
</keymap>

```


Logfiles is placed here (Linux):

```sh
/home/<username>/.kodi/temp/kodi.log
```

A Debugger is convenient,I'm using WinPDB:

http://kodi.wiki/view/HOW-TO:Debug_python_scripts_with_WinPDB

# PyCharm environment

Run import __init__ to be able to use Python console