var logTimeOut;
var _t = openerp._t;

function getResults (result) {
    console.log(result); // to see which data come from server
}

function attendance_data_loop(id) {
    openerp.jsonRpc('/longpolling/poll','call',
    {
        "channels":["attendance"],
        "last":id
    }).then(function(r){
        for(i=0; i<r.length; i++){
            if(Math.floor(r[i].message) == r[i].message && $.isNumeric(r[i].message))
                get_attendance(r[i].message);
            else
                continue;
        }
        if(r.length>0)
            attendance_data_loop(r[r.length-1].id);
        else
            attendance_data_loop(id);
        }, function(r) {
            setTimeout(function() {
                attendance_data_loop(id);
            }, 5000);
        }
    )
};
attendance_data_loop(0);

//http://www.deadosaurus.com/detect-a-usb-barcode-scanner-with-javascript
$(document).ready(function() {
    var pressed = false;
    var chars = [];
    $(window).keypress(function(e) {
        if (e.which >= 48 && e.which <= 57) {
            chars.push(String.fromCharCode(e.which));
        }
        console.log(e.which + ":" + chars.join("|"));
        if (pressed == false) {
            setTimeout(function(){
                if (chars.length >= 10) {
                    var barcode = chars.join("");
                    console.log("Barcode Scanned: " + barcode);
                    employee_id(barcode);
                }
                chars = [];
                pressed = false;
            },500);
        }
        pressed = true;
    });
    //~ time_out.query(["key"]).filter([["key", "=", "terminal_timeout"]])
    //~ .then(function(result){
        //~ console.log(result);
    //~ })
});

function employee_id(rfid){
    if (rfid != "") {
        openerp.jsonRpc("/hr/attendance/employee", 'call', {
            'rfid': rfid,
        }).done(function(data){
            if(data == ""){
                $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Unidentified User") + "</h2>");
                $('#Log_div').delay(15000).fadeOut('slow');
            }
            else
                employee_state(data);
        });
    }
    if ($("#hr_employee").val() != ""){
        employee_state($("#hr_employee").val());
    }
}

function attendance_state_update(data){
    if(data['state'] == "present") {
        $("#hr_employee").val(data['id']);
        $("#login").addClass("hidden");
        $("#logout").removeClass("hidden");
    }
    if(data['state'] == "absent") {
        $("#hr_employee").val(data['id']);
        employee_project(data['id']);
        $("#login").removeClass("hidden");
        $("#logout").addClass("hidden");
    }
}

function attendance_state_reset(id){
    $("#login").addClass("hidden");
    $("#logout").addClass("hidden");
}

function employee_state(id){
    clearContent();
    if (id != "") {
        openerp.jsonRpc("/hr/attendance/state", 'call', {
            'employee': id,
        }).done(function(data){
            attendance_state_update(data);
        });
    }
    else {
        attendance_state_reset(id);
    }
}

function employee_project(id){
    if (id != "")  {
        openerp.jsonRpc("/hr/attendance/employee_project", 'call', {
            'employee': id,
        }).done(function(data){
            if('projects' in data) {
                var html_content = "<select id='hr_employee_project' class='form-control selectpicker dropdown dropdown_attendance' data-style='btn-primary'>";
                html_content += "<option value='' selected='checked'><span>" + _t(" -- No Project -- ") + "</span></option>";
                for(i=0; i<data['projects'].length; i++) {
                    html_content += "<option value=" + data['projects'][i].id + ">";
                    html_content += "<span>" + data['projects'][i].name + "</span></option>";
                }
                html_content += "</select>";
                $("#employee_projects").html(html_content);
            }
            else
                $("#employee_projects").empty();
        });
    }
}

function number_employees(){
    openerp.jsonRpc("/hr/attendance/employees_number", 'call', {
    }).done(function(data){
        $("#employees_qty").html("<span>" + data +"</span>");
    });
}

function check_employees(){
    openerp.jsonRpc("/hr/attendance/employees", 'call', {
    }).done(function(data){
        clearContent();
        if(data == "") {
            number_employees();
            $("#employees_list").html("<h2 style='color: #f00;' class='text-center'>" + _t("No User is logged in") +"</h2>");
        }
        else {
            var employee_contect = "";
            $.each( data, function( name, image ) {
                var img = "<img src='/hr_attendance_terminal/static/src/img/icon-user.png' style='width: 64px; height: 64px; margin: auto; display: block;'/>";
                if (image !== null)
                    img = "<img src='data:image/png;base64," + image + "' style='margin: auto; display: block;'/>";
                employee_contect += "<div class='col-md-2 col-sm-2 col-xs-2'>" + img + "<p class='text-center'>" + name + "</p></div>"
            });
            number_employees();
            $("#employees_list").html(employee_contect);
        }
        logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
    });
}

/* Come and Go */
function come_and_go(){
    console.log('come_and_go ' + new Date());
	openerp.jsonRpc("/hr/attendance/come_and_go", 'call', {
		'employee_id': $("#hr_employee").val(),
		'project_id': $("#hr_employee_project").val(),
    }).done(function(data){
        if (data != undefined) {
            clearContent();
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + data +"</h2>");
            logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
        }
    });
}

function get_attendance(id){
    openerp.jsonRpc("/hr/attendance/" + id, 'call', {
        }).done(function(data){
            $("#login").addClass("hidden");
            $("#logout").addClass("hidden");
            $("#attendance_div").load(document.URL +  " #attendance_div");
            clearContent();
            if (data.employee.img !== null)
                $("#employee_image").html("<img src='data:image/png;base64," + data.employee.img + "'/>");
            if (data.employee.img === null)
                $("#employee_image").html("<img src='/hr_attendance_terminal/static/src/img/icon-user.png'/>");
            if (data.attendance.action === 'sign_in') {
                $("#employee_message").html("<h2>" + _t("Welcome!") + "</h2><h2>" + data.employee.name +"</h2>");
                number_employees();
            }
            if (data.attendance.action === 'sign_out'){
                var workedHour = 0;
                var workedMinute = 0;

                if (data.attendance.worked_hours != false) {
                    workedHour = hour2HourMinute(data.attendance.worked_hours)[0];
                    workedMinute = hour2HourMinute(data.attendance.worked_hours)[1];
                }
                $("#employee_message").html("<h2>" + _t("Goodbye!") + "</h2><h2>" + data.employee.name +"</h2>");
                $("#employee_worked_hour").html("<h4><strong>" + _t("Worked Hours") + ": </strong>" + workedHour + _t(" hours and ") + Math.round(workedMinute) + _t(" minutes") + "</h4>");
                if(data.attendance.work_time === 'flex'){
                    $("#employee_flex_time").html("<h4><strong>" + _t("Flex Time") + ": </strong>" + Math.round(data.attendance.flextime) + _t(" minutes") + "</h4><h4 id=\"flextime_total_" + id + "\"><strong>" + _t("Flex Time Bank") + ": </strong></h4>");
                    openerp.jsonRpc("/hr/attendance/flextotal/" + id, 'call', {
                        }).done(function(data){
                            $("#flextime_total_" + id).html("<strong>" + _t("Flex Time Bank") + ": </strong>" + Math.round(data.flextime_total) + _t(" minutes"));
                        });
                }
                number_employees();
            }
            logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
        });
}

function hour2HourMinute(hour) {
    var hour_minute = new Array(2);
    hour_minute[0] = Math.floor(hour);
    hour_minute[1] = hour > 0 ? Math.floor(hour % 1 * 60.0) : -Math.floor(Math.abs(hour) % 1 * 60.0);
    return hour_minute;
}

function clearContent(){
    $("#employees_list").empty();
    $("#employee_image").empty();
    $("#employee_message").empty();
    $("#employee_message_error").empty();
    $("#employee_worked_hour").empty();
    $("#employee_flex_time").empty();
    $("#employee_time_bank").empty();
    $('#Log_div').css("display", "unset");
    $('#Log_div').stop();
    clearTimeout(logTimeOut);
}

$('#Log_div').click(function () {
    clearContent();
    $(this).css("display", "none");
});

function clock() {
    var today = new Date();
    var year = today.getFullYear();
    var month = today.getMonth() + 1;
    var day = today.getDate();
    var week_day = today.getDay();
    var hour = today.getHours();
    var minute = today.getMinutes();
    //var second = today.getSeconds();
    minute = checkTime(minute);
    //second = checkTime(second);
    $("#time").text(hour + ":" + minute);
    //~ $("#week_day_d").text(getWeekDay(week_day) + " den " + day);
    //~ $("#week_day_m_y").text(getMonth(month) + " " + year);
    $("#date").text(year + "-" + (month < 10 ? ("0" + month) : month) + "-" + (day < 10 ? ("0" + day) : day));
    var time = setTimeout(clock, 500);
}

function checkTime(i) {
    if (i < 10)
        i = "0" + i;
    return i;
}

function getWeekDay(day) {
    switch(day) {
        case 1: return 'måndagen';
        case 2: return 'tisdagen';
        case 3: return 'onsdagen';
        case 4: return 'torsdagen';
        case 5: return 'fredagen';
        case 6: return 'lördagen';
        case 0: return 'söndagen';
    }
}
function getMonth(month) {
    switch(month) {
        case 1: return 'januari';
        case 2: return 'februari';
        case 3: return 'mars';
        case 4: return 'april';
        case 5: return 'maj';
        case 6: return 'juni';
        case 7: return 'juli';
        case 8: return 'augusti';
        case 9: return 'september';
        case 10: return 'oktober';
        case 11: return 'november';
        case 12: return 'december';
    }
}
