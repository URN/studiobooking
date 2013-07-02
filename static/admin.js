
function destroyBookingForm() {
    $('#duration').val('');
    $('#booking').hide(duration=400);
}

function showBookingForm(date) {
    destroyBookingForm();
    $('#booking').show(duration=400);
    $('#response').hide(duration=400);
    $(window).scrollTop($('#booking').offset().top);
    $('#start').val(date.toUTCString());
    $('#date').val(date.toDateString('dd-mm-yyyy'));
    $('#time').val(date.toTimeString('hh-mm'));
    $('#duration').timepicker('option', {
        'minTime': date,
        'maxTime': '12:00am',
        'showDuration': true
});
};

function editBooking(event) {
    destroyBookingForm();
    $('#booking').show(duration=400);
    $('#response').hide(duration=400);
    $(window).scrollTop($('#booking').offset().top);
    $("#bookingform").attr("action", "/edit/" + event.id);
    $('#name').val(event.name)
    $('#contact').val(event.contact)
    $('#start').val(event.start.toUTCString());
    $('#date').val(event.start.toDateString('dd-mm-yyyy'));
    $('#time').val(event.start.toTimeString('hh-mm'));
    $('#duration').timepicker('option', {
        'minTime': event.start,
        'maxTime': '12:00am',
        'showDuration': true
    });
    $('#duration').val(event.end.toTimeString('hh:mm'));
    $('#studio').val(event.studio);
};


function deleteBooking(event) {
    if (confirm('This will delete the booking '+event.title+'. Are you sure?')) {
        $.ajax({
            type: "GET",
            url: '/delete/' + event.id,
            success: function(data) {
                $('#response').html(data);
                $('#calendar').fullCalendar('refetchEvents');
            }
        });
    }
};


$(document).ready(function() {

    $('#duration').timepicker();

    $('#cancelbooking').click(function(event) {
        event.preventDefault();
        destroyBookingForm();
    })

    $("#bookingform").submit(function() {

        $('#booking').hide(duration=400);
        $.ajax({
            type: "POST",
            url: '/booking',
            data: $("#bookingform").serialize(),
            success: function(data)
            {
                $('#response').html(data);
                $('#calendar').fullCalendar('refetchEvents');
            }
            });
        $('#response').show(duration=400);
        return false;
    });

    $('#calendar').fullCalendar({
    events: '/events',
    dayClick: function(date, allDay, jsEvent, view) {
            if (allDay) {
                $('#calendar').fullCalendar('changeView', 'agendaDay');
                $('#calendar').fullCalendar('gotoDate', date);
            } else {
                showBookingForm(date);
            }
    },
    eventClick: function(event, jsEvent, view) {
        deleteBooking(event)
    },
    header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,agendaWeek,agendaDay'
    },
    defaultView: 'agendaWeek',
    minTime: 8,
    aspectRatio: 1,
})

});

