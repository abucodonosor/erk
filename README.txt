
<p align="center">
	<img src="https://github.com/nutjob-laboratories/erk/raw/master/images/logo_200x200.png"><br>
	<a href="https://github.com/nutjob-laboratories/erk/releases/tag/0.800.066"><b>Download latest stable release</b></a><br>
	<a href="https://github.com/nutjob-laboratories/erk/raw/master/downloads/erk-latest.zip"><b>Download Ərk !_VERSION_!</b></a><br>
	<a href="https://github.com/nutjob-laboratories/erk/blob/master/documentation/Erk_Plugin_Guide.pdf"><b>View Ərk plugin documentation</b></a>
</p>

**Ərk** is a graphical open source [Internet relay chat](https://en.wikipedia.org/wiki/Internet_Relay_Chat) client. The current development version is **!_FULL_VERSION_!**.

**Ərk** is fully functional for use. Most features are complete, but bugs are still being found and fixed, and features are still being added.

# Screenshot

<p align="center">
	<a href="https://github.com/nutjob-laboratories/erk/raw/master/images/screenshot_full.png"><img src="https://github.com/nutjob-laboratories/erk/raw/master/images/screenshot.png"></a><br>
	<b>Ərk connected to EFnet</b><br>
	<i>Click image to enlarge</i><br>
</p>

# Features

* **Ərk** does chat, and _only_ chat.
	* **No** [DCC file transfer](https://en.wikipedia.org/wiki/Direct_Client-to-Client) support
	* **No** [Bittorrent](https://en.wikipedia.org/wiki/BitTorrent) client
	* Just plain ol' fashioned IRC
* Supports multiple connections (you can chat on more than one IRC server at a time)
* Open source ([GPL 3](https://www.gnu.org/licenses/gpl-3.0.en.html))
* An extensive set of configuration options
	* Almost every part of the interface can be customized
	* Most behaviors can be customized
* Built-in [spell checker](https://github.com/barrust/pyspellchecker)
	* Supports English, Spanish, French, and German
	* Right click on misspelled words for suggested spellings/words
* [Emoji](https://en.wikipedia.org/wiki/Emoji) support
	* Insert emojis into chat by using shortcodes (such as `:joy:` :joy:, `:yum:` :yum:, etc.)                                                                        |
* Command/nickname auto-completion
	* Type the first few letters of a command or nickname and hit the tab key
	* Auto-complete works for emoji shortcodes, too
* Optional profanity filter
* Support for IRC color codes (and the option to turn them off)
* A built-in list of over 80 IRC servers to connect to
* Automatic logging of channel and private chats
	* Logging can be switched on and off
	* Logs can be automatically loaded when resuming public or private chats
* Powerful macro engine
	* Users can create and edit macros directly in the client
	* Macros can send messages or execute commands
* Plugins!
	* Plugins are written in Python 3, just like **Ərk**
	* **Ərk** features a complete plugin [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment), built into the client!
		* Text editor with syntax highlighting
		* Tools to create, package, and export plugin packages
		* Create a basic plugin with two mouse clicks!
	* [Plugin documentation](https://github.com/nutjob-laboratories/erk/blob/master/documentation/Erk_Plugin_Guide.pdf) is included...no trying to figure out how to write a plugin from endless forum posts!
	* Plugins can be found in the [official **Ərk** plugin repository](https://github.com/nutjob-laboratories/erk-plugins)
* An extensive set of command-line flags, allowing for _even more_ configuration options
	* Disable most features on startup
	* Connect to an IRC server from the command-line
	* Support for connecting via [IRC URLs](https://www.w3.org/Addressing/draft-mirashi-url-irc-01.txt)

# Requirements
**Ərk** requires Python 3, [PyQt5](https://pypi.org/project/PyQt5/), [Twisted](https://twistedmatrix.com/trac/), and [qt5reactor](https://github.com/sunu/qt5reactor). PyQt5, Twisted, and qt5reactor can be manually installed, or by using [**pip**](https://pypi.org/project/pip/):

    pip install pyqt5
    pip install Twisted
    pip install qt5reactor

To connect to IRC servers via SSL, two additional libraries are needed:

    pip install pyOpenSSL
    pip install service_identity

**Ərk** is being developed with Python 3.7 on Windows 10.

# Install

First, make sure that all the requirements are installed. Next, [download **Ərk**](https://github.com/nutjob-laboratories/erk/raw/master/downloads/erk-latest.zip). Extract the zipfile to a directory of your choice using your favorite archive/zip program. Open a command prompt, navigate to the directory you extracted **Ərk** to, and type:

	python erk.py

Hit enter, and **Ərk** will start up! Click "Connect" on the **Ərk** menu to enter a server hostname/IP and port to connect to a specific IRC server, or click "Networks" to select a server from the built-in server list.

**Ərk** does not need to be "installed" to any specific directory to run; it will run from any directory it is extracted to.

To make things easier, Windows users can create a shortcut to **Ərk** so all you have to do is double click to start chatting. There are many tutorials on how to do this online; a good place to start is [right here](https://therenegadecoder.com/code/how-to-make-a-python-script-shortcut-with-arguments/).

# Frequently asked questions

## Is **Ərk** designed for multiple users?

Not directly, as all its configuration files are stored in **Ərk**'s installation directory. However, there are three command-line options you can use to manage settings for different users:

* `--config` : This tells **Ərk** to use a user-specified file for most configuration options.
* `--user` : This tells **Ərk** to use a user-specified user settings file. Stored in this file are nickname and username settings, server connection history, the disabled plugins list, and other user specific data.
* `--format` : This tells **Ərk** to use a user-specified text display settings file. This sets what colors and formatting is used to display text in the client.

This allows users to set specific configuration files for different users, and can be set in a shortcut or batch file. Configuration and user setting files are JSON, and the text format settings file is CSS. If the filename passed to **Ərk** is not found, **Ərk** will create the file and fill it with default settings.

More command-line settings can be viewed by executing **Ərk** with the `--help` command-line flag.

## What does "erk" mean?

The previous name for this client was "Quirc", but after working on it for a while, I discovered that there was already an IRC client named [Quirc](https://quirc.org/). I was asking for some name suggestions in IRC, when one of the users in the channel suggested "Erk", because "that's how you pronouce IRC". And thus **Ərk** was born.

## Another IRC client? Why not use HexChat?

HexChat is, well, aging. The last I heard, there was nobody maintaining the source. I wanted a new IRC client written in a modern, accessible language; I wanted a client that was *not* written in C or C++. I wanted a pretty, attractive client that looks like it was written in the last decade. And, moreover, I wanted a client written for the desktop; I didn't want one that runs in a web browser, or on a smartphone, or in "the cloud". I wanted a client that was open source (both free as in beer and free as in speech).  I wanted a client that ran fast, consumed resources commensurate with the task of a text-only chat protocol.  I wanted a client that wasn't limited to just text;  a client that can send and display emojis.

Since I couldn't find that IRC client, I decided to write my own.

When I decided to write a new IRC client, I wanted it to feature a few things:

* It had to be open source (free as in speech and as in beer)
* The ability to connect to multiple servers at a time (something almost every open source client does)
* A full, modern GUI (HexChat is sort of modern, I guess, if was still 1999-2000)
* Easy to install, easy to run (if you're trying to compile HexChat for Windows, good luck, you'll need it)
* Focuses on the chat experience (not downloading/uploading files)
* Cross-platform without having to jump through hoops

**Ərk** is being developed on Windows 10, but it uses no Windows-specific libraries or functionality. It's written in pure Python3 and PyQt5, and installing it as easy as cloning this repo, making sure you have Python3 and the other pre-requisites installed, and executing `python erk.py`. It does IRC, and nothing else, and it looks good doing it.

## Is **Ərk** completed?

No. I'm still adding features and tracking down and squashing bugs.

## Can I use **Ərk** to chat on IRC?

Yes! Most basic functionality is done, and it's ready for most IRC stuff.

