from streamlit_authenticator.utilities.hasher import Hasher

passwords_to_hash = ['fashion@123', 'increff@fashion']
hasher = Hasher()  # Instantiate without arguments

# Hypothetical method, replace with the actual one from documentation
hashed_passwords = [hasher.hash_passwords(password) for password in passwords_to_hash]

print(hashed_passwords)
