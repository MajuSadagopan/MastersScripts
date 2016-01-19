import flickrapi
import csv

#Maju's api key and secret provided on the flickr api page
api_key = u'f605173d33bea33076eaa7ec9d894e61'
api_secret = u'9976b5b2ab8a1ef3'

#Object to access and query Flickr API as documented on
flickr = flickrapi.FlickrAPI(api_key, api_secret)

# Maju's Yahoo user id needed to log in https://www.flickr.com/services/api/
user_id = '132844550@N06'


#Bounding box for the whole Region of Waterloo
kwBBox = [-80.6397,43.3450,-80.3646,43.5400]

#Total horizontal and vertical distance in degrees
xDist = kwBBox[2] - kwBBox[0]
yDist = kwBBox[3] - kwBBox[1]

#Degrees needed to create new bounding box
xAdd = xDist/2
yAdd = yDist/2


#Loops to create series of bounding boxes to make calls to Flickr API and save them in an array
bboxArray = []
xfirst = kwBBox[0]

while xfirst < kwBBox[2]:
	yfirst = kwBBox[1]
	xSecond = xfirst + xAdd
	while yfirst < kwBBox[3]:
		ySecond = yfirst + yAdd
		bounds = str(xfirst)+','+str(yfirst)+','+str(xSecond)+','+str(ySecond)
		bboxArray.append(bounds)
		yfirst = ySecond
	xfirst = xSecond



#Array containing dictionaries used to write into CSV file
records = []

#Query for photos using flickr API bounding box and min data taken using Jan 1, 2013 Midnight as min date taken (without min date only pics in last 24hrs show), max result per query is 250
pics = flickr.photos.search(min_taken_date=1356998400,bbox = '-80.5467, 43.4126, -80.4119, 43.4682')

for pic in pics.findall('photos'):
	for pi in pic.findall('photo'):
		pic_id = pi.attrib['id']

		photo_info = flickr.photos.getinfo(photo_id = pic_id)

		for phot in photo_info.findall('photo'):
			for t in phot.findall('title'):
				title = t.text
			for d in phot.findall('description'):
				desc = d.text
			
			notestring = ""
			for notes in phot.findall('notes'):
				for note in notes.findall('note'):
					nt = note.text
					notestring = notestring + nt + ', '
			
			tagString = ""
			for tags in phot.findall('tags'):
				for tag in tags.findall('tag'):
					tg = tag.text
					tagString = tagString + tg + ', '

			for piece in phot.findall('location'):
				lon = piece.attrib['longitude']
				lat = piece.attrib['latitude']

			records.append({'title':title,'desc':desc,'tags':tagString, 'notes': notestring, 'lon':lon,'lat':lat})

print records

keys = records[0].keys()

with open('flickr2.csv', 'wb') as output:
	dict_writer = csv.DictWriter(output, keys)
	dict_writer.writeheader()
	dict_writer.writerows(records)

