
# Para evitar tecnicas de fingerprint
#------------------------------------------------------------------------------
class AntiFingerPrint(object):
	""""""

	#----------------------------------------------------------------------
	def process_response(self, request, response):
		# Agregamos el X-Powered-By de asp.net
		response["Server"]           = "Microsoft-HTTPAPI/2.0"
		response["X-AspNet-Version"] = "4.6.1-r2921 beta"
		response["X-Powered-By"]     = "ASP.NET"

		return response



