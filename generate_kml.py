#!/usr/bin/env python
# -*- coding: utf-8 -*- 

######################################################################################################
### @Author: Dominic Kohler, Flurin Truebner
### Open Data 2016, Universitaet Bern
### Bundesamt fuer Umwelt, Hansueli Pestalozzi
### http://www.bafu.admin.ch/org/organisation/15909/index.html?lang=de
###################################################################################################### 

import csv
import logging as log
import re
from xml.sax.saxutils import escape

log.basicConfig(format='%(levelname)s:%(message)s', level=log.DEBUG)

langs = ['de', 'fr', 'en', 'it']
topics = []
unique_mtopic_inst = []
filename = 'data/bafu/UBD0109_20160517.csv'

# @see: swisstopo, script [1] to transform coordinates from CH1093 to WGS:84
# 		this functions is slightly adapted for purposes of easier parsing the csv input file
#
# 		[1] http://www.swisstopo.admin.ch/internet/swisstopo/en/home/products/software/products/skripts.html
#
def ch_to_wgs_lat(x, y):
	try:
		x = float(x)
		y =float(y)
		y_aux = (y - 600000)/1000000
		x_aux = (x - 200000)/1000000

		lat = 16.9023892 + 3.238272 * x_aux - 0.270978 * pow(y_aux,2) - 0.002528 * pow(x_aux,2) - 0.0447 * pow(y_aux,2) * x_aux - 0.0140 * pow(x_aux,3)
		lat = lat * 100 / 36

		return lat

	except:
		log.error('nan')
		return float('nan')

# @see: swisstopo, script [1] to transform coordinates from CH1093 to WGS:84
# 		this functions is slightly adapted for purposes of easier parsing csv input file
# 		
#		[1] http://www.swisstopo.admin.ch/internet/swisstopo/en/home/products/software/products/skripts.html
#
def ch_to_wgs_lng(x, y):
	try:
		x = float(x)
		y = float(y)
		y_aux = (y - 600000)/1000000
		x_aux = (x - 200000)/1000000

		lng = 2.6779094 + 4.728982 * y_aux + 0.791484 * y_aux * x_aux + 0.1306  * y_aux * pow(x_aux,2) - 0.0436 * pow(y_aux,3); 
		lng = lng * 100/36;
     
		return lng	
		
	except:
		log.error("Could not parse string, check if file has empty values")
		return float('nan')

# @param: 	file_path
#			lang
def get_uniqu_topics(file_path, lang):
	topics = []
	with open(file_path, 'rb') as f:
		reader = csv.DictReader(f)
		for row in reader:
			if ((row[ 'group_maintopic_' + lang ] not in topics)):				
				topics.append(row[ 'group_maintopic_' + lang ])
	f.close()
	return topics

def gen_topic_list(l):
	sorted_topics = topics.sort()
	with open('data/topics_' + l + '.csv', 'w') as f:
		f.write("topic\n")
		for topic in topics:
			f.write(topic + "\n")



# Generating .kml files for every topic
# Furthermore, groups with the same maintopic,belonging to the same institution are aggregate in one placemark.(Otherwise, )
## The complexity of this construct could be reduced at least by O(n),
for lang in langs:
	topics = get_uniqu_topics(filename, lang)
	log.info("Generate file with topics in " + lang + "...");
	gen_topic_list(lang)
	unique_mtopic_inst = [];
	log.info("Create KML files in " + lang + "...")
	for topic in topics:
		t = re.sub(r'\s+', '', topic) # spaces in failename are worst
		with open("data/kml/" + lang + "/" + t+ '.kml', 'w') as d:
			d.write(
					"﻿<kml xmlns=\"http://www.opengis.net/kml/2.2\" " 
					+ "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" " 
					+ "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" " 
					+ "xsi:schemaLocation=\"http://www.opengis.net/kml/2.2 https://developers.google.com/kml/schema/kml22gx.xsd\"> \n" 
					+ "<Document> \n"
					)

			with open(filename, 'rb') as f:
				reader = csv.DictReader(f)
				for row in reader:
					if row[ 'group_maintopic_' + lang  ] == topic:
						if (row[ 'group_maintopic_' + lang ] + " " + row[ 'institution' ] + " " + row[ 'group_xcoord' ] + " " + row[ 'group_ycoord' ]) not in unique_mtopic_inst:
							unique_mtopic_inst.append(row[ 'group_maintopic_de' ] + " " + row[ 'institution' ]+ " " + row[ 'group_xcoord' ] + " " + row[ 'group_ycoord' ])
							d.write(
									"<Placemark> \n" 
									+ "<Style>" 
											+ "<IconStyle> \n" 
													+ "<scale>0.25</scale>" 
													+ "<Icon><href>https://map.geo.admin.ch/1460548321/img/maki/circle-24@2x.png</href><gx:w>48</gx:w><gx:h>48</gx:h>" 
													+ "</Icon><hotSpot x=\"24\" y=\"24\" xunits=\"pixels\" yunits=\"pixels\"/>" 
											+ "</IconStyle>" 
									+ "</Style>" 
									+ "<Point>" 
										+ "<coordinates>"
											+ str(ch_to_wgs_lng((row[ 'group_xcoord' ]) , (row[ 'group_ycoord' ]))) 	# y-coordinate transformed from CH1903 to wgs:84
												+ ","
											 + str(ch_to_wgs_lat((row[ 'group_xcoord' ]), (row[ 'group_ycoord' ])))  	# x-coordinate
										+ "</coordinates>"
									+ "</Point>" 
									+ "<description><![CDATA[ \n" 
									+	"<table>" 
									+		"<tr>")
							if lang == "it":
									d.write("<td class=\"cell-left\">Istituzione</td>")
							else:
								d.write("<td class=\"cell-left\">Institution </td>")
							d.write(
										"<td class=\"cell-leftr\">" + str(row[ 'institution' ]) + "</td>"
									+		"<tr>\n"
									+		"<tr>"
									+			"<td><span class=\"icon icon--message\" aria-hidden=\"true\" style=\"padding-left: 15px;\"></td>"
									+ 			"<td>" + row[ 'group_street'] + "</td>"
									+		"</tr>"
									+		"<tr>"
									+			"<td></td>"
									+			"<td>"  + row[ 'group_zip' ] + " " + row[ 'group_city' ] + "</td>"			 		
									+		"</tr> \n"
									+		"<tr>" 
									)
							if lang == "de":
								d.write( 
										"<tr>" 
										+ "<td class=\"cell-left\"> Gruppename </td> </tr>")
							elif lang == "fr":
								d.write( 
										"<tr>" 
										+ "<td class=\"cell-left\"> Nom de groupe </td> </tr>")
							elif lang == "en":
								d.write( 
										"<tr>" 
										+ "<td class=\"cell-left\"> Group name </td> </tr>")
							elif lang == "it":
								d.write(
									"<tr>" 
										+ "<td class=\"cell-left\"> Nome del gruppo </td> </tr>"
									)
								
							
							uniq_grname = []
							
							with open(filename, 'rb') as fu:
								rfu = csv.DictReader(fu)
								for rec in rfu:
									key_set1 = rec[ 'group_maintopic_' + lang ] + " " + rec[ 'institution' ] + rec[ 'group_xcoord' ] + " " + rec[ 'group_ycoord' ]
									key_set2 = row[ 'group_maintopic_' + lang ] + " " + row[ 'institution' ] + row[ 'group_xcoord' ] + " " + row[ 'group_ycoord' ]
									gr1_top = row[ 'group_maintopic_' + lang]
						
									if key_set1 == key_set2 and gr1_top == topic and rec[ 'groupname' ] not in uniq_grname:					
										d.write( 
												 "<tr><td class=\"cell-leftr\">" + escape(rec[ 'groupname' ]) + "</td>" 
										  		+ "<td class=\"cell-leftr\">" + "<p><span class=\"icon icon--external\" aria-hidden=\"true\"></span>" 
										  		+ "<a href=" + rec[ 'group_website' ].strip("/") + "> " + rec[ 'group_website' ] + "</a></p></td>" 
										  + "</tr> \n"
										  )
										
										uniq_grname.append(row[ 'groupname' ])
									
								d.write(
												"</table> ]]>"
											+ "</description>\n" 
										+ "</Placemark> \n") 

			d.write("</Document></kml>")
			d.close()


