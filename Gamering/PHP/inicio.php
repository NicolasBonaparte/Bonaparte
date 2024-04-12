<?php
session_start(); // Asegúrate de iniciar la sesión al principio del archivo

$host = "localhost";
$user = "root";
$password = "";
$dbname = "prueba";

$conn = new mysqli($host, $user, $password, $dbname);

if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Verificar si la clave "email" está definida antes de usarla
    $email = isset($_POST["email"]) ? $_POST["email"] : null;
    
    if (isset($_POST["registro"])) {
        $nombre = $_POST["nombre"];
        $contrasena = $_POST["contrasena"];

        // Verificar si el nombre y la contraseña ya existen en la base de datos
        $verificarExistencia = mysqli_query($conn, "SELECT * FROM registro WHERE nombre = '$nombre' AND contrasena = '$contrasena'");
        
        if ($verificarExistencia->num_rows > 0) {
            // Usuario registrado, redirige a la página principal
            header("Location: http://localhost/prueba/Gamering/index.html");
            exit();
        } else {
            $insertarDatos = "INSERT INTO registro (nombre, email, contrasena) VALUES ('$nombre', '$email', '$contrasena')";

            $ejecutarinsertar = mysqli_query($conn, $insertarDatos);

            if ($ejecutarinsertar) {
                echo "Registro exitoso.";
            } else {
                echo "Error al registrar: " . mysqli_error($conn);
            }
        }
    }

    if (isset($_POST["inicia"])) {
        
        header("Location: http://localhost/prueba/Gamering/iniciar_session.html");
        exit();
    }
}
?>
