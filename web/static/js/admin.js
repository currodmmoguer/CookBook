// Comprueba si un objeto está en una lista
function contiene(lista, obj){
    lista.forEach(element => {
        if (element === obj){
            return true;
        }
    });
    return false;
}

// Crea un color aleatorio en formato rgb
function random_rgb() {
    var o = Math.round, r = Math.random, s = 255;
    return 'rgb(' + o(r()*s) + ',' + o(r()*s) + ',' + o(r()*s) + ')';
}