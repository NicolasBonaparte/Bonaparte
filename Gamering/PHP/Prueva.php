<?php

require 'vendor/autoload.php';

use Kreait\Firebase\Factory;
use Kreait\Firebase\ServiceAccount;

// Ruta al archivo JSON de Service Account
$serviceAccount = ServiceAccount::fromJsonFile('path/to/your/serviceAccountKey.json');

// Configuración de Firebase
$firebase = (new Factory)
    ->withServiceAccount($serviceAccount)
    ->create();

$database = $firebase->getDatabase();

// Datos a agregar
$nuevoUsuario = [
    'nombre' => 'Ejemplo Usuario',
    'correo' => 'ejemplo@example.com',
    'fecha_registro' => date('Y-m-d H:i:s')
];

// Agregar datos a la colección 'usuarios'
$database->getReference('usuarios')->push($nuevoUsuario);

echo "Datos agregados correctamente.";

?>
