var retryCount = 0; // Contador de reintentos
const maxRetries = 10; // Máximo número de reintentos
const baseDelay = 500; // Retraso inicial de 5 segundos

function startTransfer() {
    $('#loading').show(); // Muestra la vista de carga
    var progress = 0; // Establece el progreso en 0%
    var interval = setInterval(function() {
        progress += 1; // Incrementa el progreso en 1% por cada iteración
        $('#progress').text(progress + '%'); // Actualiza el texto del elemento de progreso

        // if progress is greater than 100%
        if (progress >= 100) clearInterval(interval);
    }, 5000); // Actualiza el progreso cada 2 segundos update foreach n time

    $.ajax({ //start polling
        url: '/transferData',
        type: 'GET',
        success: function(response) {
            console.log(response, interval)
            if (response.status == 200) {
                setTimeout(function() { pollServer(interval); }, baseDelay);
            } 
        }
    });  
}

function pollServer(interval) {
    $.ajax({
        url: '/Validator',
        type: 'GET',
        success: function(response) {
            console.log(response, interval)
            if (response.status == 200) {
                clearInterval(interval); // stop the interval when data transfer is finished
                $('#loading').hide(); // hidden view of loading
                location.href = '/'; //redirect main page
                retryCount = 0; // set counter of retrys
            } else {
                // if transfer is not complete , send request to server
                if (retryCount < maxRetries) {
                    retryCount++;
                    const delay = baseDelay * Math.pow(2, retryCount); //increment exponential retry
                    setTimeout(function() { pollServer(interval); }, delay);
                }
            }
        },
        error: function(error) {
            clearInterval(interval); //interval if exists some error
            $('#loading').hide(); // hidden view of loading
            alert('Error al transferir data'); // message of error
        }
    });
}
