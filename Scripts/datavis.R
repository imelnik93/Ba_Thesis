#loading libraries and functions
library(ggplot2)
library(grid)
qacfplot=function(df){
    ggplot(df) + geom_line(aes(x = lag, y = acf), color = 'blue') + 
    geom_ribbon(aes(x = lag, ymin = lb, ymax = ub), alpha=0.2, fill='blue') + 
    ylim(-0.1, 1)
}
#setting wd and loading df
pathdata='~/Dropbox/Study/Coursework/BaThesis/Data/simdata'
pathgraph='~/Dropbox/Study/Coursework/BaThesis/TeX/graphics'
setwd(pathdata)
constacf <- function(lg, thet, Tavg=50){
    if (lg==0) {return(1)}
    if (lg<Tavg) {return(thet*(1-lg/Tavg))}
    else {return(0)}
}
unifacf <- function(lg, thet, Tavg=50, d=20){
    va <- log(Tavg+d)-log(Tavg-d)+2*d*(1-thet)/(100*thet)
    if (lg==0){return(1)}
    else if ((lg<Tavg-d)){return((log(Tavg+d)-log(Tavg-d)-2*lg*d/(Tavg^2-d^2))/va)}
    else if ((lg>=Tavg-d)&(lg<=Tavg+d)){return((lg/(Tavg+d)-log(lg/(Tavg+d))-1)/va)}
    else {return(0)}
}
dlist=c('c','cth1','u','uth1')
a <- data.frame(mapply(constacf, c(0:90), .7, 50), 
                mapply(constacf, c(0:90), 1, 50),
                mapply(unifacf, c(0:90), .7, 50, 20),
                mapply(unifacf, c(0:90), 1, 50, 20))
colnames(a) <- dlist
for (i in c(1:length(dlist))){
    dname <- dlist[i]
    curdf <- data.frame(read.csv(paste0('acf', dname, '.csv')))
    colnames(curdf)[1] <- 'lag'
    plot <- qacfplot(curdf) + geom_line(aes(x = c(0:90), y = a[, i]))
    ggsave(filename = paste0('acf', dname, '.pdf'), plot, path = pathgraph)
}
