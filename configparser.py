import re
import os

class Expression:
	
	def __init__(self, value, match):
		self.value = value
		self.match = match

	def __makeNumber__(self, number):
		try:
			inumber = int(number)
			return inumber
		except ValueError:
			fnumber = float(number)
			return fnumber


class NumberExpression(Expression):
	
	def getValue(self):
		return self.__makeNumber__(self.match.group('float'))

class StringExpression(Expression):
	
	def getValue(self):
		return self.match.group('string')
		
class TupleExpression(Expression):
	
	def getValue(self):
		value1 = self.match.group('number1')
		value2 = self.match.group('number2')
		return (self.__makeNumber__(value1), self.__makeNumber__(value2))		
		
class RegExpression(Expression):
	
	def getValue(self):	
		return self.__formatReg__(self.match.group('reg'))

	def __formatReg__(self, regExpression):
		regExpression = regExpression.replace(".", "\.")
		regExpression = regExpression.replace("<ignore>", ".+")
		regExpression = regExpression.replace("<","(?P<")
		regExpression = regExpression.replace(">", ">\w+)")
		return regExpression


class ExpressionFactory:

	def __init__(self):
		numbermatch = re.compile('(?P<float>[0-9.]+)$')
		stringmatch = re.compile('\"(?P<string>.+)\"$')
		tuplematch = re.compile('\(\s*(?P<number1>[0-9.]+)\s*,\s*(?P<number2>[0-9.]+)\s*\)$')
		regmatch = re.compile('\<(?P<reg>.+)\>$')
		self.matchlist = [(numbermatch, NumberExpression), (stringmatch, StringExpression), (tuplematch, TupleExpression), (regmatch, RegExpression)]
		
	def getExpression(self, value):
		for m in self.matchlist:
			match = m[0].match(value)
			if match != None:
				return m[1](value, match)

	
class ConfigParser:
	
	def __init__(self, configfilename):
		self.configfilename = configfilename

	def setMasterdata(self, masterdata):
		self.masterdata = masterdata

	def parse(self):
		self.masterdata.set("ConfigFile", self.configfilename)
		self.masterdata.set("Caller", self.masterdata.caller)
		configExpression	= re.compile('\[(?P<configparagraph>.+)\]$')									#[<configparagraph>]												#<<regular expression group>>
		configparagraph = None
		configfile = open(self.configfilename, 'r')
		for line in configfile:
			uncommentedline = line.split('#', 1)[0].strip()
			if uncommentedline == '':
				continue
			configmatch = configExpression.match(uncommentedline)
			if configmatch != None:
				configparagraph = configmatch.group('configparagraph')
				continue
			formattedline = uncommentedline.split('=', 1)
			if len(formattedline) == 1:
				raise Exception("Configuration file has a line that's not of the form <key>=<value>: " + line)
			if configparagraph == self.masterdata.get("Caller") or configparagraph == "all":
				key		= formattedline[0].strip()
				value	= formattedline[1].strip()
				factory = ExpressionFactory()
				expression = factory.getExpression(value)
				self.masterdata.set(key, expression.getValue())
		configfile.close()

