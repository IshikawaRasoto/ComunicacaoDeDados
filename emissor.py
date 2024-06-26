import tkinter as tk
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket

ip_receiver = '25.6.83.161'
port = 12345

dados_global = ''

deslocamento_cesar = 3

def caesar_encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            encrypted_text += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_text += char
    return encrypted_text

def manchester_differential_encoding(binary_data):
    encoded_data = []
    last_level = 'high'
    
    for bit in binary_data:
        if bit == '1':
            
            if last_level == 'high':
                encoded_data.append('high')
                last_level = 'high'
            else:
                encoded_data.append('low')
                last_level = 'low'
        else:
            if last_level == 'high':
                encoded_data.append('low')
                last_level = 'low'
            else:
                encoded_data.append('high')
                last_level = 'high'

        if last_level == 'high':
            encoded_data.append('low')
            last_level = 'low'
        else:
            encoded_data.append('high')
            last_level = 'high'


    return ''.join('1' if level == 'high' else '0' for level in encoded_data)

def convert_to_binary(text):
    
    # A linha abaixo converte em binário a String que o usuário colocou
    binary_text = ' '.join(format(ord(x), '08b') for x in text)
    
    # Descomentar a linha abaixo e comentar a de cima caso queira testar a forma de onda com valor 19
    #binary_text = ' '.join(format(19, '08b') for x in text)

    txt_binary.delete("1.0", tk.END)
    txt_binary.insert("1.0", binary_text)
    return binary_text.replace(' ', '')  

def encrypt_message():
    global dados_global
    global deslocamento_cesar

    plain_text = txt_input.get("1.0", tk.END).strip()
    
    
    encrypted_text = caesar_encrypt(plain_text, deslocamento_cesar)
    # Descomentar a linha abaixo e comentar a de cima para desabilitar a criptografia
    #encrypted_text = plain_text
    
    txt_encrypted.delete("1.0", tk.END)
    txt_encrypted.insert("1.0", encrypted_text)
    binary_text = convert_to_binary(encrypted_text)  
    encoded_output = manchester_differential_encoding(binary_text)
    dados_global = encoded_output
    txt_encoded.delete("1.0", tk.END)
    txt_encoded.insert("1.0", encoded_output)
    show_graph(encoded_output)

def show_graph(encoded_output):
    binary_values = encoded_output
    

    data_points = [int(bit) for bit in binary_values]
    
    fig, ax = plt.subplots(figsize=(15,5))
    ax.step(range(len(data_points)), data_points, where='mid')
    

    for i in range(0, len(data_points) + 1, 2): 
        ax.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=0.5)

    ax.set_ylim(-0.5, 1.5)  
    ax.set_title("Gráfico Binário da Mensagem")
    ax.set_xlabel("Índice do Bit")
    ax.set_ylabel("Valor do Bit")
    
    canvas = FigureCanvasTkAgg(fig, master=window) 
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=8, column=0, columnspan=7)
    canvas.draw()


def send_bits():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_receiver, port))
            s.sendall(dados_global.encode())
            print("Data sent successfully")
    except Exception as e:
        print(f"An error occurred: {e}")


# Configuração da janela principal
window = tk.Tk()
window.title("Emissor de Mensagens")
window.geometry("1500x900")

# Widgets
txt_input = scrolledtext.ScrolledText(window, height=3)
txt_input.grid(row=0, column=0, columnspan=2)

btn_encrypt = tk.Button(window, text="Criptografar e Converter", command=encrypt_message)
btn_encrypt.grid(row=1, column=0)

label_cripotgrafado = tk.Label(window, text="Texto encriptografado:")
label_cripotgrafado.grid(row=2, column=0)

txt_encrypted = scrolledtext.ScrolledText(window, height=3)
txt_encrypted.grid(row=3, column=0, columnspan=2)

label_binario = tk.Label(window, text="Binario encriptografado")
label_binario.grid(row=4, column=0)

txt_binary = scrolledtext.ScrolledText(window, height=3)
txt_binary.grid(row=5, column=0, columnspan=2)

label_binario_manchester = tk.Label(window, text="Binario Manchester")
label_binario_manchester.grid(row=6, column=0)

txt_encoded = scrolledtext.ScrolledText(window, height=3)
txt_encoded.grid(row=7, column=0, columnspan=2)

btn_enviar = tk.Button(window, text="Enviar Mensagem", command=send_bits)
btn_enviar.grid(row=9, column=0)

window.mainloop()
