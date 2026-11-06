from importlib import import_module

from roadshow import Roadshow, discover_demos


module_demos = discover_demos(import_module("my_app.demos"))
package_demos = Roadshow("my_app").discover()
