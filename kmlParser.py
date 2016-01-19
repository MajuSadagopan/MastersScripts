# Import csv, regex and XML libraries
import re
import csv
from xml.etree.ElementTree import ElementTree

# Use ElementTree to parse KML file (in same folder as script)
tree = ElementTree()
tree.parse("c_remarks_KW.kml")
root = tree.getroot()

# Array to store dictionaries as rows, array is stored as CSV
doc = []

# For loop to parse through each Place element named 'Placemark' in kml
for place in root.findall('Placemark'):
	
	#Dictionary for each row
	row = {}

	#For loop to extract XY coordinates from the nested 'coordinate' tag
	for point in place.findall('Point'):
		cords = point.find('coordinates').text
		lang = cords.split(',')[0]
		lat = cords.split(',')[1]
		row['lat'] = lat
		row['long'] = lang

	# For loop to extract 'description' info from the same tag
	for desc in place.findall('description'):
		popup = desc.text
		popd = re.search(r"<br>((.|\n)*?)<br>", popup)
		dsc = popd.group(1)
		dsc = re.sub(r'<div>((.|\n)*?)<\/div>','IMG',dsc)
		#dsc = dsc.replace("<a href=''></a>", '')
		row['dsc'] = dsc

	#Append row dictionary to array
	doc.append(row)

# With open specifies csv file name and wb specifies writeback, dictionary keys are used as headers
with open('communityOutputs.csv','wb') as output:
	dict_writer = csv.DictWriter(output,doc[0].keys())
	dict_writer.writeheader()
	dict_writer.writerows(doc)

print "DONE!"