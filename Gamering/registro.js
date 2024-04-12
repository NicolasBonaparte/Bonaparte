const firebaseConfig = {
    apiKey: "AIzaSyBnzO43K9YZcBhjIRooqvMXMuMuWJ3JhUs",
    authDomain: "game-8cb6c.firebaseapp.com",
    projectId: "game-8cb6c",
    storageBucket: "game-8cb6c.appspot.com",
    messagingSenderId: "71936696275",
    appId: "1:71936696275:web:a455f5ae77dda213879926",
    measurementId: "G-9EW13L1QKQ"
  };
const app = firebase.initializeApp(firebaseConfig);
        
// Obtén una referencia a la autenticación y la base de datos
const auth = firebase.auth();
const database = firebase.database();

// Agrega aquí tu lógica de registro con Firebase
document.getElementById('registroForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const nombre = document.getElementById('floatingNombre').value;
    const email = document.getElementById('floatingEmail').value;
    const contrasena = document.getElementById('floatingPassword').value;
    
    // Registra al usuario con correo electrónico y contraseña
    auth.createUserWithEmailAndPassword(email, contrasena)
        .then((userCredential) => {
            // Registro exitoso
            console.log('Usuario registrado:', userCredential.user);
            // Guarda información adicional en la base de datos
            database.ref('Usuarios/' + userCredential.user.uid).set({
                nombre: nombre,
                email: email
            });
            // Redirecciona al usuario o muestra un mensaje de éxito
        })
        .catch((error) => {
            // Error en el registro
            console.error('Error al registrar usuario:', error);
            // Muestra un mensaje de error al usuario
        });
});