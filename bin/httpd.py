from microWebSrv import MicroWebSrv

mws = MicroWebSrv(routeHandlers=[], port=80, bindIP='0.0.0.0', webPath="/www")
mws.Start(threaded=True)

