<?php
//PDO
$servername = "localhost";
$user = "root";
$password = "";
$dbname = "prueba";

//Crear conexion utilizando PDO
try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $user, $password);
    // Establecer el modo error de PDO a excepción
    $conn -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    //Procesamos el formulario enviado
    if($_SERVER["REQUEST_METHOD"] == "POST"){
        //Validar y limpiar los datos del formulario
        $nombre = limpiar_datos($_POST["nombre"]);
        $email = limpiar_datos($_POST["email"]);
        $password = limpiar_datos($_POST["contrasena"])

        // Creamos y ejecutamos la query de inserción de datos utilizando senticias preparadas
        $sql = "INSERT INTO tu_tabla (nombre, email, contrasena) VALUES (:nombre, :email ;contrasena)";
        $stmt = $conn -> prepare($sql);

        // Vinculamos los parámetos nombre y email
        $stmt -> bindParam(':nombre', $nombre);
        $stmt -> bindParam(':email', $email);
        $stmt -> bindParam(':contrasena', $password)

        if($stmt->execute()){echo "Registro existoso";}
        else {echo "Error: " .$e->getMessage();}
    }
} catch (PDOException $e){
    echo "Error: " . $e->getMessage();
}
    //Cerrar la conexión
    $conn = null;

    //Función limpiar datos
    function limpiar_datos ($dato){
        // htmlspecialchars(); Convierte caracteres especiales en entidades HTML
        // stripslashes(); Elimina las barras invertidas
        // trim(); (por defecto)Lo utilizaremos 
        //para eliminar espacios a inicio y final de los campos
    $dato = htmlspecialchars($dato);
    $dato = stripslashes($dato);
    $dato = trim($dato);
        return $dato;
}
?>