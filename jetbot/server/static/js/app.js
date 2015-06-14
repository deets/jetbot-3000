String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

String.prototype.startsWith = function(prefix) {
    return this.indexOf(prefix) == 0;
};

function python_timestamp() {
    return Date.now() / 1000.0;
};

function app() {
    function bindInputs() {
	var keydown = $(document).asEventStream('keydown').map('.keyCode');
	var keyup = $(document).asEventStream('keyup').map('.keyCode');

	var left   = keydown.filter(function(x) { return x === 37; }).map("left");
	var right  = keydown.filter(function(x) { return x === 39; }).map("right");
	var up   = keydown.filter(function(x) { return x === 38; }).map("up");
	var down  = keydown.filter(function(x) { return x === 40; }).map("down");

	var left_stop   = keyup.filter(function(x) { return x === 37; }).map("left_stop");
	var right_stop  = keyup.filter(function(x) { return x === 39; }).map("right_stop");
	var up_stop   = keyup.filter(function(x) { return x === 38; }).map("up_stop");
	var down_stop  = keyup.filter(function(x) { return x === 40; }).map("down_stop");

	var vc = Bacon.fromEventTarget(document, "visibilitychange").map(
	function(event) {
	    return event.target.visibilityState;
	});

	return {
	    left: left,
	    right: right,
	    down: down,
	    up: up,
	    left_stop: left_stop,
	    right_stop: right_stop,
	    up_stop: up_stop,
	    down_stop: down_stop,
	    vc: vc
	    };
    }

    var inputs = bindInputs();
    var stop = Bacon.constant("stop");

    function const_(v) {
	function f() {
	    return v;
	}
	return f;
    }
    var stop = const_("stop");

    var drivecommands = Bacon.mergeAll(
	$.map(
	    inputs,
	    function(stream) { return stream; }
	)
    );
    var sm = drivecommands.withStateMachine(
	"stop",
	function(direction, event) {
	    event = event.value();
	    if(event.endsWith("stop")) {
		if(event.startsWith(direction)) {
		    return ["stop", [new Bacon.Next("stop")]];
		} else {
		    return [direction, [new Bacon.Next(direction)]];
		}
	    } else if(event == "hidden" || event == "visible") {
		return ["stop", [new Bacon.Next("stop")]];
	    }
	    return [event, [new Bacon.Next(event)]];
	});

    var tick   = Bacon.interval(100).map("tick");
    sm.log("statemachine: ");
    sm.onValue(function(event) {
	var data = { "command" : event, "timestamp" : python_timestamp() };
	$.ajax({
	    url: '/track',
	    type: 'POST',
	    data: JSON.stringify(data),
	    contentType: 'application/json; charset=utf-8',
	    dataType: 'json'
	}); });
    sm.onValue(function(event) {
	$(".arrow").removeClass("active");
	var sel = ".arrow." + event;
	$(sel).addClass("active");
    });


    function statusPoll(){
	$.ajax(
	    "/status",
	    {
		"success": function(data) {
		    $("#status").text(data.status);
		    $("#status").removeClass();
		    $("#status").addClass(data.status);
		    $("#status").addClass("well");
		    setTimeout(statusPoll, 500);
		},
		"error": function() {
		    setTimeout(statusPoll, 500);
		}
	    }
	)
    };
    statusPoll();

    (function() {
	var ws = null;

	function errororclose() {
	    if (ws !== null) {
		console.log("lost timesync connection, re-connecting");
		ws = null;
		setTimeout(connect, 500);
	    }
	};

	function connect() {
	    ws = new WebSocket("ws://" + document.location.host + "/websocket");
	    ws.onmessage = function (evt) {
		var sync = JSON.parse(evt.data);
		console.log(sync);
		var now = python_timestamp();
		var ack = {
		    'sender_timestamp': sync.timestamp,
		    'receiver_timestamp': now,
		    'sender_uid': sync.uid,
		    'type': 'SYNC_ACK',
		    'uid': sync.uid + '-browser',
		    'timestamp': now
		};
		console.log(ack);
		if(ws !== null && ws.readyState == WebSocket.OPEN) {
		    ws.send(JSON.stringify(ack));
		}
	    };

	    ws.onclose = ws.onerror = errororclose;
	};
	connect();
    }());
}
