#Seth Lyles
#2016 June 22

from bs4 import BeautifulSoup
import urllib3, certifi, psycopg2, string
from dateutil.parser import parse


def db():
	'''globals are bad, mmkay?'''
	# Use the try if we might not connect to the db
	try:

		# db login info
		connect_str = "dbname='ungc_test' user='ducttapecreator' host='localhost' "

		# use our connection values to establish a connection
		conn = psycopg2.connect(connect_str)
		# create a psycopg2 cursor that can execute queries
		return(conn)
	except Exception as e:
		print("Uh oh, can't connect. Invalid dbname, user or password?")
		print(e)

def fix(stri, fu = 0):
	'''stri to clean for db entry
		db not so good with apostrophes
		get rid of spaces and ., other punctuation too, preventatively
		may cause complications for country ID but postgres doesn't case sensitive'''
	# Python interprets 'None' as None for some reason;
	# 'None' was listed as reason for delisting so script errored out.
	def fux(st):
		return st.replace(" ", "_")
		
	if stri is not None:
		stri = stri.lower()
		stri = "".join(l for l in stri if l not in string.punctuation)
		#stri = stri.replace(" ","_")
		if(fu):
			stri = fux(stri)
		return(stri)
	else:
		return("none")
# comment comment	
def data_getter(url):
	''' Returns the page data from URL '''
	ld = http.request("GET", url)
	sp = BeautifulSoup(ld.data, "lxml")
	return(sp)

def scrape_data(url):
	''' Finds the date that the entity became delisted at URL '''
	sp = data_getter(url)
	# Find all the relevant locations in web page source
	#name, date joined, and date due/delisted are in different locations
	nm = sp.find("header", {"class":"main-content-header"})
	start = sp.find("div", {"class":"company-information-since"})
	ldtext = sp.find("div",  {"class":"company-information-cop-due"})
	othertext = sp.find("div", {"class":"company-information-overview"})
	# all other data is together, so we make list of key and value
	keys = othertext.findAll("dt")
	vals = othertext.findAll("dd")
	
	# clean dates so they are accepted by db
	dd = parse(ldtext.time.string).strftime("%Y/%m/%d")
	dj = parse(start.time.string).strftime("%Y/%m/%d")
	
	# build dict so we can return only one thing
	#d = {'name': fix(nm.h1.string), 'date_due':dd, 'date_joined':dj}
	d = {"name": fix(nm.h1.string), "date_due":dd, "date_joined":dj}
	
	# add rest of data to dict
	for i in range(len(keys)):
		#d[fix(keys[i].string)] = fix(vals[i].string)
		d[fix(keys[i].string, 1)] = fix(vals[i].string)
		
	# return dictionary of keys (name, country, sector, etc.) with assoc. values ("tims_auto", "spain", "manufacturing", etc.)
	return(d)

def add_ungc_table():
	''' Adds the UNGC participants to a database, using a new table called 'active' '''
	# Open a pool manager object; create a socket requiring certificates
	http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

	# First half of URL of search page of participants
	BASE_URL = "https://www.unglobalcompact.org/what-is-gc/participants/search?page="

	# Root page of UNGC, need for links to non-communicating and delisted entities
	UNGC_URL = "https://www.unglobalcompact.org"
	
	# create a new table with columns called name, type, sector, country, and date
	# Fill table with members of UNGC
	# Can add fields to active, noncomm or delisted by looking at status
	
	conn = db()
	cursor = conn.cursor()
	
	fields = ("name", "org_type", "sector", "country", "global_compact_status", "date_joined", "date_due", "employees", "ownership")
	cursor.execute('''drop table if exists UNGC;''')
	cursor.execute("CREATE TABLE UNGC (%s varchar(250), %s varchar(150), %s varchar(150), %s varchar(150), %s varchar(150), %s date, %s date, %s int, %s varchar(150));" % fields)
	# The half of active link after page number
	THE_REST = 	"&search[keywords]=&search[per_page]=50&search[sort_direction]=asc&search[sort_field]=&utf8="
	
	# Is there a way to know how many pages without going to site?
	# Maybe do while loop, checking for 50 things? Probably not worth it, but could be more elegant
	
	for i in range(444): #444 as of 7 Aug 2016
	
		# observe which page we're parsing
		print(i)
		
		# get data from ith page
		soup = data_getter(BASE_URL + str(i+1) + THE_REST)
		
		# get name tags, for links are stored there
		nf = soup.findAll("th", "name")
		
		# build list of links to get important dates, # employees, etc.
		links = [UNGC_URL + th.a["href"] for th in nf[1:]]
		
		# the list of dates for those delistings
		
		for link in links:
			data = ()
			d = scrape_data(link)
			
			# make new tuple of dictionary values
			# Do we really need a dictionary here? should be able to use a list so we don't have to build anything...
			for f in fields:
				data += (d[f], )
			
			#  ('name', 'org_type', 'sector', 'country', 'global_compact_status', 'date_joined', 'date_due', 'employees', 'ownership')
			# postgres wasn't accepting the string unless it was done in 2 pieces, parentheses maybe?
			cmd0 = "INSERT INTO UNGC (%s, %s, %s, %s, %s, %s, %s, %s, %s) " % fields
			cmd1 = "VALUES (%r, %r, %r, %r, %r, %r, %r, %s, %r)" % data
			cmd = cmd0 + cmd1	
			#cmd = cmd.replace('"', "'")
			# Add to our db:
			try:
				cursor.execute(cmd)
			except psycopg2.ProgrammingError: # I think... this is because SQL differentiates bt " and '
				print('ah, piss')
				return(1)
		
		# make sure that we're getting the same number of each of these; names had same tag in headings and content of table
		# print(len(names), len(types), len(sectors), len(countries), len(dates))
		# print(names[0], types[0], sectors[0], countries[0], dates[0])
		

		# Save db
		conn.commit()
		conn.close()


def add_worldbank_table():
	f = open("/Downloads/WGI_csv/WGI_Data.csv", 'r')
	fields = ("country", "ind_code", "year", "val")
	cursor.execute("CREATE TABLE WGI (%s varchar(250), %s varchar(150), %s date, %s float);" % fields)
	first = f.readline()
	for line in f:
		for i, year in enumerate(first[4:]):
			entry = (line[0], line[3], year, line[i+4])
		
		cursor.execute('INSERT INTO WGI (%s, %s, %s, %s) VALUES (%s, %s, %s, %s);' % entry)
	f.close()

def count_by_years_table():
	
	# make a list of countries in the UNGC list
	clist = []
	# Fill cursor buffer
	cursor.execute('select distinct country from ungc')
	# dump cursor buffer into list
	for country in cursor:
		# country is a tuple, like ('country', ) so it needs the index
		clist.append(country[0])
		
	# let's just start a new table
	cursor.execute('drop table if exists BY_COUNTRY;')
	cursor.execute("CREATE TABLE BY_COUNTRY (Country CHAR(250), Date DATE, Firms INT, Sectors INT, Types INT, CPI FLOAT);")

	def year_total_count(year, cry):
		st = "SELECT count(name) as entities, count(distinct sector) as sectors, count(distinct org_type) as orgs from UNGC where date_joined <= '%s' and date_due > '%s' and country='%s' limit 20;" % (year, year+10000, country)
		
		return(cursor.execute(st))
	
	for j in range(len(clist)):
		cry = clist[j]
		yr = 19950101
		for i in range(1,22):
			#print(country)
			df_postgres = year_total_count(yr, cry)[0]
			print(yr)
			#print(df_postgres)
			yr = yr + 10000

	
# show that we have stuff in db:
# cursor.execute("""SELECT date_joined
# 					 from ungc
# 					 where date_joined < '2014/01/01'
# 					 limit 50;""")
#cs = cursor.fetchall()
#for c in cs:
#	print(c)

def add_CPI_table():
	''' Adds CPI data from Transparency International. Not country rank though, not really useful for anything '''
	# CPI_Final has the CPI data from TI, with 0 instead of blanks, 
	# and countries removed if they have data for fewer than 15 years b/t 1995 and 2015.
	f = open("./CPI_Final.txt", 'r')
	fields = ("country", "year", "val")
	conn = db()
	cursor = conn.cursor()
	# we just make year int because m/d doesn't matter
	cursor.execute("CREATE TABLE CPI (%s varchar(250), %s int, %s float);" % fields)
	years = f.readline().split()
	
	def is_number(s):
		''' is s a number? needed for line_fix '''
		try:
			float(s)
			return True
		except ValueError:
			return False
	def line_fix(line):
		''' dammit costa rica!
		necessary for countries with multiple words '''
		l = line.split('\t')
		i = 0
		c = ""
		while is_number(l[i]) is False:
			c += l[i]
			i += 1
		return([c] + l[i:])
		
	for line in f:
		# clean the line; we want [country, 1995_val, 1996_val, etc] and not [cou, ntry, etc]
		l = line_fix(line)

		country = l[0]
		
		# because the split('\t') leaves \n on the last one...
		l[-1] = l[-1].split()[0]
		
		for i in range(1, len(l)):
			# we only want to add table for years with values
			if l[i] != '0':
				data = (country, years[i-1], l[i])
			
				cmd0 = "INSERT INTO CPI (%s, %s, %s) " % fields
				cmd1 = "VALUES (%r, %r, %r)" % data
				cmd = cmd0 + cmd1	
				# Add to our db:
				cursor.execute(cmd)

	conn.commit()
	cursor.close()
	conn.close()

add_CPI_table()
#def get_category_links(section_url):
    



