import socket
import struct

class CommunicationServer:
    def __init__(self, address, port_number, protocol_type):
        self.address = address
        self.port_number = port_number
        self.protocol_type = protocol_type
        self.server_socket = None

    def start(self):
        if self.protocol_type == 'TCP':
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.address, self.port_number))
            self.server_socket.listen(1)
            print(f"TCP сервер запущен на {self.address}:{self.port_number}")
            connection_socket, client_info = self.server_socket.accept()
            print(f"Подключено: {client_info}")
            self.handle_tcp_connection(connection_socket)
        else:  # UDP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.address, self.port_number))
            print(f"UDP сервер запущен на {self.address}:{self.port_number}")
            self.listen_udp()

    def handle_tcp_connection(self, connection_socket):
        with connection_socket:
            while True:
                try:
                    incoming_message = self.receive_full_message(connection_socket)
                    print(f"TCP Получено сообщение: {incoming_message.decode()}")
                    response = input("Ответ от сервера (TCP): ")
                    self.send_full_message(connection_socket, response)
                except (ConnectionError, struct.error):
                    print("Клиент отключился.")
                    break

    def listen_udp(self):
        while True:
            try:
                msg, address = self.server_socket.recvfrom(1024)
                print(f"UDP Получено сообщение от {address}: {msg.decode()}")
                reply = input("Ответ от сервера (UDP): ")
                self.server_socket.sendto(reply.encode(), address)
            except Exception as e:
                print(f"Ошибка: {e}")

    def receive_full_message(self, conn):
        header = self.receive_exact_bytes(conn, 4)
        message_length = struct.unpack('!I', header)[0]
        return self.receive_exact_bytes(conn, message_length)

    def send_full_message(self, conn, message):
        message_encoded = message.encode()
        length = len(message_encoded)
        conn.sendall(struct.pack('!I', length) + message_encoded)

    def receive_exact_bytes(self, conn, byte_count):
        data = b''
        while len(data) < byte_count:
            fragment = conn.recv(byte_count - len(data))
            if not fragment:
                raise ConnectionError("Соединение было потеряно.")
            data += fragment
        return data

class CommunicationClient:
    def __init__(self, address, port_number, protocol_type):
        self.address = address
        self.port_number = port_number
        self.protocol_type = protocol_type
        self.client_socket = None

    def start(self):
        if self.protocol_type == 'TCP':
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.address, self.port_number))
            print(f"Соединение с TCP сервером {self.address}:{self.port_number} установлено")
            self.tcp_interaction()
        else:  # UDP
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Соединение с UDP сервером {self.address}:{self.port_number} установлено")
            self.udp_interaction()

    def tcp_interaction(self):
        try:
            while True:
                client_message = input("Клиент (TCP): ")
                self.send_full_message(client_message)
                server_reply = self.receive_full_message()
                print(f"TCP Получено от сервера: {server_reply.decode()}")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.client_socket.close()

    def udp_interaction(self):
        try:
            while True:
                client_message = input("Клиент (UDP): ")
                self.client_socket.sendto(client_message.encode(), (self.address, self.port_number))
                response, _ = self.client_socket.recvfrom(1024)
                print(f"UDP Получено от сервера: {response.decode()}")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.client_socket.close()

    def send_full_message(self, message):
        encoded_message = message.encode()
        length = len(encoded_message)
        self.client_socket.sendall(struct.pack('!I', length) + encoded_message)

    def receive_full_message(self):
        header = self.receive_exact_bytes(4)
        msg_length = struct.unpack('!I', header)[0]
        return self.receive_exact_bytes(msg_length)

    def receive_exact_bytes(self, byte_count):
        data = b''
        while len(data) < byte_count:
            fragment = self.client_socket.recv(byte_count - len(data))
            if not fragment:
                raise ConnectionError("Соединение было потеряно.")
            data += fragment
        return data

def execute_chat(mode, address, port_number):
    if "server" in mode:
        protocol_type = "TCP" if "tcp" in mode else "UDP"
        server_instance = CommunicationServer(address, port_number, protocol_type)
        server_instance.start()
    else:
        protocol_type = "TCP" if "tcp" in mode else "UDP"
        client_instance = CommunicationClient(address, port_number, protocol_type)
        client_instance.start()

if __name__ == "__main__":
    import argparse
    argument_parser = argparse.ArgumentParser(description="Простое приложение чата с использованием TCP и UDP")
    argument_parser.add_argument("mode", choices=["tcp_server", "tcp_client", "udp_server", "udp_client"], help="Режим: сервер или клиент")
    argument_parser.add_argument("--address", default="127.0.0.1", help="IP адрес")
    argument_parser.add_argument("--port", type=int, default=12345, help="Номер порта")
    args = argument_parser.parse_args()
    
    execute_chat(args.mode, args.address, args.port)
