odoo.define('hr_staff_ledger.staff_ledger', function (require) {
	//~ "use strict";
	var ajax = require('web.ajax');
	
function getLocation() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(showLocation, showError);
	} else {
		x.innerHTML = "Geolocation is not supported by this browser."; 
	}
}


function showLocation(position) {
	var lat = "";
	var lon = "";
	lat = position.coords.latitude;
	lon = position.coords.longitude;
	
	if (lat != "") {
		$("input#latitude_in").val(lat);
	}
	if (lon != "") {
		$("input#longitude_in").val(lon);
	}
	
	
	ajax.jsonRpc("/staffledger/closest_pos", 'call', {'lat': lat, 'long': lon, 'default_location': $("input[name='location']").val()}).then( function (res) { 
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


function detectDevice() {
	var device = navigator.userAgent.toLowerCase();
	
	if (/mobile|iemobile|windows phone|windows mobile|lumia|android|webos|iphone|ipod|blackberry|playbook|bb10|opera mini|\bcrmo\/|opera mobi/i.test(device)  ) {
		myDevice = "Smartphone";
		$("input#device").val(myDevice);
	}
	
	else if ( /tablet|ipad/i.test(device) && window.innerWidth <= 1280 && window.innerHeight >= 800) {
		myDevice = "Tablet";
		$("input#device").val(myDevice);
	}
	
	else {
		myDevice = "Computer";
		$("input#device").val(myDevice);
	}
	
}

//~ function measure(lat1, lon1, lat2, lon2){  // generally used geo measurement function
    //~ var R = 6378.137; // Radius of earth in KM
    //~ var dLat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180;
    //~ var dLon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180;
    //~ var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    //~ Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    //~ Math.sin(dLon/2) * Math.sin(dLon/2);
    //~ var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    //~ var d = R * c;
    //~ return d * 1000; // meters
//~ }


$(document).ready(function(){
	detectDevice();
	getLocation();
	});
});


