import tkinter as tk
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket
import threading

port = 12345
cesar_desloc = 3

def start_server():
    def handle_client(conn):
        global received_data
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                received_data += data.decode()
            process_received_data(received_data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', port))
        s.listen()
        print(f"Listening on port {port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()

def manchester_differential_decoding(encoded_data):
    decoded_data = []
    last_level = 'high'

    for i in range(0, len(encoded_data), 2):
        bit_pair = encoded_data[i:i+2]
        if bit_pair == '10':
            if last_level == 'high':
                decoded_data.append('1')
                last_level = 'low'
            else:
                decoded_data.append('0')
                last_level = 'low'
        elif bit_pair == '01':
            if last_level == 'low':
                decoded_data.append('1')
                last_level = 'high'
            else:
                decoded_data.append('0')
                last_level = 'high'

    return ''.join(decoded_data)

def convert_to_text(binary_data):
    text = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
    txt_binary.delete("1.0", tk.END)
    txt_binary.insert("1.0", binary_data)
    return text

def cesar_decrypt(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            encrypted_text += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            encrypted_text += char
    return encrypted_text

def decrypt_message(encrypted_text):
    decrypted_text = cesar_decrypt (encrypted_text, cesar_desloc)
    txt_decrypted.delete("1.0", tk.END)
    txt_decrypted.insert("1.0", decrypted_text)
    return decrypted_text

def process_received_data(data):
    global received_data
    received_data = ""
    txt_received.delete("1.0", tk.END)
    txt_received.insert("1.0", data)
    
    binary_data = manchester_differential_decoding(data)
    txt_binary.delete("1.0", tk.END)
    txt_binary.insert("1.0", binary_data)

    encrypted_text = convert_to_text(binary_data)
    txt_encrypted.delete("1.0", tk.END)
    txt_encrypted.insert("1.0", encrypted_text)
    decrypted_text = decrypt_message(encrypted_text)

    show_graph(data)
    
def show_graph(encoded_output):
    binary_values = encoded_output

    data_points = [int(bit) for bit in binary_values]
    
    fig, ax = plt.subplots()
    ax.step(range(len(data_points)), data_points, where='mid')   
    
    for i in range(0, len(data_points) + 1, 2): 
        ax.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=0.5)

    ax.set_ylim(-0.5, 1.5)  
    ax.set_title("Gráfico Binário da Mensagem")
    ax.set_xlabel("Índice do Bit")
    ax.set_ylabel("Valor do Bit")
    
    canvas = FigureCanvasTkAgg(fig, master=window)  
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=9, column=0, columnspan=3)
    canvas.draw()

window = tk.Tk()
window.title("Receptor de Mensagens")

received_data = ''

label_received = tk.Label(window, text="Mensagem Recebida:")
label_received.grid(row=0, column=0)

txt_received = scrolledtext.ScrolledText(window, height=3)
txt_received.grid(row=1, column=0, columnspan=2)

label_binario = tk.Label(window, text="Binário Decodificado")
label_binario.grid(row=2, column=0)

txt_binary = scrolledtext.ScrolledText(window, height=3)
txt_binary.grid(row=3, column=0, columnspan=2)

label_encrypted = tk.Label(window, text="Texto Encriptografado (ASCII)")
label_encrypted.grid(row=4, column=0)

txt_encrypted = scrolledtext.ScrolledText(window, height=3)
txt_encrypted.grid(row=5, column=0, columnspan=2)

label_decrypted = tk.Label(window, text="Texto Descriptografado")
label_decrypted.grid(row=6, column=0)

txt_decrypted = scrolledtext.ScrolledText(window, height=3)
txt_decrypted.grid(row=7, column=0, columnspan=2)

threading.Thread(target=start_server, daemon=True).start()

window.mainloop()
