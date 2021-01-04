library(rgdal)
library(tidyr)
library(sf)
library(raster)
library(sp)
library(dplyr)
library(lubridate)
library(GISTools)


setwd("/Users/tawnamorgan/Documents/puma/fuelmeter-tools/R/Spatial")
data <-read.csv("/Users/tawnamorgan/Documents/puma/fuelmeter-tools/data/text/multiStoveInput.csv", header=TRUE) #
data <- data[!is.na(data$fuel),]
data<-data[data$fuel > 0,]
houses<-unique(data[c("stove","latitude","longitude")])
allStoves <- houses$stove
houses<-houses[houses$stove != "FBK013",] #FBK013 is outside the available prediction area
houses<-houses[houses$stove != "FBK009",] #FBK009 is outside the available prediction area
geo_proj = "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
albers_proj <-  "+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"

spatialHouses<-SpatialPointsDataFrame(
  houses[c("longitude","latitude")],proj4string = CRS(geo_proj),  houses)
albershouses<-spTransform(spatialHouses,CRS(albers_proj))

aspect <- st_read(getwd(), "aoi_pts_aspect")
aspect$POINT_X <- st_coordinates(aspect)[,1]
aspect$POINT_Y <- st_coordinates(aspect)[,2]

elevation <- st_read(getwd(), "aoi_pts_elev")

slope <- st_read(getwd(),"aoi_pts_slope")
bbox = st_bbox(slope)


#read in roads layer
roads<-st_read(getwd(), "FBKRoads")
roads<-st_zm(roads)

e<-extent(albershouses)

e[1] <- e[1] - 1000
e[2] <-e[2] + 1000
e[3] <- e[3] - 1000
e[4] <- e[4] + 1000
select_roads<-  st_crop(roads,e)

r <-raster(xmn=bbox[1]- 25,xmx=bbox[3]+25,ymn=bbox[2]-25,ymx=bbox[4] + 25,crs="+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
res(r)<-50
projection(r) <- "+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"

rslope<-rasterize(as(slope,"Spatial"),r)
relevation<-rasterize(as(elevation,"Spatial"),r)
raspect<-rasterize(as(aspect,"Spatial"),r)

rslope <- crop(rslope,e)
relevation <- crop(relevation,e)
raspect <- crop(raspect,e)

rslope$rad = rslope$RASTERVALU * pi/180
raspect$rad = raspect$RASTERVALU * pi/180
myhillshade<-hillShade(rslope$rad, raspect$rad)
myslope<-raster::extract(rslope, albershouses)
myelevation<-raster::extract(relevation, albershouses)
myaspect<-raster::extract(raspect, albershouses)

houses$slope <-myslope[,3]
houses$elevation <-myelevation[,2]
houses$aspect <-myaspect[,5]
houses$x <- myaspect[,3]
houses$y <- myaspect[,4]

alldata <- merge(data,houses,by="stove")
alldata$gpf <- alldata$fuel / alldata$area
alldata$date <-as.Date(alldata$date)
alldata$month<-month(alldata$date)
winterdata<-alldata[alldata$month %in% c(1,2,3,9,10,11,12),]

#this should already only contain positive gpf values but just in case
winterdata<-winterdata[winterdata$gpf > 0,]
winterdata <- winterdata%>%group_by(stove)%>%summarize(mgpf = mean(gpf),x =mean(x),y =mean(y), aspect =mean(aspect),slope = mean(slope),elevation = mean(elevation))
glmmResult <- glm(log(mgpf) ~ aspect + elevation + y +x, data = winterdata, family=gaussian(link="identity"))

newdata<-data.frame('x' = values(raspect$POINT_X), 'y' = values(raspect$POINT_Y), 'aspect' = values(raspect$rad), 'slope'=values(rslope$rad), 'elevation'=values(relevation$RASTERVALU))
predictedValues <-predict(glmmResult,newdata)

#now plot
newdata$newValues <- exp(predictedValues)
newdata$newValues <-round(newdata$newValues, 4)

#make newdata spatial so we can xtract to an empty raster
spatialLandscape<-SpatialPointsDataFrame(
 newdata[c("x","y")],proj4string = CRS(albers_proj),  newdata[c('x','y','newValues')])

rfuel<-rasterize(spatialLandscape,r)
#plot the study area and average fuel by landscape

for (stove in allStoves){

  png(paste(stove,"spatial_fuel.png", sep = ""),width=800, height=500)
  par(mar=c(0,0,0,4), oma=c(0,4,0,4))
  plot(myhillshade,ylim=c(e[3]-1000,e[4]+ 1000),xlim=c(e[1]-1000,e[2]+1000), axes=FALSE, legend=FALSE,box = FALSE, col = grey(1:100/100))

  plot(rfuel$newValues,ylim=c(e[3]-1000,e[4]+ 1000),xlim=c(e[1]-1000,e[2]+1000), axes=FALSE, box = FALSE, legend=TRUE, legend.args=list(text=expression(paste("gallons per ft"^"2", sep = "")), side=4, font=2, line=4, cex=1),col = rev(heat.colors(5)), add=TRUE, alpha=0.4)
  plot(select_roads$geometry,ylim=c(e[3]-900,e[4]+ 900),xlim=c(e[1]-900,e[2]+900), axes=FALSE, legend=FALSE,box = TRUE, col = "dark grey", add=TRUE )
  if (nrow(albershouses[albershouses$stove == stove,]) > 0){
    plot(albershouses[albershouses$stove == stove,],ylim=c(e[3]-1000,e[4]+ 1000),xlim=c(e[1]-1000,e[2]+1000), add=TRUE, pch=24, cex =2, col="red", bg="blue", lwd=2, box=TRUE)
    }
 map.scale(x=e[2]-10000, y=e[3]+1500, len = 5000, ndivs=2,units="km")
north.arrow(xb=e[2]-3000, yb=e[3]+ 1500, len=300, lab="N", col="black") 
  dev.off()
  }
