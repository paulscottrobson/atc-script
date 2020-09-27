# *****************************************************************************
# *****************************************************************************
#
#		Name:		spreadsheet.py
#		Author:		Paul Robson (paul@robsons.org.uk)
#		Date:		27 Sept 2020
#		Purpose:	Object representing Spreadsheet.
#					Tested on : Libre Office, Google Sheets.
#
# *****************************************************************************
# *****************************************************************************

import re,sys

# *****************************************************************************
#
#								Spreadsheet Class
#
# *****************************************************************************

class Spreadsheet(object):
	def __init__(self):
		self.cells = {}
		self.xMax = 'A'
		self.yMax = 1
	#
	def get(self,ref):
		ref = self.check(ref)
		return self.cells[ref] if ref in self.cells else ""
	#
	def put(self,ref,value):
		self.cells[self.check(ref)] = value
	#
	def check(self,ref):
		assert re.match("^[A-Za-z]\\d+$",ref) is not None,"Bad cell reference "+ref
		ref = ref.upper()
		self.xMax = max(self.xMax,ref[0])
		self.yMax = max(self.yMax,int(ref[1:]))
		return ref
	#
	def render(self,handle):
		for row in range(1,self.yMax+1):
			s = ",".join([self.renderCell(chr(col),row) for col in range(ord('A'),ord(self.xMax)+1)])
			handle.write(s+"\n")
	#
	def renderCell(self,x,y):
		c = self.get(x+str(y))
		return '"'+str(c).replace('"','""')+'"'

if __name__ == "__main__":
	s = Spreadsheet()
	s.put('A1',2)
	s.put('A2',4)
	s.put('B1',"Hello world")
	s.put('C3',"=A1+A2")
	s.put('D2','=CONCAT(B1,"!")')
	s.render(sys.stdout)
	s.render(open("testspr.csv","w"))

	