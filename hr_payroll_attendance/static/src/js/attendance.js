var logTimeOut;

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
            attendance_data_loop(id);
        }
    )
};
attendance_data_loop(0);

function employee_state(){
    if ($("#hr_employee").val() != '') {
        openerp.jsonRpc("/hr/attendance/report", 'call', {
            'employee': $("#hr_employee").val(),
        }).done(function(data){
            if(data == "present") {
                $("#login").addClass("hidden");
                $("#logout").removeClass("hidden");
            }
            if(data == "absent") {
                $("#login").removeClass("hidden");
                $("#logout").addClass("hidden");
            }
        });
    }
    else {
        $("#login").addClass("hidden");
        $("#logout").addClass("hidden");
    }
}

/* Come and Go */
function come_and_go(){
openerp.jsonRpc("/hr/attendance/come_and_go", 'call', {
    'employee_id': $("#hr_employee").val(),
    }).done(function(data){
        //~ console.log(data);
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
            $("#employee_image").html("<img src='data:image/png;base64," + data.employee.img + "''/>");
        if (data.employee.img === null)
            $("#employee_image").html("<img src='/hr_payroll_attendance/static/src/img/icon-user.png'/>");
        if (data.attendance.action === 'sign_in') {
            $("#employee_message").html("<h2>Welcome!</h2><h2>" + data.employee.name +"</h2>");
        }
        if (data.attendance.action === 'sign_out'){
            var flexWorkedHour = 0;
            var flexWorkedMinute = 0;
            var flexHour = 0;
            var flexMinute = 0;
            var timeBankHour = 0;
            var timeBankMinute = 0;

            if (data.attendance.flex_working_hours != false) {
                flexWorkedHour = minute2HourMinute(data.attendance.flex_working_hours)[0];
                flexWorkedMinute = minute2HourMinute(data.attendance.flex_working_hours)[1];
            }
            if (data.attendance.flextime != false) {
                flexHour = minute2HourMinute(data.attendance.flextime)[0];
                flexMinute = minute2HourMinute(data.attendance.flextime)[1];
            }

            $("#employee_message").html("<h2>Goodbye!</h2><h2>" + data.employee.name +"</h2>");
            $("#employee_worked_hour").html("<h4><strong>You have worked: </strong>" + flexWorkedHour + " hours and " + flexWorkedMinute +" minutes</h4>");
            $("#employee_flex_time").html("<h4><strong>Your flex time: </strong>" + flexHour + " hours and " + flexMinute +" minutes</h4>");
            $("#employee_time_bank").html("<h4><strong>Your time bank is: </strong>" + timeBankHour + " hours and " + timeBankMinute +" minutes</h4>");
        }
        logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
    });
}

function minute2HourMinute(minute) {
    hour_minute = new Array(2);
    if(Math.abs(minute) % 60 === 0 || minute === 0) {
        hour_minute[0] = minute / 60;
        hour_minute[1] = 0;
    }
    else {
        hour_minute[0] = Math.floor(minute / 60);
        if(minute > 0)
            hour_minute[1] = Math.floor(minute % 60);
        else
            hour_minute[1] = -Math.floor(Math.abs(minute) % 60);
    }
    return hour_minute;
}

function clearContent(){
    $("#employee_image").empty();
    $("#employee_message").empty();
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
    $("#week_day_d").text(getWeekDay(week_day) + " den " + day);
    $("#week_day_m_y").text(getMonth(month) + " " + year);
    $("#date").text(year + "-" + month + "-" + day);
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
