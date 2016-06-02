// track collection
{
  "_id": ObjectId("1234"),
  "mbid": "f1c85e63-1318-46fc-b3b1-e85f40c1cb49", 
  "title": "Bone Machine", 
  "key": "pixies-bonemachine", 
  "img": "http://img2-ak.lst.fm/i/u/174s/94de1db7486d4761c715a96890cccc82.png", 
  "artist": "Pixies"
}

// Show collection
{
  "_id": ObjectId("abcd"),
  "title": "TXFM Drive", 
  "url": "http://www.txfm.ie/drive", 
  "start_time": "15:00", 
  "end_time": "19:00",
  "discription": "Joe takes the sting out of the commute with all the essential information, great interviews and the finest songs on radio",
  "image": "http://www.txfm.ie/content/011/images/000001/719_119_pages_11_3_656x500.jpg"
}

// Plays collection
{
  "track_id": ObjectId("1234"),
  "show_id": ObjectId("abcd"),
  "station": "TXFM"
  "played_at": "5/30/2016, 3:34:04 PM",
  "now_playing": true
}
