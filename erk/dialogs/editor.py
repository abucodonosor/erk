#
#  Erk IRC Client
#  Copyright (C) 2019  Daniel Hetrick
#               _   _       _                         
#              | | (_)     | |                        
#   _ __  _   _| |_ _  ___ | |__                      
#  | '_ \| | | | __| |/ _ \| '_ \                     
#  | | | | |_| | |_| | (_) | |_) |                    
#  |_| |_|\__,_|\__| |\___/|_.__/ _                   
#  | |     | |    _/ |           | |                  
#  | | __ _| |__ |__/_  _ __ __ _| |_ ___  _ __ _   _ 
#  | |/ _` | '_ \ / _ \| '__/ _` | __/ _ \| '__| | | |
#  | | (_| | |_) | (_) | | | (_| | || (_) | |  | |_| |
#  |_|\__,_|_.__/ \___/|_|  \__,_|\__\___/|_|   \__, |
#                                                __/ |
#                                               |___/ 
#  https://github.com/nutjob-laboratories
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import string
import shutil
import zipfile
import re

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from erk.resources import *
from erk.files import PLUGIN_TEMPLATE
import erk.dialogs.find as Find
import erk.dialogs.template as Template
import erk.config
from erk.widgets.action import MenuAction

import erk.dialogs.export_package as Export

import erk.dialogs.editor_input as EditorInput

INSTALL_DIRECTORY = sys.path[0]
PLUGIN_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "plugins")
ERK_MODULE_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "erk")
DATA_DIRECTORY = os.path.join(ERK_MODULE_DIRECTORY, "data")
PLUGIN_SKELETON = os.path.join(DATA_DIRECTORY, "plugin")

def EditorPrompt(title,prompt,twoinputs=False,twoprompt=None):
	x = EditorInput.Dialog(title,prompt,twoinputs,twoprompt)
	info = x.get_string_information(title,prompt,twoinputs,twoprompt)
	del x

	if not info: return None
	return info

def getPackageName(filename):
	dname = filename.replace(os.path.basename(filename),'')
	dname = os.path.join(dname, "package.txt")

	if os.path.isfile(dname):
		script = open(dname,"r")
		pname = script.read()
		script.close()
		return [pname,True]
	else:
		pname = os.path.basename(filename)
		pname = os.path.splitext(pname)[0]
		return [pname,False]

class Window(QMainWindow):

	def closeEvent(self, event):
		if self.changed:
			if erk.config.EDITOR_PROMPT_FOR_SAVE_ON_EXIT:
				self.doExitSave(self.filename)

		if self.app!=None:
			self.app.quit()

		event.accept()
		self.close()

	def docModified(self):
		if self.changed: return
		self.changed = True
		self.title = "* "+self.title
		self.setWindowTitle(self.title)

	def doNewFile(self):
		if self.changed:
			self.doExitSave(self.filename)

		self.filename = ''
		self.sep_icon.hide()
		self.status_file.setText('')
		self.editor.clear()
		self.title = "Editor"
		self.setWindowTitle(self.title)
		self.changed = False
		self.menuSave.setEnabled(False)
		if self.findWindow != None:
			self.findWindow.setWindowTitle("Find")

		#self.status_package.setText("<b><small>Unknown package</small></b>")

		self.package_icon.hide()
		self.status_package.hide()
		self.plugin_icon.hide()

	def doFileSaveAs(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Plugin As...",PLUGIN_DIRECTORY,"Python File (*.py);;All Files (*)", options=options)
		if fileName:
			if '.py' in fileName:
				pass
			else:
				fileName = fileName + '.py'
			self.filename = fileName
			code = open(fileName,"w")
			code.write(self.editor.toPlainText())
			code.close()
			self.title = os.path.basename(fileName)
			self.setWindowTitle(self.title)
			self.sep_icon.show()
			self.status_file.setText("<i><small>"+self.filename+"</small></i>")
			self.changed = False
			self.menuSave.setEnabled(True)
			if self.findWindow != None:
				self.findWindow.setWindowTitle(self.title)

			pname = getPackageName(fileName)
			if pname[1]:
				self.package_icon.show()
				self.status_package.show()
				self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
				self.plugin_icon.hide()
			else:
				self.package_icon.hide()
				self.status_package.show()
				self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
				self.plugin_icon.show()

	def doFileSave(self):
		code = open(self.filename,"w")
		code.write(self.editor.toPlainText())
		code.close()
		self.title = os.path.basename(self.filename)
		self.setWindowTitle(self.title)
		self.sep_icon.show()
		self.status_file.setText("<i><small>"+self.filename+"</small></i>")
		self.changed = False
		if self.findWindow != None:
			self.findWindow.setWindowTitle(self.title)

		pname = getPackageName(self.filename)
		if pname[1]:
			self.package_icon.show()
			self.status_package.show()
			self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
			self.plugin_icon.hide()
		else:
			self.package_icon.hide()
			self.status_package.show()
			self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
			self.plugin_icon.show()

	def doFileOpen(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"Open Plugin", PLUGIN_DIRECTORY,"Python File (*.py);;All Files (*)", options=options)
		if fileName:
			script = open(fileName,"r")
			self.editor.setPlainText(script.read())
			script.close()
			self.filename = fileName
			self.menuSave.setEnabled(True)
			self.title = os.path.basename(fileName)
			self.setWindowTitle(self.title)
			self.sep_icon.show()
			self.status_file.setText("<i><small>"+self.filename+"</small></i>")
			self.changed = False
			if self.findWindow != None:
				self.findWindow.setWindowTitle(self.title)

			pname = getPackageName(fileName)
			if pname[1]:
				self.package_icon.show()
				self.status_package.show()
				self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
				self.plugin_icon.hide()
			else:
				self.package_icon.hide()
				self.status_package.show()
				self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
				self.plugin_icon.show()

	def doExitSave(self,default):
		if not default: default = PLUGIN_DIRECTORY
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Plugin As...",default,"Python File (*.py);;All Files (*)", options=options)
		if fileName:
			if '.py' in fileName:
				pass
			else:
				fileName = fileName + '.py'
			self.filename = fileName
			code = open(fileName,"w")
			code.write(self.editor.toPlainText())

	def hasUndo(self,avail):
		if avail:
			self.menuUndo.setEnabled(True)
		else:
			self.menuUndo.setEnabled(False)

	def hasRedo(self,avail):
		if avail:
			self.menuRedo.setEnabled(True)
		else:
			self.menuRedo.setEnabled(False)

	def hasCopy(self,avail):
		if avail:
			self.menuCopy.setEnabled(True)
			self.menuCut.setEnabled(True)
		else:
			self.menuCopy.setEnabled(False)
			self.menuCut.setEnabled(False)

	def doFind(self):

		if self.findWindow != None:
			ftext = self.findWindow.find.text()
			winpos = self.findWindow.pos()
			if self.findWindow.icount!=' ':
				icount = self.findWindow.icount.text()
			else:
				icount = None
			self.findWindow.close()
		else:
			ftext = None
			winpos = None
			icount = None

		self.findWindow = Find.Dialog(self,False)
		if self.filename:
			self.findWindow.setWindowTitle(self.title)
		if ftext: self.findWindow.find.setText(ftext)

		if winpos:
			self.findWindow.move(winpos)

		if icount:
			self.findWindow.icount.setText(icount)

		self.findWindow.show()
		return

	def doFindReplace(self):

		if self.findWindow != None:
			ftext = self.findWindow.find.text()
			winpos = self.findWindow.pos()
			if self.findWindow.icount!=' ':
				icount = self.findWindow.icount.text()
			else:
				icount = None
			self.findWindow.close()
		else:
			ftext = None
			winpos = None
			icount = None

		self.findWindow = Find.Dialog(self,True)
		if self.filename:
			self.findWindow.setWindowTitle(self.title)
		if ftext: self.findWindow.find.setText(ftext)

		if winpos:
			self.findWindow.move(winpos)

		if icount:
			self.findWindow.icount.setText(icount)


		self.findWindow.show()
		return

	def build_plugin_from_template(self,name,fullname,description,do_check=True):

		if self.indentspace:
			i = ' '*self.tabsize
		else:
			i = "\t"

		out = PLUGIN_TEMPLATE
		out = out.replace('!_INDENT_!',i)
		out = out.replace('!_PLUGIN_NAME_!',name)
		out = out.replace('!_PLUGIN_FULL_NAME_!',fullname)
		out = out.replace('!_PLUGIN_DESCRIPTION_!',description)

		if do_check:
			if 'from erk import *' in self.editor.toPlainText():
				pass
			else:
				if 'from erk import Plugin' in self.editor.toPlainText():
					pass
				else:
					out = 'from erk import *'+"\n\n"+out

		return out

	def menuTemplate(self):
		x = Template.Dialog("Insert",self)
		info = x.get_name_information("Insert",self)

		if info:
			# Create Python-safe name
			safe_name = info[0]
			for c in string.punctuation:
				safe_name=safe_name.replace(c,"")
			safe_name = safe_name.translate( {ord(c): None for c in string.whitespace}  )

			# Escape double quotes in non-safe name
			info[0] = info[0].replace('"','\\"')

			# Escape double quotes in description
			info[1] = info[1].replace('"','\\"')

			t = self.build_plugin_from_template(safe_name,info[0],info[1])
			self.editor.insertPlainText(t)

	def newPackage(self):
		x = Template.Dialog("Create",self)
		info = x.get_name_information("Create",self)

		if info:
			# Create Python-safe name
			safe_name = info[0]
			for c in string.punctuation:
				safe_name=safe_name.replace(c,"")
			safe_name = safe_name.translate( {ord(c): None for c in string.whitespace}  )

			outdir = os.path.join(PLUGIN_DIRECTORY, safe_name)

			if not os.path.exists(outdir):
				os.mkdir(outdir)
				shutil.copy(os.path.join(PLUGIN_SKELETON, "package.png"), os.path.join(outdir, "package.png"))
				shutil.copy(os.path.join(PLUGIN_SKELETON, "plugin.png"), os.path.join(outdir, "plugin.png"))

				# Escape double quotes in non-safe name
				info[0] = info[0].replace('"','\\"')

				f = open(os.path.join(outdir, "package.txt"),"w")
				f.write(info[0])
				f.close()

				self.status_package.setText("<b><small>"+info[0]+"</small></b>")

				self.package_icon.show()
				self.status_package.show()

				# Escape double quotes in description
				info[1] = info[1].replace('"','\\"')

				t = self.build_plugin_from_template(safe_name,info[0],info[1],False)
				t = "from erk import *\n\n"+ t

				f = open(os.path.join(outdir, "plugin.py"),"w")
				f.write(t)
				f.close()

				# Load source into the editor
				self.editor.setPlainText(t)
				self.filename = os.path.join(outdir, "plugin.py")
				self.sep_icon.show()
				self.status_file.setText("<i><small>"+self.filename+"</small></i>")
				self.menuSave.setEnabled(True)
				self.title = "plugin.py"
				self.setWindowTitle(self.title)
				self.changed = False
				if self.findWindow != None:
					self.findWindow.close()

			else:

				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Error")
				msg.setInformativeText("A plugin packaged named \""+safe_name+"\" already exists")
				msg.setWindowTitle("Error")
				msg.exec_()


	def exportPackage(self):
		x = Export.Dialog(self)
		info = x.get_name_information(self)

		if info:
			options = QFileDialog.Options()
			options |= QFileDialog.DontUseNativeDialog
			fileName, _ = QFileDialog.getSaveFileName(self,"Save Package As...",INSTALL_DIRECTORY,"Zip File (*.zip);;All Files (*)", options=options)
			if fileName:
				if '.zip' in fileName:
					pass
				else:
					fileName = fileName + '.zip'
				zf = zipfile.ZipFile(fileName, "w")
				for dirname, subdirs, files in os.walk(info):
					pname = os.path.basename(info)
					for fname in files:
						if "__pycache__" in fname: continue
						filename, file_extension = os.path.splitext(fname)
						if file_extension.lower()==".pyc": continue
						sfile = os.path.join(dirname,fname)
						bname = os.path.basename(sfile)

						zf.write(sfile,pname+"\\"+bname)
				zf.close()


	def __init__(self,filename=None,obj=None,app=None,config=None,parent=None):
		super(Window, self).__init__(parent)

		self.filename = filename
		self.gui = obj
		self.app = app
		self.config = config

		self.changed = False
		self.findWindow = None

		erk.config.load_settings(config)

		if self.filename:
			self.title = os.path.basename(self.filename)
			self.setWindowTitle(self.title)
		else:
			self.setWindowTitle("Editor")
			self.title = "Editor"
		self.setWindowIcon(QIcon(EDITOR_ICON))

		# Use spaces for indent
		self.indentspace = erk.config.USE_SPACES_FOR_INDENT

		# Number of spaces for indent
		self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT

		# Wordwrap
		self.wordwrap = erk.config.EDITOR_WORD_WRAP

		# Autoindent
		self.autoindent = erk.config.EDITOR_AUTO_INDENT

		self.editor = QCodeEditor(self)
		self.highlight = PythonHighlighter(self.editor.document())

		self.highlight.do_highlight = erk.config.EDITOR_SYNTAX_HIGHLIGHT

		self.editor.textChanged.connect(self.docModified)
		self.editor.redoAvailable.connect(self.hasRedo)
		self.editor.undoAvailable.connect(self.hasUndo)
		self.editor.copyAvailable.connect(self.hasCopy)

		if erk.config.EDITOR_FONT!='':
			f = QFont()
			f.fromString(erk.config.EDITOR_FONT)
			self.font = f

			self.editor.setFont(self.font)

		self.setCentralWidget(self.editor)

		self.editor.autoindent = self.autoindent

		self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
		self.editor.customContextMenuRequested.connect(self.contextMenu)

		if self.wordwrap:
			self.editor.setWordWrapMode(QTextOption.WordWrap)
			self.editor.update()
			self.update()
		else:
			self.editor.setWordWrapMode(QTextOption.NoWrap)
			self.editor.update()
			self.update()

		if self.filename:
			if os.path.isfile(self.filename):
				x = open(self.filename,mode="r",encoding="latin-1")
				source_code = str(x.read())
				x.close()
				self.editor.setPlainText(source_code)
				self.changed = False
				self.title = os.path.basename(self.filename)
				self.setWindowTitle(self.title)

		self.menubar = self.menuBar()

		fileMenu = self.menubar.addMenu("File")

		entry = QAction(QIcon(NEWFILE_ICON),"New file",self)
		entry.triggered.connect(self.doNewFile)
		entry.setShortcut("Ctrl+N")
		fileMenu.addAction(entry)

		entry = QAction(QIcon(OPENFILE_ICON),"Open file",self)
		entry.triggered.connect(self.doFileOpen)
		entry.setShortcut("Ctrl+O")
		fileMenu.addAction(entry)

		self.menuSave = QAction(QIcon(SAVEFILE_ICON),"Save file",self)
		self.menuSave.triggered.connect(self.doFileSave)
		self.menuSave.setShortcut("Ctrl+S")
		fileMenu.addAction(self.menuSave)
		if not self.filename:
			self.menuSave.setEnabled(False)

		entry = QAction(QIcon(SAVEASFILE_ICON),"Save as...",self)
		entry.triggered.connect(self.doFileSaveAs)
		fileMenu.addAction(entry)

		fileMenu.addSeparator()

		plugin_dir = QAction(QIcon(DIRECTORY_ICON),"Open plugin directory",self)
		plugin_dir.triggered.connect(lambda state,s=PLUGIN_DIRECTORY: os.startfile(s))
		fileMenu.addAction(plugin_dir)

		fileMenu.addSeparator()

		entry = QAction(QIcon(QUIT_ICON),"Quit",self)
		entry.setShortcut("Ctrl+Q")
		entry.triggered.connect(self.close)
		fileMenu.addAction(entry)

		toolsMenu = self.menubar.addMenu("Tools")

		entry = MenuAction(self,MENU_PACKAGE_ICON,"New package","Create a new plugin package",25,self.newPackage)
		toolsMenu.addAction(entry)

		entry = MenuAction(self,MENU_ARCHIVE_ICON,"Export package","Export an installed package",25,self.exportPackage)
		toolsMenu.addAction(entry)

		toolsMenu.addSeparator()

		entry = QAction(QIcon(INSERT_ICON),"Insert plugin template",self)
		entry.triggered.connect(self.menuTemplate)
		toolsMenu.addAction(entry)

		toolsMenu.addSeparator()

		entry = QAction(QIcon(SPACES_ICON),"Convert indent to spaces",self)
		entry.triggered.connect(lambda state,s="converttospace": self.toggleSetting(s))
		toolsMenu.addAction(entry)

		entry = QAction(QIcon(TABS_ICON),"Convert indent to tabs",self)
		entry.triggered.connect(lambda state,s="converttotab": self.toggleSetting(s))
		toolsMenu.addAction(entry)

		editMenu = self.menubar.addMenu("Edit")

		mefind = QAction(QIcon(WHOIS_ICON),"Find",self)
		mefind.triggered.connect(self.doFind)
		mefind.setShortcut("Ctrl+F")
		editMenu.addAction(mefind)

		mefind = QAction(QIcon(REPLACE_ICON),"Find and replace",self)
		mefind.triggered.connect(self.doFindReplace)
		mefind.setShortcut("Ctrl+R")
		editMenu.addAction(mefind)

		editMenu.addSeparator()

		entry = QAction(QIcon(SELECTALL_ICON),"Select All",self)
		entry.triggered.connect(self.editor.selectAll)
		entry.setShortcut("Ctrl+A")
		editMenu.addAction(entry)

		editMenu.addSeparator()

		self.menuUndo = QAction(QIcon(UNDO_ICON),"Undo",self)
		self.menuUndo.triggered.connect(self.editor.undo)
		self.menuUndo.setShortcut("Ctrl+Z")
		editMenu.addAction(self.menuUndo)
		self.menuUndo.setEnabled(False)

		self.menuRedo = QAction(QIcon(REDO_ICON),"Redo",self)
		self.menuRedo.triggered.connect(self.editor.redo)
		self.menuRedo.setShortcut("Ctrl+Y")
		editMenu.addAction(self.menuRedo)
		self.menuRedo.setEnabled(False)

		editMenu.addSeparator()

		self.menuCut = QAction(QIcon(CUT_ICON),"Cut",self)
		self.menuCut.triggered.connect(self.editor.cut)
		self.menuCut.setShortcut("Ctrl+X")
		editMenu.addAction(self.menuCut)
		self.menuCut.setEnabled(False)

		self.menuCopy = QAction(QIcon(COPY_ICON),"Copy",self)
		self.menuCopy.triggered.connect(self.editor.copy)
		self.menuCopy.setShortcut("Ctrl+C")
		editMenu.addAction(self.menuCopy)
		self.menuCopy.setEnabled(False)

		entry = QAction(QIcon(CLIPBOARD_ICON),"Paste",self)
		entry.triggered.connect(self.editor.paste)
		entry.setShortcut("Ctrl+V")
		editMenu.addAction(entry)

		editMenu.addSeparator()

		entry = QAction(QIcon(PLUS_ICON),"Zoom in",self)
		entry.triggered.connect(self.editor.zoomIn)
		entry.setShortcut("Ctrl++")
		editMenu.addAction(entry)

		entry = QAction(QIcon(MINUS_ICON),"Zoom out",self)
		entry.triggered.connect(self.editor.zoomOut)
		entry.setShortcut("Ctrl+-")
		editMenu.addAction(entry)

		settingsMenu = self.menubar.addMenu("Settings")

		self.fontMenuEntry = QAction(QIcon(FONT_ICON),"Font",self)
		self.fontMenuEntry.triggered.connect(self.menuFont)
		settingsMenu.addAction(self.fontMenuEntry)

		f = self.editor.font()
		fs = f.toString()
		pfs = fs.split(',')
		font_name = pfs[0]
		font_size = pfs[1]

		self.fontMenuEntry.setText(f"Font ({font_name}, {font_size} pt)")

		self.set_wordwrap = QAction(QIcon(UNCHECKED_ICON),"Word wrap",self)
		self.set_wordwrap.triggered.connect(lambda state,s="wordrap": self.toggleSetting(s))
		settingsMenu.addAction(self.set_wordwrap)

		if erk.config.EDITOR_WORD_WRAP: self.set_wordwrap.setIcon(QIcon(CHECKED_ICON))

		self.set_statusbar = QAction(QIcon(UNCHECKED_ICON),"Status bar",self)
		self.set_statusbar.triggered.connect(lambda state,s="statusbar": self.toggleSetting(s))
		settingsMenu.addAction(self.set_statusbar)

		if erk.config.EDITOR_STATUS_BAR: self.set_statusbar.setIcon(QIcon(CHECKED_ICON))

		self.set_syntaxcolor = QAction(QIcon(UNCHECKED_ICON),"Syntax highlighting",self)
		self.set_syntaxcolor.triggered.connect(lambda state,s="highlight": self.toggleSetting(s))
		settingsMenu.addAction(self.set_syntaxcolor)

		if erk.config.EDITOR_SYNTAX_HIGHLIGHT: self.set_syntaxcolor.setIcon(QIcon(CHECKED_ICON))

		self.set_exitsave = QAction(QIcon(UNCHECKED_ICON),"Prompt for save on exit",self)
		self.set_exitsave.triggered.connect(lambda state,s="exitsave": self.toggleSetting(s))
		settingsMenu.addAction(self.set_exitsave)

		if erk.config.EDITOR_PROMPT_FOR_SAVE_ON_EXIT: self.set_exitsave.setIcon(QIcon(CHECKED_ICON))

		settingsMenu.addSeparator()

		self.set_autoindent = QAction(QIcon(UNCHECKED_ICON),"Auto-indent",self)
		self.set_autoindent.triggered.connect(lambda state,s="autoindent": self.toggleSetting(s))
		settingsMenu.addAction(self.set_autoindent)

		if erk.config.EDITOR_AUTO_INDENT: self.set_autoindent.setIcon(QIcon(CHECKED_ICON))

		self.set_indent_spaces = QAction(QIcon(UNCHECKED_ICON),"Use spaces for indent",self)
		self.set_indent_spaces.triggered.connect(lambda state,s="indentspace": self.toggleSetting(s))
		settingsMenu.addAction(self.set_indent_spaces)

		if erk.config.USE_SPACES_FOR_INDENT: self.set_indent_spaces.setIcon(QIcon(CHECKED_ICON))

		self.spacesMenu = settingsMenu.addMenu(QIcon(INDENT_ICON),"Number of spaces to indent")

		self.set_spaces_1 = QAction(QIcon(UNCHECKED_ICON),"One",self)
		self.set_spaces_1.triggered.connect(lambda state,s="spaces_1": self.toggleSetting(s))
		self.spacesMenu.addAction(self.set_spaces_1)

		if self.tabsize==1: self.set_spaces_1.setIcon(QIcon(CHECKED_ICON))

		self.set_spaces_2 = QAction(QIcon(UNCHECKED_ICON),"Two",self)
		self.set_spaces_2.triggered.connect(lambda state,s="spaces_2": self.toggleSetting(s))
		self.spacesMenu.addAction(self.set_spaces_2)

		if self.tabsize==2: self.set_spaces_2.setIcon(QIcon(CHECKED_ICON))

		self.set_spaces_3 = QAction(QIcon(UNCHECKED_ICON),"Three",self)
		self.set_spaces_3.triggered.connect(lambda state,s="spaces_3": self.toggleSetting(s))
		self.spacesMenu.addAction(self.set_spaces_3)

		if self.tabsize==3: self.set_spaces_3.setIcon(QIcon(CHECKED_ICON))

		self.set_spaces_4 = QAction(QIcon(UNCHECKED_ICON),"Four",self)
		self.set_spaces_4.triggered.connect(lambda state,s="spaces_4": self.toggleSetting(s))
		self.spacesMenu.addAction(self.set_spaces_4)

		if self.tabsize==4: self.set_spaces_4.setIcon(QIcon(CHECKED_ICON))

		self.set_spaces_5 = QAction(QIcon(UNCHECKED_ICON),"Five",self)
		self.set_spaces_5.triggered.connect(lambda state,s="spaces_5": self.toggleSetting(s))
		self.spacesMenu.addAction(self.set_spaces_5)

		if self.tabsize==5: self.set_spaces_5.setIcon(QIcon(CHECKED_ICON))

		if not erk.config.USE_SPACES_FOR_INDENT: self.spacesMenu.setEnabled(False)

		self.status = self.statusBar()
		self.status.setStyleSheet('QStatusBar::item {border: None;}')

		self.package_icon = QLabel(self)
		pixmap = QPixmap(PACKAGE_ICON)
		fm = QFontMetrics(self.editor.font())
		pixmap = pixmap.scaled(fm.height()-1, fm.height()-1, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.package_icon.setPixmap(pixmap)

		self.status.addPermanentWidget(self.package_icon,0)


		self.plugin_icon = QLabel(self)
		pixmap = QPixmap(PLUGIN_ICON)
		fm = QFontMetrics(self.editor.font())
		pixmap = pixmap.scaled(fm.height()-1, fm.height()-1, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.plugin_icon.setPixmap(pixmap)

		self.status.addPermanentWidget(self.plugin_icon,0)


		self.status_package = QLabel("<b><small>Unknown package</small></b>")
		self.status.addPermanentWidget(self.status_package,0)

		self.sep_icon = QLabel(self)
		pixmap = QPixmap(VERTICAL_RULE_BACKGROUND)
		fm = QFontMetrics(self.editor.font())
		pixmap = pixmap.scaled(fm.height()-2, fm.height()-2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.sep_icon.setPixmap(pixmap)

		self.status.addPermanentWidget(self.sep_icon,0)

		self.package_icon.hide()
		self.status_package.hide()
		self.sep_icon.hide()
		self.plugin_icon.hide()

		self.status_file = QLabel("")
		self.status.addPermanentWidget(self.status_file,1)

		if self.filename:
			if os.path.isfile(self.filename):
				self.sep_icon.show()
				self.status_file.setText("<i><small>"+self.filename+"</small></i>")

				pname = getPackageName(self.filename)
				if pname[1]:
					self.package_icon.show()
					self.status_package.show()
					self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
					self.plugin_icon.hide()
				else:
					self.package_icon.hide()
					self.status_package.show()
					self.status_package.setText("<b><small>"+pname[0]+"</small></b>")
					self.plugin_icon.show()

		if not erk.config.EDITOR_STATUS_BAR: self.status.hide()

	def menuFont(self):
		font, ok = QFontDialog.getFont()
		if ok:
			erk.config.EDITOR_FONT = font.toString()
			erk.config.save_settings(self.config)

			self.font = font
			self.editor.setFont(self.font)

			pfs = erk.config.EDITOR_FONT.split(',')
			font_name = pfs[0]
			font_size = pfs[1]

			self.fontMenuEntry.setText(f"Font ({font_name}, {font_size} pt)")

	def toggleSetting(self,setting):

		if setting=="exitsave":
			if erk.config.EDITOR_PROMPT_FOR_SAVE_ON_EXIT:
				erk.config.EDITOR_PROMPT_FOR_SAVE_ON_EXIT = False
				self.set_exitsave.setIcon(QIcon(UNCHECKED_ICON))
			else:
				erk.config.EDITOR_PROMPT_FOR_SAVE_ON_EXIT = True
				self.set_exitsave.setIcon(QIcon(CHECKED_ICON))
			erk.config.save_settings(self.config)
			return

		if setting=="highlight":
			if erk.config.EDITOR_SYNTAX_HIGHLIGHT:
				erk.config.EDITOR_SYNTAX_HIGHLIGHT = False
				self.set_syntaxcolor.setIcon(QIcon(UNCHECKED_ICON))
			else:
				erk.config.EDITOR_SYNTAX_HIGHLIGHT = True
				self.set_syntaxcolor.setIcon(QIcon(CHECKED_ICON))
			self.highlight.do_highlight = erk.config.EDITOR_SYNTAX_HIGHLIGHT
			self.toggle_highlight()
			erk.config.save_settings(self.config)
			return

		if setting=="statusbar":
			if erk.config.EDITOR_STATUS_BAR:
				erk.config.EDITOR_STATUS_BAR = False
				self.status.hide()
				self.set_statusbar.setIcon(QIcon(UNCHECKED_ICON))
			else:
				erk.config.EDITOR_STATUS_BAR = True
				self.status.show()
				self.set_statusbar.setIcon(QIcon(CHECKED_ICON))
			erk.config.save_settings(self.config)
			return

		if setting=="converttotab":
			self.convert_indent(' '*self.tabsize,"\t")
			return

		if setting=="converttospace":
			self.convert_indent("\t",' '*self.tabsize)
			return

		if setting=="autoindent":
			if erk.config.EDITOR_AUTO_INDENT:
				erk.config.EDITOR_AUTO_INDENT = False
				self.editor.autoindent = False
				self.set_autoindent.setIcon(QIcon(UNCHECKED_ICON))
			else:
				erk.config.EDITOR_AUTO_INDENT = True
				self.editor.autoindent = True
				self.set_autoindent.setIcon(QIcon(CHECKED_ICON))
			erk.config.save_settings(self.config)
			return

		if setting=="wordrap":
			if erk.config.EDITOR_WORD_WRAP:
				erk.config.EDITOR_WORD_WRAP = False
				self.editor.setWordWrapMode(QTextOption.NoWrap)
				self.editor.update()
				self.update()
				self.set_wordwrap.setIcon(QIcon(UNCHECKED_ICON))
			else:
				erk.config.EDITOR_WORD_WRAP = True
				self.editor.setWordWrapMode(QTextOption.WordWrap)
				self.editor.update()
				self.update()
				self.set_wordwrap.setIcon(QIcon(CHECKED_ICON))
			erk.config.save_settings(self.config)
			return

		if setting=="spaces_5":
			erk.config.NUMBER_OF_SPACES_FOR_INDENT = 5
			erk.config.save_settings(self.config)
			self.set_spaces_5.setIcon(QIcon(CHECKED_ICON))
			self.set_spaces_1.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_2.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_3.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_4.setIcon(QIcon(UNCHECKED_ICON))
			self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT
			return

		if setting=="spaces_4":
			erk.config.NUMBER_OF_SPACES_FOR_INDENT = 4
			erk.config.save_settings(self.config)
			self.set_spaces_4.setIcon(QIcon(CHECKED_ICON))
			self.set_spaces_1.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_2.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_3.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_5.setIcon(QIcon(UNCHECKED_ICON))
			self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT
			return

		if setting=="spaces_3":
			erk.config.NUMBER_OF_SPACES_FOR_INDENT = 3
			erk.config.save_settings(self.config)
			self.set_spaces_3.setIcon(QIcon(CHECKED_ICON))
			self.set_spaces_1.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_2.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_4.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_5.setIcon(QIcon(UNCHECKED_ICON))
			self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT
			return

		if setting=="spaces_2":
			erk.config.NUMBER_OF_SPACES_FOR_INDENT = 2
			erk.config.save_settings(self.config)
			self.set_spaces_2.setIcon(QIcon(CHECKED_ICON))
			self.set_spaces_1.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_3.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_4.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_5.setIcon(QIcon(UNCHECKED_ICON))
			self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT
			return

		if setting=="spaces_1":
			erk.config.NUMBER_OF_SPACES_FOR_INDENT = 1
			erk.config.save_settings(self.config)
			self.set_spaces_1.setIcon(QIcon(CHECKED_ICON))
			self.set_spaces_2.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_3.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_4.setIcon(QIcon(UNCHECKED_ICON))
			self.set_spaces_5.setIcon(QIcon(UNCHECKED_ICON))
			self.tabsize = erk.config.NUMBER_OF_SPACES_FOR_INDENT
			return

		if setting=="indentspace":
			if erk.config.USE_SPACES_FOR_INDENT:
				erk.config.USE_SPACES_FOR_INDENT = False
				self.spacesMenu.setEnabled(False)
			else:
				erk.config.USE_SPACES_FOR_INDENT = True
				self.spacesMenu.setEnabled(True)
			erk.config.save_settings(self.config)
			if erk.config.USE_SPACES_FOR_INDENT:
				self.set_indent_spaces.setIcon(QIcon(CHECKED_ICON))
			else:
				self.set_indent_spaces.setIcon(QIcon(UNCHECKED_ICON))
			self.indentspace = erk.config.USE_SPACES_FOR_INDENT
			return

	def toggle_highlight(self):
		# Save cursor position
		cursor = self.editor.textCursor()
		oldpos = cursor.position()

		doc = self.editor.toPlainText()
		self.editor.clear()
		self.editor.appendPlainText(doc)

		# Move cursor to saved position
		cursor.setPosition(oldpos,QTextCursor.MoveAnchor)
		self.editor.setTextCursor(cursor)

	def convert_indent(self,oldindent,newindent):
		# Save cursor position
		cursor = self.editor.textCursor()
		oldpos = cursor.position()

		doc = self.editor.toPlainText()
		out = []
		for line in doc.split("\n"):
			indent = re.match(r"\s*",line).group()
			line = line.replace(oldindent,newindent)
			out.append(line)
		self.editor.clear()
		self.editor.appendPlainText("\n".join(out))

		# Move cursor to saved position
		cursor.setPosition(oldpos,QTextCursor.MoveAnchor)
		self.editor.setTextCursor(cursor)

	def contextMenu(self,location):

		menu = self.editor.createStandardContextMenu()

		menu.addSeparator()

		funcMenu = QMenu("Insert plugin method")
		funcMenu.setIcon(QIcon(ERK_ICON))
		menu.insertMenu(menu.actions()[0],funcMenu)

		entry = QAction(QIcon(LAMBDA_ICON),"info()",self)
		entry.triggered.connect(lambda state,f="info": self.insertMethod(f))
		funcMenu.addAction(entry)

		entry = QAction(QIcon(LAMBDA_ICON),"uptime()",self)
		entry.triggered.connect(lambda state,f="uptime": self.insertMethod(f))
		funcMenu.addAction(entry)

		entry = QAction(QIcon(LAMBDA_ICON),"exec()",self)
		entry.triggered.connect(lambda state,f="exec": self.insertMethod(f))
		funcMenu.addAction(entry)

		funcMenu.addSeparator()

		entry = QAction(QIcon(PRINT_ICON),"print()",self)
		entry.triggered.connect(lambda state,f="print": self.insertMethod(f))
		funcMenu.addAction(entry)

		entry = QAction(QIcon(CONSOLE_ICON),"console()",self)
		entry.triggered.connect(lambda state,f="console": self.insertMethod(f))
		funcMenu.addAction(entry)

		entry = QAction(QIcon(WINDOW_ICON),"write()",self)
		entry.triggered.connect(lambda state,f="write": self.insertMethod(f))
		funcMenu.addAction(entry)

		entry = QAction(QIcon(WINDOW_ICON),"log()",self)
		entry.triggered.connect(lambda state,f="log": self.insertMethod(f))
		funcMenu.addAction(entry)

		# Finish menu

		menu.insertSeparator(menu.actions()[1])

		action = menu.exec_(self.editor.mapToGlobal(location))

	def insertMethod(self,ctype):

		if ctype=="log":
			data = EditorPrompt("Write/Log to window","Target",True,"Text")
			if data:
				data[0] = data[0].replace('"','\\"')
				data[1] = data[1].replace('"','\\"')
				code = "self.log(\""+data[0]+"\",\""+data[1]+"\")"
				self.editor.insertPlainText(code)

		if ctype=="write":
			data = EditorPrompt("Write to window","Target",True,"Text")
			if data:
				data[0] = data[0].replace('"','\\"')
				data[1] = data[1].replace('"','\\"')
				code = "self.write(\""+data[0]+"\",\""+data[1]+"\")"
				self.editor.insertPlainText(code)

		if ctype=="console":
			data = EditorPrompt("Text to console print","Text")
			if data:
				data = data.replace('"','\\"')
				code = "self.console(\""+data+"\")"
				self.editor.insertPlainText(code)

		if ctype=="print":
			data = EditorPrompt("Text to print","Text")
			if data:
				data = data.replace('"','\\"')
				code = "self.print(\""+data+"\")"
				self.editor.insertPlainText(code)

		if ctype=="exec":
			data = EditorPrompt("Command to execute","Command")
			if data:
				data = data.replace('"','\\"')
				code = "self.exec(\""+data+"\")"
				self.editor.insertPlainText(code)

		if ctype=="info":
			code = "erk_version = self.info()"

			self.editor.insertPlainText(code)

		if ctype=="uptime":
			code = "connection_uptime = self.uptime()"

			self.editor.insertPlainText(code)


def format(color, style=''):
	"""Return a QTextCharFormat with the given attributes.
	"""
	_color = QColor()
	_color.setNamedColor(color)

	_format = QTextCharFormat()
	_format.setForeground(_color)
	if 'bold' in style:
		_format.setFontWeight(QFont.Bold)
	if 'italic' in style:
		_format.setFontItalic(True)
	if 'bi' in style:
		_format.setFontWeight(QFont.Bold)
		_format.setFontItalic(True)

	return _format

# Syntax styles that can be shared by all languages
STYLES = {
	'keyword': format('blue'),
	'operator': format('red'),
	'brace': format('darkGray'),
	'defclass': format('black', 'bold'),
	'string': format('magenta'),
	'string2': format('darkMagenta'),
	'comment': format('darkGreen', 'italic'),
	'self': format('black', 'italic'),
	'numbers': format('brown'),

	'erk': format('#0212b6','bi'),
}

class PythonHighlighter (QSyntaxHighlighter):
	"""Syntax highlighter for the Python language.
	"""

	erk = [
		'self.print','self.console','self.write','self.log','self.uptime',
		'Plugin','self.info','self.exec','from erk import *','from erk import Plugin',
		'self.name','self.description','self.version','self.website','self.source','self.author',
	]

	# Python keywords
	keywords = [
		'and', 'assert', 'break', 'class', 'continue', 'def',
		'del', 'elif', 'else', 'except', 'exec', 'finally',
		'for', 'from', 'global', 'if', 'import', 'in',
		'is', 'lambda', 'not', 'or', 'pass', 'print',
		'raise', 'return', 'try', 'while', 'yield',
		'None', 'True', 'False',
	]

	# Python operators
	operators = [
		'=',
		# Comparison
		'==', '!=', '<', '<=', '>', '>=',
		# Arithmetic
		'\+', '-', '\*', '/', '//', '\%', '\*\*',
		# In-place
		'\+=', '-=', '\*=', '/=', '\%=',
		# Bitwise
		'\^', '\|', '\&', '\~', '>>', '<<',
	]

	# Python braces
	braces = [
		'\{', '\}', '\(', '\)', '\[', '\]',
	]
	def __init__(self, document):
		QSyntaxHighlighter.__init__(self, document)

		self.do_highlight = True

		# Multi-line strings (expression, flag, style)
		# FIXME: The triple-quotes in these two lines will mess up the
		# syntax highlighting from this point onward
		self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
		self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

		rules = []

		# Keyword, operator, and brace rules
		rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
			for w in PythonHighlighter.keywords]
		rules += [(r'%s' % o, 0, STYLES['operator'])
			for o in PythonHighlighter.operators]
		rules += [(r'%s' % b, 0, STYLES['brace'])
			for b in PythonHighlighter.braces]

		# All other rules
		rules += [
			# 'self'
			(r'\bself\b', 0, STYLES['self']),

			# Double-quoted string, possibly containing escape sequences
			(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
			# Single-quoted string, possibly containing escape sequences
			(r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

			# 'def' followed by an identifier
			(r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
			# 'class' followed by an identifier
			(r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

			# From '#' until a newline
			(r'#[^\n]*', 0, STYLES['comment']),

			# Numeric literals
			(r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
			(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
			(r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
		]

		rules += [(r'%s' % o, 0, STYLES['erk'])
			for o in PythonHighlighter.erk]


		# Build a QRegExp for each pattern
		self.rules = [(QRegExp(pat), index, fmt)
			for (pat, index, fmt) in rules]

	def highlightBlock(self, text):

		if not self.do_highlight: return

		"""Apply syntax highlighting to the given block of text.
		"""
		# Do other syntax formatting
		for expression, nth, format in self.rules:
			index = expression.indexIn(text, 0)

			while index >= 0:
				# We actually want the index of the nth match
				index = expression.pos(nth)
				# length = expression.cap(nth).length()
				length = len(expression.cap(nth))
				self.setFormat(index, length, format)
				index = expression.indexIn(text, index + length)

		self.setCurrentBlockState(0)

		# Do multi-line strings
		in_multiline = self.match_multiline(text, *self.tri_single)
		if not in_multiline:
			in_multiline = self.match_multiline(text, *self.tri_double)

	def match_multiline(self, text, delimiter, in_state, style):
		"""Do highlighting of multi-line strings. ``delimiter`` should be a
		``QRegExp`` for triple-single-quotes or triple-double-quotes, and
		``in_state`` should be a unique integer to represent the corresponding
		state changes when inside those strings. Returns True if we're still
		inside a multi-line string when this function is finished.
		"""
		# If inside triple-single quotes, start at 0
		if self.previousBlockState() == in_state:
			start = 0
			add = 0
		# Otherwise, look for the delimiter on this line
		else:
			start = delimiter.indexIn(text)
			# Move past this match
			add = delimiter.matchedLength()

		# As long as there's a delimiter match on this line...
		while start >= 0:
			# Look for the ending delimiter
			end = delimiter.indexIn(text, start + add)
			# Ending delimiter on this line?
			if end >= add:
				length = end - start + add + delimiter.matchedLength()
				self.setCurrentBlockState(0)
			# No; multi-line string
			else:
				self.setCurrentBlockState(in_state)
				# length = text.length() - start + add
				length = len(text) - start + add
			# Apply formatting
			self.setFormat(start, length, style)
			# Look for the next match
			start = delimiter.indexIn(text, start + length)

		# Return True if still inside a multi-line string, False otherwise
		if self.currentBlockState() == in_state:
			return True
		else:
			return False

class QLineNumberArea(QWidget):
	def __init__(self, editor):
		super().__init__(editor)
		self.codeEditor = editor

	def sizeHint(self):
		return QSize(self.editor.lineNumberAreaWidth(), 0)

	def paintEvent(self, event):
		self.codeEditor.lineNumberAreaPaintEvent(event)

class QCodeEditor(QPlainTextEdit):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.parent = parent
		self.lineNumberArea = QLineNumberArea(self)
		self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
		self.updateRequest.connect(self.updateLineNumberArea)
		self.cursorPositionChanged.connect(self.highlightCurrentLine)
		self.updateLineNumberAreaWidth(0)

		self.autoindent = False

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Tab:
			if self.parent.indentspace:
				t = " " * self.parent.tabsize
			else:
				t = "\t"
			self.insertPlainText(t)
			return

		elif event.key() == Qt.Key_Return:
			if self.autoindent:
				cursor = self.textCursor()
				line_number = cursor.blockNumber()
				d = self.document()
				b = d.findBlockByLineNumber(line_number)
				l = b.text()
				indent = re.match(r"\s*",l).group()

				if l[-1:]==':':
					# indent another level
					if self.parent.indentspace:
						indent = indent + (" " * self.parent.tabsize)
					else:
						indent = indent + "\t"

				super().keyPressEvent(event)
				self.insertPlainText(indent)
				return
		
		super().keyPressEvent(event)

	def lineNumberAreaWidth(self):
		digits = 1
		max_value = max(1, self.blockCount())
		while max_value >= 10:
			max_value /= 10
			digits += 1
		space = 3 + self.fontMetrics().width('9') * digits
		return space

	def updateLineNumberAreaWidth(self, _):
		self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

	def updateLineNumberArea(self, rect, dy):
		if dy:
			self.lineNumberArea.scroll(0, dy)
		else:
			self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
		if rect.contains(self.viewport().rect()):
			self.updateLineNumberAreaWidth(0)

	def resizeEvent(self, event):
		super().resizeEvent(event)
		cr = self.contentsRect()
		self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

	def highlightCurrentLine(self):
		extraSelections = []
		if not self.isReadOnly():
			selection = QTextEdit.ExtraSelection()
			lineColor = QColor(Qt.yellow).lighter(160)
			selection.format.setBackground(lineColor)
			selection.format.setProperty(QTextFormat.FullWidthSelection, True)
			selection.cursor = self.textCursor()
			selection.cursor.clearSelection()
			extraSelections.append(selection)
		self.setExtraSelections(extraSelections)

	def lineNumberAreaPaintEvent(self, event):
		painter = QPainter(self.lineNumberArea)

		painter.fillRect(event.rect(), Qt.lightGray)

		block = self.firstVisibleBlock()
		blockNumber = block.blockNumber()
		top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
		bottom = top + self.blockBoundingRect(block).height()

		# Just to make sure I use the right font
		height = self.fontMetrics().height()
		while block.isValid() and (top <= event.rect().bottom()):
			if block.isVisible() and (bottom >= event.rect().top()):
				number = str(blockNumber + 1)
				painter.setPen(Qt.black)
				painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

			block = block.next()
			top = bottom
			bottom = top + self.blockBoundingRect(block).height()
			blockNumber += 1

	