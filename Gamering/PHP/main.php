<?php
// Establecer los encabezados CORS
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET");
header("Access-Control-Allow-Headers: Content-Type");
//MySQLi
$servername = "localhost";
$user = "root";
$password = "";
$dbname = "prueba";

//Establecer coneion
$conn = new mysqli($servername, $user, $password, $dbname);

// Veificación de la conexión
if($conn -> connect_error)
{ die("Conexión fallida: ".$conn->connect_error);}
//Procesamiento del formulario que se ha enviado
if ($_SERVER["REQUEST_METHOD"] == "POST"){
//Validación y limpieza de los datos del formulario
$nombre = limpiar_datos($_POST["nombre"]); 
$email = limpiar_datos($_POST["email"]);
$password = limpiar_datos($_POST["contrasena"]);

//Creado y ejectutado la query para la inserción de los datos con sentencias ya preparadas
$sql = "INSERT INTO registro (nombre, email, contrasena) VALUES (?, ?, ?)";
$stmt = $conn -> prepare($sql);
//Vinculación de los datos
$stmt-> bind_param("sss", $nombre, $email, $password);

if ($stmt->execute()) {
    // Redireccionar después de un registro exitoso
    header("Location: http://localhost/prueba/Gamering/login.html");
    exit(); // Asegura que el script se detenga después de la redirección
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

}
//Cerrar conexión
$conn -> close();
//Declaracion de la funcion para limpiar datos
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