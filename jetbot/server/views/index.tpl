<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>JETBOT 3000</title>
    <!-- Bootstrap -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->

    <script src="/static/js/jquery-2.1.1.min.js"></script>
    <script src="/static/js/Bacon.js"></script>
    <script src="/static/js/app.js"></script>
    <link href="/static/styles.css" rel="stylesheet"/>
  </head>
  
  <body>
    <div class="jumbotron header">
      <div class="container">
	<h1>JETBOT 3000</h1>
	<p>An experiment in telepresence-robotics.</p>
      </div>
    </div>

    <div class="container-fluid bottomhalf">
      <div class="row">
	<div class="col-md-4">
	  <p>Use the arrow-keys to control movement. 
	    <b>IMPORTANT:</b>Don't switch the focus away from the browser while pressing a key, otherwise the robot doesn't stop.</p>
	</div>
	<div class="col-md-4">
	  <div class="well">
	    <div class="arrow-container">
	      <div class="box">&nbsp;</div>
	      <div class="arrow up">&#x2191;</div>
	      <div class="box">&nbsp;</div>
	      <div class="arrow left">&#x2190;</div>
	      <div class="arrow down">&#x2193;</div>
	      <div class="arrow right">&#x2192;</div>
	    </div>
	  </div>
	</div>
	<div class="col-md-4">
	</div>
      </div>
    </div>
    <script src="/static/js/bootstrap.min.js"></script>
    <script>
      $(document).ready(function() {
        app();
      });
    </script>
  </body>
</html>
