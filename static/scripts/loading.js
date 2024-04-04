function startTransfer() {
    $('#loading').show(); //show view of loading
    var progress = 0; // set progress in 0%
    var interval = setInterval(function() {
        progress += 1; //increment the progress in 5% for each interation
        $('#progress').text(progress + '%'); //update text of the element of progress

        // if the progress exceeds 100%, stop de interval
        if (progress >= 100) clearInterval(interval);
    }, 2000); //update the progress for each 2 seconds

    $.ajax({
        url: '/transferData',
        type: 'GET',
        success: function(response) {
            console.log(response, interval)
            if (response.status == 200) {
                setTimeout(pollServer, 5000);
            } 
        }
        })  
}

function pollServer(interval) {
    console.log('starting pool...')
    $.ajax({
        url: '/Validator',
        type: 'GET',
        success: function(response) {
            console.log(response, interval)
            if (response.status == 200) {
                clearInterval(interval); // stop  the interval when the trasnfer is complete
                $('#loading').hide(); // hide the view of the loading
                location.href = '/'; // redirect to main page
            } else {
                // If the transfer is not complete, poll the server again after a delay
                setTimeout(pollServer, 5000);
            }
        },
        error: function(error) {
            clearInterval(interval); // stop the interval if there are some error
            $('#loading').hide(); // hide de view of loading
            alert('Error al transferir data'); // show the message error
        }
    });
}

