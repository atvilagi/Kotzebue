function ZVector= returnZVector(x,y,z)

 cellsize=1;
 minx=min(x);
 maxx=max(x);
 miny=min(y);
 maxy=max(y);

 xi=(minx:cellsize:maxx);
 yi=(miny:cellsize:maxy);
 [X,Y]=meshgrid(xi,yi);
 [m,n]=size(X);

 %populate the grid using gridcell averaging
 xind=floor((x-minx)./cellsize)+1;
 yind=floor((y-miny)./cellsize)+1;

 zind=unique([yind,xind],'rows');


 ZVector=ones(m,n).*NaN;
 h = waitbar(0,'Please wait...'); 


 for k=1:length(zind)
     
     ind=find(xind==zind(k,2) &...
         yind==zind(k,1)==1);
     
     ZVector(zind(k,1),zind(k,2))=mean(z(ind));
     
     waitbar(k/length(zind),h,{'Populating Grid.';...
         sprintf('%.0f Percent Complete...',...
         (k/length(zind))*100)})
 end
 close(h)