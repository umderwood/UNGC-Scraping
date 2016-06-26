require 'rubygems'
	require 'nokogiri'
	require 'open-uri'
	
	
	url = 'http://www.pfizer.com/responsibility/working_with_hcp/payments_report.jsp?enPdNm=All&iPageNo=1'
	page = Nokogiri::HTML(open(url))
	# page now contains the HTML that your browser would have read had you visited the url with your browser 
