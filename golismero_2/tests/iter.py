

#------------------------------------------------------------------------------
class itero(object):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		self.a = list(xrange(10))
		self.index = -1

	#----------------------------------------------------------------------
	def __iter__(self):
		""""""
		return self

	#----------------------------------------------------------------------
	def next(self):
		""""""
		self.index+=1
		if self.index < len(self.a):
			return self.a[self.index]
		else:
			raise StopIteration


	#----------------------------------------------------------------------
	def hola_get(self):
		""""""
		if not hasattr(self, '_%s__associated_url' % self.__class__.__name__):
			return None
		else:
			return self.__associated_url


	#----------------------------------------------------------------------
	def hola_set(self, value):
		""""""
		self.__associated_url = value

	hola = property(hola_get, hola_set)


from urllib import url