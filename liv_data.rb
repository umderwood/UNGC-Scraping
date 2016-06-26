	# Call Ruby's OpenURI module which gives us a method to 'open' a specified webpage
	require 'open-uri'
	require 'uri'





	# This is the basic address of Pfizer's all-inclusive list. Adding on the iPageNo parameter will get us from page to page.
	FIRST_PAGE = 'https://www.unglobalcompact.org/what-is-gc/participants/search?utf8=✓&search[keywords]=&search[per_page]=50&search[sort_field]=&search[sort_direction]=asc'
	#'https://www.unglobalcompact.org/what-is-gc/participants/search?utf8=✓&search[keywords]=&search[reporting_status][]=active&search[per_page]=50&search[sort_field]=&search[sort_direction]=asc'
	BASE_LIST_URL = 'https://www.unglobalcompact.org/what-is-gc/participants/search?page='			
	THE_REST = 	'&search[keywords]=&search[per_page]=50&search[reporting_status][]=active&search[sort_direction]=asc&search[sort_field]=&utf8='

	LAST_PAGE_NUMBER = 2

	# create a subdirectory called 'TA-list-pages'
	LIST_PAGES_SUBDIR = 'TA-list-pages'

	Dir.mkdir(LIST_PAGES_SUBDIR) unless File.exists?(LIST_PAGES_SUBDIR)

	# So, from 1 to 485, we'll open the same address on Pfizer's site, but change the last number
	
# 	encoded_base = URI.encode(BASE_LIST_URL)
# 	encoded_rest = URI.encode(THE_REST)
# 	URI.parse(encoded_base)
# 	URI.parse(encoded_rest)



	for page_number in 2..LAST_PAGE_NUMBER
		page = open("#{BASE_LIST_URL}#{page_number}#{THE_REST}")

		# create a new file into to which we copy the webpage contents
		# and then write the contents of the downloaded page (with the readlines method) to this
		# new file on our hard drive
		file = File.open("#{LIST_PAGES_SUBDIR}/TA-list-page-#{page_number}.html", 'w')

		# write to this new html file
		file.write(page.readlines)

		# close the file
		file.close

		# the previous three commands could be condensed to:
		# File.open("#{LIST_PAGES_SUBDIR}/pfizer-list-page-#{page_number}.html", 'w'){|f| f.write(page.readlines)}


		puts "Copied page #{page_number}"
		# wait 4 seconds before getting the next page, to not overburden the website.
		sleep 4 
	end
