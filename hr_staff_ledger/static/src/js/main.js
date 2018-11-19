odoo.define('website.website', function (require) {
	"use strict";
	var ajax = require('web.ajax');
	

function getLocation() {
	"use strict";
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(showLocation, showError);
	} else {
		x.innerHTML = "Geolocation is not supported by this browser."; 
	}
}


function showLocation(position) {
	"use strict";
	var lat;
	var lon;
	lat = position.coords.latitude;
	lon = position.coords.longitude;
	
	ajax.jsonRpc("/staffledger/closest_pos", 'call', {'lat': lat, 'long': lon}).then( function (res) { 
		if (res) {
			$.each($("select[name='location']").find("option"), function(){
				if ($(this).val() == res) {
					 $(this).attr('selected', 'selected');
				}
			});
		} 
	});
	
	var latlon = new google.maps.LatLng(lat, lon);
	var mapholder = document.getElementById("mapholder");
	mapholder.style.height = "240px";
	mapholder.style.width = "240px";
	var myOptions = {
		center: latlon,
		zoom: 15,
		streetViewControl: false,
		fullscreenControl: false,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		mapTypeControl: false,
		navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL}
	};
	var map = new google.maps.Map(document.getElementById("mapholder"), myOptions);
	var marker = new google.maps.Marker({position:latlon,map:map,title:"You are here!"});                 


}


function showError(error) {
	"use strict";
	switch(error.code) {
		case error.PERMISSION_DENIED:
			x.innerHTML="User denied the request for Geolocation.";
			break;
		case error.POSITION_UNAVAILABLE:
			x.innerHTML="Location information is unavailable.";
			break;
		case error.TIMEOUT:
			x.innerHTML="The request to get user location timed out.";
			break;
		case error.UNKNOWN_ERROR:
			x.innerHTML="An unknown error occurred.";
			break;
	}
}


window.onload = getLocation();
window.onload = getCurrentLocation();


$(document).ready(function(){
	
});




});
	
