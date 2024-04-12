import firebase_admin
from firebase_admin import credentials, auth

# Inicializar Firebase
cred = credentials.Certificate("E:\\Gamering\\Gamering\\PHP\\game-inir-firebase-adminsdk-4o72p-588301a897.json")
firebase_admin.initialize_app(cred)

# Función para registrar un nuevo usuario con correo electrónico y contraseña
def signup(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        print('Usuario creado exitosamente:', user.uid)
        return user
    except Exception as e:
        print('Error al crear usuario:', e)
        return None

# Función para iniciar sesión con correo electrónico y contraseña
def signin(email, password):
    try:
        user = auth.get_user_by_email(email)
        if user:
            auth_user = auth.sign_in_with_email_and_password(email, password)
            print('Usuario autenticado exitosamente:', auth_user['idToken'])
            return auth_user
    except Exception as e:
        print('Error al autenticar usuario:', e)
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Registrar un nuevo usuario
    new_user = signup("example@example.com", "password123")

    # Iniciar sesión con el nuevo usuario
    if new_user:
        auth_user = signin("example@example.com", "password123")
