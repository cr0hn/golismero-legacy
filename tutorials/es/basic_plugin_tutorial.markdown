---
title: Desarrollo básico de un plugin
layout: master
---

Tutorial básico: Desarrollo de un plugin
========================================

Índice:

1. Qué es un plugin
2. Introducción
3. Tipos de plugins
4. Fases de ejecución
5. Elección del tipo plugin
6. Copiar plantilla
7. Añadir información al plugin
8. Configuración del plugin
9. Tipos de datos
10. Escribiendo el código

*****


1 - Qué es un plugin?
---------------------

En golismero, un plugin es un pequeño programa que realiza un tarea muy específica y puede generar una serie de resultados.

A nivel de código, es una clase de python que hereda de una clase en la que se definen las operaciones permitidas por los plugins.


2 - Introducción
----------------

Crear un plugin de GoLismero es realmente fácil. Solamente tenéis que seguir unos sencillos pasos:

Un plugin consta de dos ficheros: 

- Uno de configuración, que tiene como extensión: `.golismero`
- Otro con el código fuente de plugin, con extensión: `.py`

Para desarrollar un plugin necesitaremos crear los dos y establecer los valores adecuados en cada uno de ellos.

Como ejemplo para este tutorial, vamos a explicar paso a paso como desarrollar el plugin que busca URLs sospechosas (de ahora en adelante `Suspicious`).


3 - Tipos de plugins
--------------------

GoLismero consta de varios tipos de plugins, pero en este tutorial básico solamente nos centraremos en los plugins de **testing**. 

Los plugins de testing son aquellos que realizan la auditorias o las pruebas sobre el sistema que está siendo auditado.


4 - Fases de ejecución
----------------------

Los plugins de testing se ejecutan en etapas o fases. Cada plugin tiene que pertenecer a una **única** de estas fases.

Las fases hacen referencia al momento de ejecución de plugins. Actualmente podemos distinguir varias estas de ejecución:

- **recon**: Fase de reconocimiento. Es la primera en ejecutarse.
- **scan**: Etapa de escaneo y descubrimiento. Es la segunda en ejecutarse. A esta etapa pertenecen los escaneres de puertos y hosts, por ejemplo.
- **attack**: Etapa de ataque. Tercera en ejecutarse. A esta fase pertenecen los analizadores de *XSS* y *SQL Injection*, por ejemplo.
- **intrude**: Se ejecuta después de la fase de ataque. Esta fase es intrusiva. A esta etapa pertenecen plugins que, tras encontrar una vulnerabilidad *SQL Injection* en la etapa de ataque, se encargen de volcar la base de datos.
- **cleanup**: Fase de limpieza. Es la etapa final.

En la carpeta `plugins/testing` se pueden varias carpetas, que corresponden con cada una de las fases existentes.
	
	|- plugins
	   |- testing
	      |- attacks
	      |- cleanup
	      |- post
	      |- recon
	      |- scan

5 - Elección del tipo plugin
----------------------------

En función del tipo de plugin que queramos desarrollar deberemos de elegir una etapa de ejecución u otra.

Si creamos un plugin que realice un escaner de puertos a un determinado destino, deberiamos de añadirlo a la fase de **scan**.

Si creamos un plugin que realice ataques de fuerza bruta de contraseñas, deberíamos de incluirlo en la fase de **attack**.

Para nuestro plugin de ejemplo, `Suspicious`, la fase sería la de **recon**.


6 - Copiar plantilla
--------------------

Copiamos el plugin plantilla, que consta de los ficheros `template.golismero` y `template.py`, al directorio correspondiente al tipo de plugin que queremos desarrollar. Estos ficheros se encuentran el: `test/plugin_test/`

![Template plugin](/images/tutorials/basic_plugin_tutorial/template_plugin.png)

Para nuestro caso, del `Suspicious`, lo copiamos al directorio **recon**.

Renombramos ambos ficheros por en nombre de nuestro plugin, en nuestro caso `suspicious_url.golismero` y `suspicious_url.py`:

![Template plugin rename](/images/tutorials/basic_plugin_tutorial/template_plugin_rename.png)


7 - Añadir información al plugin
--------------------------------

Modificamos los valores del fichero de configuración del plugin, del fichero `suspicious_url.golismero`:

	[Core]
	Name = Suspicious URL
	
	[Documentation]
	Description = Find suspicious words in URLs
	Author = GoLismero project team
	Version = 0.1
	Website = https://github.com/cr0hn/golismero/
	Copyright = Copyright (C) 2011-2013 GoLismero Project
	License = GNU Public License
	
	[Wordlist_middle]
	wordlist = golismero/warning_url.txt
	
	[Wordlist_extensions]
	wordlist = fuzzdb/Discovery/FilenameBruteforce/Extensions.Backup.fuzz.txt



8 - Configuración del plugin
----------------------------

**Lo primero que tendremos que hacer es cambiar el nombre de la clase por el nombre de nuestro plugin.**

Como dijimos al principio, un plugin no es más que una clase de python que ha de implementar unos determinados métodos heredados:

	class SuspiciousURLPlugin(TestingPlugin):
	
		def get_accepted_info(self):
			pass
	
		def recv_info(self, info):
			pass

Como se aprecia, es muy sencillo, puesto que solo tiene 3 métodos, pero para nuestros caso solo explicaremos 2 de ellos:

- **get_accepted_info**: Este método especifica los tipos de datos que el plugin recibe. Explicamos esto con más detalle en el siguiente punto.
- **recv_info**: Aquí es donde realmente iré el código de nuestro plugin. Lo veremos en los puntos siguientes.



9 - Tipos de datos
------------------

Golismero trabaja con tipos de datos, ¿qué es esto? Un tipo de datp puede ser cualquier cosa que almacena cierta información: una URL, un dominio, una página HTML o una dirección de correo electrónico. 

> Puede consultar los tipos de información disponibles en: [Tipos de datos](/api/api/data.html)
   
El motor de golismero es capaz de tratar y distinguir todos los tipos de datos y enviar a los plugins solamente aquellos que el plugin desea recibir. De esta forma el plugin siempre sabrá el tipo de información que recibirá y, por tanto, como procesarla.

Para escecificar los tipos de datos que deseamos recibir en nuestro plugin, debermos de devolver una lista con los mismos:

	def get_accepted_info(self):
		return [BaseUrl]


10 - Escribiendo el código
--------------------------

Por fin llegamos vamos a escribir el código de nuestro plugin. El código de nuestro plugin irá en el método `recv_info`.

Para nuestro caso:

	
	def recv_info(self, info):
        m_url = info.url

        # Check if URL is in scope
        if not is_in_scope(m_url):
            return

        # Load wordlists
        m_wordlist_middle     = WordListAPI().get_wordlist(Config.plugin_extra_config['Wordlist_middle']['wordlist'])
        m_wordlist_extensions = WordListAPI().get_wordlist(Config.plugin_extra_config['Wordlist_extensions']['wordlist'])

        # Results store
        m_results          = []
        m_results_extend   = m_results.extend

        # Add matching keywords at any positions of URL
        m_results_extend([SuspiciousURL(info, x)
                          for x in m_wordlist_middle
                          if x in m_url])

        # Add matching keywords at any positions of URL
        m_results_extend([SuspiciousURL(info, x)
                          for x in m_wordlist_extensions
                          if m_url.endswith(x)])

        return m_results


Como véis, se devuelve un tipo de dato. Para enviar los resultado obtenidos en nuestro plugin, así es como tendremos que hacerlo.

También podéis ver que el plugin usa la función del API para manejar diccionarios (`WordListAPI`). Para ampliar más información sobre cómo utilizar los diccionarios puede consultar: [WordList API](/api/api/text.html#module-golismero.api.text.wordlist_api)
