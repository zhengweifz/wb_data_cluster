con <- file('r_message.txt')
sink(con)
sink(con, type="message")
library(RColorBrewer)
library(rgdal)
library(ggplot2)
library(plyr)
library(dplyr)
library(scales)
library(maptools)
library(WDI)
gpclibPermit()
options(warn=-1)

plot_map <- function(wb_data, file_name){
  #Given a world bank R data frame, plot the map
  # read country map
  wmap <- readOGR(dsn=".", layer="ne_110m_land")
  wmap_robin <- spTransform(wmap, CRS("+proj=robin"))
  wmap_robin_df <- fortify(wmap_robin)
  theme_opts <- list(theme(panel.grid.minor = element_blank(),
                           panel.grid.major = element_blank(),
                           panel.background = element_blank(),
                           plot.background = element_rect(fill="white"),
                           panel.border = element_blank(),
                           axis.line = element_blank(),
                           axis.text.x = element_blank(),
                           axis.text.y = element_blank(),
                           axis.ticks = element_blank(),
                           axis.title.x = element_blank(),
                           axis.title.y = element_blank(),
                           plot.title = element_text(size=22)))
  wmap_countries <- readOGR(dsn=".", layer="ne_110m_admin_0_countries") 
  wmap_countries_robin <- spTransform(wmap_countries, CRS("+proj=robin"))
  wmap_countries_robin_df <- fortify(wmap_countries_robin)
  #get more map info
  wmap_countries_robin@data$id <- rownames(wmap_countries_robin@data)
  wmap_countries_robin_df_final <- join(wmap_countries_robin_df, wmap_countries_robin@data, by="id")
  wmap_countries_robin_df_final$iso_a2 = as.character(wmap_countries_robin_df_final$iso_a2)
  final <- left_join(wmap_countries_robin_df_final, wb_data, by="iso_a2")
  
  #
  gg= ggplot(subset(final, !continent == "Antarctica")) + 
    geom_polygon(aes(long, lat, group = group, fill = data_range)) + 
    geom_path(aes(long, lat, group = group), color = "gray94",size=0.3) + 
    scale_fill_brewer("\n", type="seq", palette="YlOrRd", na.value = "grey62") + 
    theme_opts + coord_equal(xlim=c(-13000000,16000000), ylim=c(-6000000,8343004))
  ggsave(filename = file_name, gg, scale=2)
}

plot_poverty <- function(){
  poverty <- WDI(indicator='SI.POV.DDAY', country="all", start=2000, end=2014)
  poverty <- subset(poverty, !is.na(poverty$SI.POV.DDAY))
  poverty <- group_by(poverty, country)
  poverty <- filter(poverty, year == max(year))
  names(poverty)[1] <- "iso_a2"
  legend_range <- c(0,20,40,60,80,100)
  poverty$data_range <- cut(poverty$SI.POV.DDAY, breaks=legend_range, ordered_result=TRUE)
  plot_map(poverty, "poverty.pdf")
}

plot_final5 <- function(){
  final5 <- read.csv("countryvalues.csv", header = FALSE)
  names(final5)[1] <- "iso_a2"
  p <- c(0 ,20 ,40, 60, 80, 100)/100
  legend_range <- quantile(final5$V2, p )
  final5$data_range <- cut(final5$V2, breaks=legend_range, ordered_result=TRUE)
  plot_map(final5, "five_indicators.pdf")
}

