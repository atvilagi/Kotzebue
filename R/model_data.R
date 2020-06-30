
library(tidyr)
library(dplyr)
library(lme4)
library(ggplot2)
library(mgcv)
setwd("E:\\PUMA\\fuelmeter-tools\\R")
data <-read.csv("..\\data\\text\\multiStoveInput.csv", header=TRUE)
data$gpf = data$fuel/data$area
data <- data[data$fuel>0,] #this should not be needed because we should filter negative values long before this

makeFuelCostPrediction<-function(data){
  predictDf <-data.frame('outdoorT' = seq(-40,50,1))

  # glmmResult <- glmer(formula = gpf ~ indoorT + outdoorT | stove,
  #                   data = data, family=gaussian(link="identity"))
  # #gammResult <-gamm(formula = gpf ~ s(indoorT) + outdoorT, random=list(stove=~1), data = data, family=gaussian(link="identity"))
  gammResult <-gamm(formula = log(gpf) ~ s(indoorT) + outdoorT, random=list(stove=~1), data = data, family=gaussian(link="identity"))

  stoves<-unique(data$stove)

  for (s in stoves){
    print(s)
    stoveArea = min(data$area[data$stove==s])
    predictable <-predictDf
    predictable$stove = s
    indoorT <- quantile(data$indoorT[data$stove == s], na.rm =TRUE)
    predictable$indoorT<-indoorT[1]
    tmp <- predictable
    for (i in 2:4){
      tmp$indoorT<-indoorT[i]
      predictable <- rbind(predictable,tmp)}
    
    # outcome <- predict(glmmResult,predictable, se.fit=TRUE)
    outcome2 <-predict(gammResult$gam,predictable, se.fit=TRUE)
    
    # outcome<-cbind(outcome,predictable)
    # outcome$upr<-outcome$fit + (2*outcome$se.fit)
    # outcome$lwr<-outcome$fit - (2*outcome$se.fit)
    
    outcome2<-cbind(outcome2,predictable)
    outcome2$upr<-outcome2$fit + (2*outcome2$se.fit)
    outcome2$lwr<-outcome2$fit - (2*outcome2$se.fit)
    
    # outcome$fuel <- outcome$fit * stoveArea
    outcome2$fuel <-exp(outcome2$fit) * stoveArea
    outcome2$upr <- exp(outcome2$upr) * stoveArea
    outcome2$lwr <- exp(outcome2$lwr) * stoveArea
    # makePlot(outcome,s)
    print(paste("starting to plot",s))
    makePlot(outcome2,s,FALSE)
  }
}
  

makePlot<-function(dat,stove,glmm){
  print(paste("plotting",stove))
  #ggplot(data=outcome, aes(y=fuel, x=outdoorT)) + geom_line(aes(colour=indoorT))
  if (glmm){
    png(paste(stove,"glmm.png",sep=""))
  }else{
    png(paste(stove,"gamm.png",sep="")) 
  }
  
  dat$fact <-as.factor(round(dat$indoorT,0))
  dat$cost <- dat$fuel * 3.50
  dat$upr <- dat$upr * 3.5
  dat$lwr <- dat$lwr * 3.5
  quants <- unique(dat$fact)
  p<-ggplot(data=dat, aes(y=cost, x=outdoorT)) + geom_line(aes(colour=fact), size=1.5) + geom_ribbon(aes(ymin=lwr,ymax=upr,  alpha=0.1, fill = fact), linetype = 1,alpha=0.2) + scale_fill_manual(values=c("#2ECC71", "#E67E22", "#3498DB", "#9B59B6")) +
  scale_color_manual(values=c("#2ECC71", "#E67E22", "#3498DB", "#9B59B6")) +

 
    
  #p + theme(legend.title = element_blank(), legend.title.align=0.5, plot.title= element_text(hjust = 0.5))
  labs(fill= expression(paste("      Indoor \nTemperature\n       ",degree,"F")), colour= expression(paste("      Indoor \nTemperature\n       ",degree,"F")) ,
           x= expression(paste("Outside Temperature ",degree,"F")),
      y="Cost per Day ($)") +
  scale_x_continuous(breaks = round(seq(min(dat$outdoorT), max(dat$outdoorT), by = 10),0)) +
  theme(plot.title= element_text(hjust = 0.5),legend.title.align=0.5)

  print(p)
  dev.off()

}

makeFuelCostPrediction(data)