# password_manager.py

def read_password():
    with open('config.py', 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('PASSWORD ='):
                return line.split('=')[1].strip().strip("'")
    return None

def write_password(new_password):
    with open('config.py', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    with open('config.py', 'w', encoding='utf-8') as file:
        for line in lines:
            if line.startswith('PASSWORD ='):
                file.write(f"PASSWORD = '{new_password}'")
            else:
                file.write(line)

def get_password():
    return read_password()