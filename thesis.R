require("RPostgreSQL")
library("RPostgreSQL")

# loads the PostgreSQL driver
drv <- dbDriver("PostgreSQL")
# creates a connection to the postgres database
# note that "con" will be used later in each connection to the database
# "dbname='ungc_test' user='oliviaunderwood1' host='localhost' "
con <- dbConnect(drv, dbname = "ungc_test", host='localhost', user='oliviaunderwood1')

# check for the cartable
dbExistsTable(con, "ungc")
clist = dbGetQuery(con, 'select distinct country from ungc')
clist

df_postgres <- dbGetQuery(con, "SELECT date_due from UNGC 
                          where date_joined >'2001-01-01'
                          and date_due > '2010-01-01'
                          and country='canada'
                          ;")
year_update <- function(year, cry){
  string = "SELECT count(name) from UNGC 
             where date_joined <= 'y1' 
             and date_due > 'y2'  
             and country='cry'
             limit 20;"
  #and date_due > 'y2'
  string2 <- gsub("y1", year, string)
  string3 <- gsub("y2", year+10000, string2)
  string4 <- gsub('cry', cry, string3)
  return(dbGetQuery(con,  string4))
  #return(string3)
}


df_postgres <- year_update(20010101)
df_postgres
#length(clist[[1]])
#clist[[1]][1]
for(j in 1:length(clist[[1]])){
  country = clist[[1]][j]
  yr = 19950101
  for(i in 1:22){
    print(country)
    df_postgres <- year_update(yr, country)
    print(yr)
    print(df_postgres)
    yr = yr + 10000
  }
}

# Basic Graph of the Data
require(ggplot2)
#ggplot(df_postgres, aes(x = as.factor(cyl), y = mpg, fill = as.factor(cyl))) + 
#  geom_boxplot() + theme_bw()


