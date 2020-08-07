//Sidebar
$(document).ready(function () {
  $('#sidebarCollapse').on('click', function () {
      $('#sidebar').toggleClass('active');
      $(this).toggleClass('active');
  });
});


// Map of DC
var myMap = L.map("map", {
  center: [38.9072, -77.0369],
  zoom: 13
});

L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
  attribution: "© <a href='https://www.mapbox.com/about/maps/'>Mapbox</a> © <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> <strong><a href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a></strong>",
  tileSize: 512,
  maxZoom: 18,
  zoomOffset: -1,
  id: "mapbox/light-v9",
  accessToken: API_KEY
}).addTo(myMap);

// Function to pull in markers
function placeMarker(iconLoc, imagePath){
  let x = L.icon({
    iconUrl: imagePath,
  
    iconSize:     [38, 38], // size of the icon
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
  });

  L.marker(iconLoc, {icon: x}).addTo(myMap);
}
// To create an icon and post to map
// var Michelin = L.icon({
//   iconUrl: 'icons/michelin.png',

//   iconSize:     [38, 38],
//   iconAnchor:   [22, 94], 
//   popupAnchor:  [-3, -76] 
// });

// L.marker([37.9072, -77.0369], {icon: Michelin}).addTo(myMap);

placeMarker([38.9072, -77.0369],"icons/star.png")

marker.bindPopup("Original Marker");


