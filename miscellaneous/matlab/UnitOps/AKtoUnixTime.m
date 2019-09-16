function t=AKtoUnixTime(x)
t=(datenum(x)-datenum(1970,1,1))*60*60*24;