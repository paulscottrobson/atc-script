# *****************************************************************************
# *****************************************************************************
#
#		Name:		builder.py
#		Author:		Paul Robson (paul@robsons.org.uk)
#		Date:		27 Sept 2020
#		Purpose:	Builds script for a given script
#
# *****************************************************************************
# *****************************************************************************

import re,sys
from spreadsheet import *

# *****************************************************************************
#
#					Converts script to a CSV import file
#
# *****************************************************************************

class ScriptConverter(object):
	#
	def __init__(self,srcFile):
		self.sheet = Spreadsheet()													# Final spreadsheet
		src = [x.replace("\t"," ") for x in open(srcFile).readlines()] 				# read source file in, do TAB
		src = [x if x.find("#") < 0 else x[:x.find("#")] for x in src] 				# remove comments
		src = [x.strip() for x in src if x.strip() != ""]							# remove blanks
		self.createSubstitutes('D',[x for x in src if x.startswith("$")])			# build substitution hash.
		#
		src = ["[]" if x == "." else x for x in src if not x.startswith("$")]		# remove $x, convert . to []
		src = ["["+x for x in " ".join(src).split("[")]								# allow for multiple lines, [ is new line
		msgCount = 0
		for msg in [x.strip() for x in src if x != "["]:							# work through each line.
			msgCount += 1
			if msg != "[]":															# create if not empty.
				self.generateMessage('A',msgCount,msg)
	#
	#		Process and create a single message
	#
	def generateMessage(self,column,row,msgDef):					
		m = re.match("^\\[(.*?)\\]\\s*(.*)$",msgDef)								# check format
		assert m is not None,"Bad message format "+msgDef
		self.sheet.put(column+str(row),m.group(1).upper())							# output the speaker
		self.sheet.put(self.succ(column)+str(row),self.processMessage(m.group(2)))	# output what they say/should say
	#
	#		Process message substitutions
	#
	def processMessage(self,msg):
		parts = re.split("(\\$[A-Za-z0-9\\_]+)",msg)								# break it up
		for n in range(0,len(parts)):												# look for substitutions
			if parts[n].startswith("$"):
				assert parts[n][1:] in self.subs,"Unknown substitution "+parts[n]
				info = self.subs[parts[n][1:]]										# details.
				parts[n] = info["col"]+str(info["row"])
			else:
				parts[n] = '" '+self.neaten(parts[n].strip())+' "'
				if n == 0:
					parts[n] = parts[n][0]+parts[n][2:]
		parts = [x for x in parts if x != '""']										# remove empty.

		return "=CONCATENATE("+",".join(parts)+")"
	#
	#		Create substitution hash.
	#
	def createSubstitutes(self,column,subList):
		subCount = 0
		self.subs = {}
		for sub in subList:
			m = re.match("^\\$([A-Za-z0-9\\_]+)\\s*(.*)$",sub)						# check each is okay and split up
			assert m is not None,"Bad substituted definition "+sub
			subName = m.group(1).strip().upper()
			subDefault = m.group(2).strip()
			subCount += 1
			assert subName not in self.subs,"Duplicate definition "+sub
			self.subs[subName] = { "name":subName.upper(),"row":subCount,"col":self.succ(column),"default":subDefault }
			self.sheet.put(column+str(subCount),self.neaten(subName)+":")			# generate sheet values.
			self.sheet.put(self.succ(column)+str(subCount),subDefault if subDefault != "" else "???")
	#
	def neaten(self,s):
		return " ".join([self._neaten(c) for c in s.split()])
	def _neaten(self,c):
		return c[0].upper()+c[1:].lower()
	def succ(self,c):
		return chr(ord(c)+1)

if __name__ == "__main__":

	sc = ScriptConverter("demo.atcscript")
	sc.sheet.render(sys.stdout)
	sc.sheet.render(open("testscript.csv","w"))
