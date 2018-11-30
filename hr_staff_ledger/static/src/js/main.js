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



$(document).ready(function(){
	detectDevice();
	getLocation();
	$('.btn-staffledger').click(function(){
        window.location=this.getAttribute("href");
        return false
    } );
    
	
});

});

