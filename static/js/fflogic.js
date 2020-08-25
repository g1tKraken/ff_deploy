// Creating map object


wh = [38.896059, -77.036679];
start = [38.942707,-96.245576];

dd = 0.333 //default distance ome mile
gapi = ''

var myMap = L.map("map", {
  center: start,
  zoom: 4
});

// Adding tile layer
L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
  attribution: "© <a href='https://www.mapbox.com/about/maps/'>Mapbox</a> © <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>",
  tileSize: 512,
  maxZoom: 18,
  zoomOffset: -1,
  id: "mapbox/light-v9",
  accessToken: gapi
}).addTo(myMap);

var cal_bearing = function (lt1,ln1,lt2,ln2) {
    
    y = Math.sin(ln2-ln1) * Math.cos(lt2);
    x = Math.cos(lt1)*Math.sin(lt2) - Math.sin(lt1)*Math.cos(lt2)*Math.cos(ln2-ln1);
    degs = Math.atan2(y, x);
    brng = (degs * 180/Math.PI + 360) % 360; // in degrees`
    //rads = brng * (Math.pow(Math.PI,2)/Math.pow(108,2))
    rads = (brng/1) * (Math.PI/180)
    return rads;
}


function placeMarker(iconLoc, imagePath){
  let x = L.icon({
    iconUrl: imagePath,

    iconSize:     [38, 38], // size of the icon
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
  });

  L.marker(iconLoc, {icon: x}).addTo(myMap);
}

myMap.on("contextmenu", function(event) {
  ll_split = event.latlng.toString().replace('LatLng(','').replace(')','').split(", ");
  var mypinpull = {};
  mypinpull.lat = ll_split[0],
  mypinpull.lon = ll_split[1],
  mypinpull.key = [dijit.byId('where').value]
  //mypinpull.key = ['steak', 'pizza', 'coffee']
  pull_data(mypinpull);
//  checkmark(ll_split);
});

//console.log(`map coordinates: ${event.latlng.toString()}`);
  
  var checkmark = function (packet) {
      console.log(`!!  checkmark coordinates: ${packet}`);
     // new_ll = packet.latlng;
    //L.marker(new_ll).addTo(myMap);

    //console.log(`var new_ll validate as: ${typeof(new_ll)} :[${new_ll}]`);
    //ll_split = new_ll.toString().replace('LatLng(','').replace(')','').split(", ");

    //console.log(`center point coordinates: ${typeof(ll_split)} :[${ll_split}]`);
    //console.log(`center point coordinates: ${ll_split}`);
    //my_bearing = cal_bearing(wh[0],wh[1], ll_split[0],ll_split[1]);

    var hicoords = getpoint(packet[0],packet[1],dd,315);
    //L.marker(hicoords).addTo(myMap);
    
    var lowcoords = getpoint(packet[0],packet[1],dd,135);
    //console.log(`bounding box: ${hicoords} ${lowcoords}`)
    //L.marker(lowcoords).addTo(myMap);

    L.polygon([
        hicoords,
        [hicoords[0],lowcoords[1]],
        lowcoords,
        [lowcoords[0], hicoords[1]]
      ], {
        color: "#F84D4D",
        fillColor: "#F84D4D",
        fillOpacity: 0.01
      }).addTo(myMap);

 
      for(var key in markerdata){
        if(markerdata.hasOwnProperty(key)){
          //console.log(`checking marker [${markerdata[key].location}] for position`);
          if((markerdata[key].lat <= hicoords[0]) && (markerdata[key].lat >= lowcoords[0]) && (markerdata[key].lon <= lowcoords[0]) && (markerdata[key].lon >= hicoords[1]))
          {
            console.log(`!!      Placing marker in range`);
            L.marker(markerdata[key].location).bindPopup(markerdata[key].popuptxt).addTo(myMap);
            delete markerdata[key];
          }else
          {
            //console.log(`marker out of range`);
          }
        }
      }
    }
      

    //console.log(`my bearing: ${my_bearing}`);
    //console.log(`starting: ${wh}`);
    //console.log(`to: ${event.latlng.toString().replace('LatLng(','').replace(')','')}`);

    //markertype
    //placeMarker([ll_split[0],ll_split[1]],"static/icons/star.png");
    
    
    //send from here: (ll_split[0],ll_split[1]]
    
    
    //placeMarker([ll_split[0],ll_split[1]],"static/icons/restaurant-vegan.png");
    //.bindPopup("Original Marker");
 

  //L.marker(wh).addTo(myMap);


var getpoint = function (Ltin,Lnin,dist,brng) {
        R = 6378.1 //Radius of the Earth
        brngrad = ((brng * Math.PI/180 + 360) % 360); //bearing converted to radians
        d = dist * 1.609344 //# = 1 * 1.609344 

        ltr = Ltin * Math.PI/180 //Current lat point converted to radians
        lnr = Lnin * Math.PI/180 //Current long point converted to radians

        lat2 = Math.asin(Math.sin(ltr)*Math.cos(d/R) + Math.cos(ltr)*Math.sin(d/R)*Math.cos(brngrad));
        lon2 = lnr + Math.atan2(Math.sin(brngrad)*Math.sin(d/R)* Math.cos(ltr), Math.cos(d/R)-Math.sin(ltr)*Math.sin(lat2));

        lat_out = lat2 * 180 / Math.PI
        lon_out = lon2 * 180 / Math.PI

        return [lat_out, lon_out]
}


// var bearingrads315 = ((315 * Math.PI/180 + 360) % 360); // in degrees`
// var bearingrads135 = ((135 * Math.PI/180 + 360) % 360); // in degrees`
// var bearingrads90 = ((90 * Math.PI/180 + 360) % 360); // in degrees`

// console.log(`get my bearings 315: ${bearingrads315} 135: ${bearingrads135} 90 : ${bearingrads90}`);

//my_bearing = cal_bearing(wh[0],wh[1], 38.926398, -77.036493);
//console.log(`my bearing: ${my_bearing}`);
