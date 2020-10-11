(function () {

    var clockElement = document.getElementById( "clock" );
  
    function updateClock ( clock ) {
      clock.innerHTML = new Date().toLocaleTimeString();
    }
  
    setInterval(function () {
        updateClock( clockElement );
    }, 1000);
  
  }());


$('.message .close')
  .on('click', function() {
    $(this)
      .closest('.message')
      .transition('zoom')
    ;
  })
; 