$(document).ready(function(){
    
    var campos = $('#receta-form input, #receta-form textarea');
    
    campos.each(function(index){
        
        if ($(this).val() != ""){
            $(this).next().addClass('with-text');
        } else {
            $(this).next().removeClass('with-text');
        }
    });

    var btn = $('button[type=submit]');

    $('input, textarea').blur(function(){
        if ($(this).val() != ""){
            $(this).next().addClass('with-text');
        } else {
            $(this).next().removeClass('with-text');
        }
    });

    $('input[type=password]').keyup(function(){
        var pass1 = $('#password');
        var pass2 = $('#password2')
        

        
        if (pass1.val() == pass2.val() && pass1.val().length >= 8){
            pass2.css('border-bottom', '2px solid green');
            //btn.prop('disabled', false);
        } else {
            pass2.css('border-bottom', '2px solid red');
            //btn.prop('disabled', true);
        }
    });

    
});