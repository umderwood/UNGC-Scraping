require("RPostgreSQL")
library("RPostgreSQL")

# loads the PostgreSQL driver
drv = dbDriver("PostgreSQL")
# creates a connection to the postgres database
# note that "con" will be used later in each connection to the database
# "dbname='ungc_test' user='oliviaunderwood1' host='localhost' "
#con = dbConnect(drv, dbname = "ungc_test", host='localhost', user='oliviaunderwood1')
con = dbConnect(drv, dbname = "ungc_test", host='localhost', user='ducttapecreator')

# check for the cartable
dbExistsTable(con, "ungc")

# list of countries present in the UNGC table
clist = dbGetQuery(con, 'select distinct country from ungc')
# clist

# Testing the date comps and stuff
# df_postgres = dbGetQuery(con, "SELECT date_due from UNGC 
#                           where date_joined >'2001-01-01'
#                           and date_due > '2010-01-01'
#                           and country='canada'
#                           ;")

# simple fxn to build data.frame
year_total_count = function(year, cry){
  string = "SELECT count(name) as entities, count(distinct sector) as sectors, count(distinct org_type) as orgs from UNGC 
             where date_joined <= 'y1' 
             and date_due > 'y2'  
             and country='cry'
             limit 20;"

  string = gsub("y1", year, string)
  string = gsub("y2", year+10000, string)
  string = gsub('cry', cry, string)
  return(dbGetQuery(con,  string))
}

# ISO 8601 seems to work best, no ambiguity and we can add to it w/o date casting
# test year_update
df_postgres = year_total_count(20010101, 'canada')
df_postgres
summary(df_postgres)
# R indexing is weird.
# length(clist[[1]])
clist[[1]][1]

# empty data.frame construction
Country = character()
Year = as.Date(character())
Firms = numeric()
Sectors = numeric()
Types = numeric()
df = data.frame(c(Country, Year, Firms, Sectors, Types))
df
df_postgres[[2]]
df_postgres[[1]]
# Again, weird. starts at 1, heathens. Iterate through country list, saving # of active members each year bt 1995 and 2016
for(j in 1:10){#length(clist[[1]])){
  cry = clist[[1]][j]
  yr = 19950101
  for(i in 1:22){
    #print(country)
    df_postgres = year_total_count(yr, cry)
    print(yr)
    df = rbind(df, c(cry, yr, df_postgres[[1]], df_postgres[[2]], df_postgres[[3]]))
    #print(df_postgres)
    yr = yr + 10000
  }
}
summary(df)
df
