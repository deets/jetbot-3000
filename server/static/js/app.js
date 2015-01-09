function app() {
    var tracking = false;
    var last_event = null;

    function send_data() {
	var data = last_event || {};
	$.ajax({
	    url: '/track',
	    type: 'POST',
	    data: JSON.stringify(data),
	    contentType: 'application/json; charset=utf-8',
	    dataType: 'json'
	});
    }

    function start_tracking() {
	tracking = true;
    }

    function stop_tracking() {
	tracking = false;
	last_event = null;
	var data = { "command" : "stop" };
	$.ajax({
	    url: '/track',
	    type: 'POST',
	    data: JSON.stringify(data),
	    contentType: 'application/json; charset=utf-8',
	    dataType: 'json'
	});
    }

    function track_coords(event) {
	if(!tracking) {
	    return;
	}
	var offsets = $(event.target).offset();
	var width = $(event.target).width();
	var height = $(event.target).height();
	var x = ((event.pageX - offsets.left) - width / 2.0) / (width / 2.0);
	var y = ((event.pageY - offsets.top) - height / 2.0) / (height / 2.0);
	last_event = { "command" : "track", "x" : x, "y" : y };
	send_data();
    };

    $(".crosshair").mousedown(function(event) { 
	start_tracking(event); track_coords(event);
    }).mousemove(track_coords).mouseup(stop_tracking).mouseout(stop_tracking);

    function resend_data() {
	setTimeout(resend_data, 50);
	if(tracking) {
	    send_data();
	}
    }
    setTimeout(resend_data, 50);

    $(document).keydown(function(event) {
	switch(event.keyCode) {
	case 38: // up
	    last_event = { "x" : 0.0, "y" : -1.0, "command" : "track"};
	    tracking = true;
	    break;
	case 39: // right
	    last_event = {"x" : 1.0, "y" : .0, "command" : "track"};
	    tracking = true;
	    break;
	case 37: // left
	    last_event = {"x" : -1.0, "y" : .0, "command" : "track"};
	    tracking = true;
	    break;
	case 40: // down
	    last_event = {"x" : 0.0, "y" : 1.0, "command" : "track"};
	    tracking = true;
	    break;
	}
    });
    $(document).keyup(stop_tracking);

}
