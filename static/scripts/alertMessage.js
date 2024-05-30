$(document).ready(function() {
    $('#upload-form').on('submit', function(event) {
        event.preventDefault();
        var action = $(this).find('input[type=submit]:focus').val();
        var url = action === 'Upload' ? '/upload' : '/delete';
        var successMessage = action === 'Upload' ? 'Archivo subido con éxito' : 'Archivos eliminados exitosamente';

        $.ajax({
            url: url,
            method: 'POST',
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                if (data.success) {
                    alert(successMessage);
                    // Limpiar el formulario después de la carga exitosa del archivo
                    $('#upload-form')[0].reset();
                }
            }
        });
    });
});
