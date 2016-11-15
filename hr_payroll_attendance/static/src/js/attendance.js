function attendance_data_loop() {
    openerp.jsonRpc('/longpolling/poll','call',{"channels":["attendance"],last:0}).then(function(r){
        $('#attendance_data').html(r[0].message);
        attendance_data_loop();
        }, function(r) {
            attendance_data_loop();
        }
    )
};
attendance_data_loop()

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
}

/* Come and Go */
function come_and_go(){
openerp.jsonRpc("/hr/attendance/come_and_go", 'call', {
    'employee_id': $("#hr_employee").val(),
    }).done(function(data){
        $("#login").addClass("hidden");
        $("#logout").addClass("hidden");
        $("#attendance_div").load(document.URL +  " #attendance_div");
        $('#Log_div').fadeIn();
        if (data.img !== null)
            $("#employee_image").html("<img src='/website/image/hr.employee/" + data.id +"/image'/>");
        if (data.img === null)
            $("#employee_image").html("<img src='/hr_payroll_attendance/static/src/img/icon-user.png'/>");
        if (data.state === 'present')
            $("#employee_message").html("<h2>Welcome!</h2><h2>" + data.name +"</h2>");
        if (data.state === 'absent')
            $("#employee_message").html("<h2>Goodbye!</h2><h2>" + data.name +"</h2>");
        $('#Log_div').delay(2000).fadeOut("slow");
    });
}
