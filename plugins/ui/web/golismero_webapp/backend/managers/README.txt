This package contains files and classes to manage GoLismero and their internal BBDD.

Scheme of that are:

+------+      +--------+           +------------------+
| REST | <--> | Facade | <-->|<--> | GoLismero Bridge |
+------+      +--------+     |     +------------------+
                             |
                             |     +------+
                             |<--> | BBDD |
                                   +------+


Where:
-             REST: REST API frontend (apps.rest_api.views).
-           Facade: Facade interface (backend.managers.golismero_facade).
- GoLismero Bridge: RPC to comunicate with GoLismero (backend.managers.golismero_bridge).
-             BBDD: native django interface to manage databases.