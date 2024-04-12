// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBnzO43K9YZcBhjIRooqvMXMuMuWJ3JhUs",
  authDomain: "game-8cb6c.firebaseapp.com",
  projectId: "game-8cb6c",
  storageBucket: "game-8cb6c.appspot.com",
  messagingSenderId: "71936696275",
  appId: "1:71936696275:web:a455f5ae77dda213879926",
  measurementId: "G-9EW13L1QKQ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const email = loginForm.nombre.value;
  const password = loginForm.contrasena.value;

  firebase.auth().signInWithEmailAndPassword(email, password)
    .then((userCredential) => {
      // Inicio de sesión exitoso, redirigir o mostrar mensaje de éxito
      console.log("Inicio de sesión exitoso:", userCredential.user);
    })
    .catch((error) => {
      // Error en el inicio de sesión, mostrar mensaje de error
      console.error("Error al iniciar sesión:", error.message);
    });
});