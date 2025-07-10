import socket
import sys

class ForumClient:
    def __init__(self, server_port):
        self.server_ip = '127.0.0.1'  
        self.server_port = server_port
        self.udp_socket = None
        self.tcp_socket = None
        self.username = None
        
    def start(self):
        print(f'python clinet {self.server_port}')

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.authenticate()
        
        self.show_commands()
        
        while True:
            user_input = input("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: ")
            self.process_command(user_input)
    
    def authenticate(self):
        while True:
            username = input("Enter username: ")
            
            # Send username to server
            message = f"AUTH:{username}"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            
            # Receive response
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response == "PASSWORD:":
                # Existing user, ask for password
                password = input("Enter password: ")
                self.udp_socket.sendto(password.encode(), (self.server_ip, self.server_port))
                
                # Get authentication result
                data, _ = self.udp_socket.recvfrom(1024)
                result = data.decode()
                
                if result.startswith("SUCCESS:"):
                    self.username = username
                    print(result[9:])  
                    return
                else:
                    print(result[7:])  
            
            elif response == "NEWUSER:":
                # New user, create account
                password = input("New user, enter password: ")
                self.udp_socket.sendto(password.encode(), (self.server_ip, self.server_port))
                
                # Get account creation result
                data, _ = self.udp_socket.recvfrom(1024)
                result = data.decode()
                
                if result.startswith("SUCCESS:"):
                    self.username = username
                    print(result[9:])  
                    return
            
            elif response.startswith("ERROR:"):
                # Username already in use
                print(response[7:]) 
                
    def show_commands(self):
            print("Available commands:")
            print("CRT: Create Thread")
            print("LST: List Threads")
            print("MSG: Post Message")
            print("DLT: Delete Message")
            print("RDT: Read Thread")
            print("EDT: Edit Message")
            print("UPD: Upload File")
            print("DWN: Download File")
            print("RMV: Remove Thread")
            print("XIT: Exit")
    
    def process_command(self, command):
        parts = command.split()
        
        if parts[0] == "CRT":
            if len(parts) != 2:
                print("Incorrect syntax for CRT. Usage: CRT threadtitle")
                return
                
            thread_title = parts[1]
            
            # Send CRT command to server
            message = f"CRT {thread_title} {self.username}"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            
            # Receive response
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                print(f"Thread {thread_title} created")
            else:
                print(response[7:])  
        
        elif parts[0] == "LST":
            if len(parts) != 1:
                print("Incorrect syntax for LST. Usage: LST")
                return 
            
            message = "LST"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))

            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()

            if response.startswith("SUCCESS:"):
                threads = response[9:].split('\n')
                if threads[0] == "No threads to list":
                    print("No threads to list")
                else:
                    print(f'The list of active threads')
                    for thread in threads:
                        print(thread)
            else:
                print(response[7:])
        
        elif parts[0] == "MSG":
            if len(parts) < 3:
                print("Incorrect syntax for MSG. Usage: MSG threadtitle message")
                return
        
            thread_title = parts[1]
            message = ' '.join(parts[2:])
            
            message_to_send = f"MSG {thread_title} {self.username} {message}"
            self.udp_socket.sendto(message_to_send.encode(), (self.server_ip, self.server_port))
            
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                print(f"Message posted to {thread_title} thread")
            else:
                print(response[7:]) 
        
        elif parts[0] == "DLT":
            if len(parts) != 3:
                print("Incorrect syntax for DLT. Usage: DLT threadtitle messagenumber")
                return
            thread_title = parts[1]
            # print(parts[2])
            try :
                msg_number = int(parts[2])
            except ValueError:
                print("please enter the correct message number")
                return
            
            message_to_send = f"DLT {thread_title} {self.username} {msg_number}"
            self.udp_socket.sendto(message_to_send.encode(), (self.server_ip, self.server_port))
            
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                print("Message deleted")
            else:
                print(response[7:]) 

        elif parts[0] == "EDT":
            if len(parts) < 3:
                print("Incorrect syntax for EDT. Usage: EDT threadtitle messagenumber message")
                return
            
            thread_title = parts[1]

            try :
                msg_number = int(parts[2])
            except ValueError:
                print("please enter the correct message number")
                return
            msg = ' '.join(parts[3:])
            
            message_to_send = f"EDT {thread_title} {self.username} {msg_number} {msg}"
            self.udp_socket.sendto(message_to_send.encode(), (self.server_ip, self.server_port))
            
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                print("Message edited")
            else:
                print(response[7:])

        elif parts[0]== "RDT":
            if len(parts) != 2:
                print("Incorrect syntax for RDT. Usage: RDT threadtitle")
                return 
            thread_title = parts[1]

            message_to_send = f"RDT {thread_title}"
            self.udp_socket.sendto(message_to_send.encode(), (self.server_ip, self.server_port))

            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()

            if response.startswith("SUCCESS:"):
                threads = response[9:].split('\n')
                if threads[0] == "Thread is empty.":
                    print("Thread is empty")
                else:
                    for line in threads:
                        print(line)
            else:
                print(response[7:])

        elif parts[0] == "RMV":
            if len(parts) != 2:
                print("Incorrect syntax for RMV. Usage: RMV threadtitle")
                return 
            thread_title = parts[1]

            message_to_send = f"RMV {self.username} {thread_title}"
            self.udp_socket.sendto(message_to_send.encode(), (self.server_ip, self.server_port))

            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()

            if response.startswith("SUCCESS:"):
                print(f"Thread {thread_title} removed by {self.username} ")
            else:
                print(response[7:])

        elif parts[0] == "XIT":
            if len(parts) != 1:
                print("Incorrect syntax for XIT. Usage: XIT")
                return 
            
            message = f"XIT {self.username}"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))

            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()

            if response.startswith("SUCCESS:"):
                print(f"User {self.username} logged out ")
            else:
                print(response[7:])
            sys.exit(0)


        elif parts[0] == 'UPD':
            if len(parts) != 3:
                print("Incorrect syntax for UPD. Usage: UPD threadtitle filename")
                return
                
            thread_title = parts[1]
            filename = parts[2]
            
            # Check if the file exists
            try:
                with open(filename, 'rb') as file:
                    pass
            except FileNotFoundError:
                print(f"Error: File {filename} not found")
                return
                
            message = f"UPD {thread_title} {self.username} {filename}"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                # File upload approved, establish TCP connection to transfer the file
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_socket.connect((self.server_ip, self.server_port))
                
                with open(filename, 'rb') as file:
                    file_data = file.read()
                    self.tcp_socket.sendall(file_data)
                    
                # Close TCP connection after file transfer
                self.tcp_socket.close()
                self.tcp_socket = None
                
                # Wait for final confirmation from server
                data, _ = self.udp_socket.recvfrom(1024)
                response = data.decode()
                
                if response.startswith("SUCCESS:"):
                    print(f"File {filename} uploaded successfully")
                else:
                    print(response[7:])
            else:
                print(response[7:])

        elif parts[0] == 'DWN':
            if len(parts) != 3:
                print("Incorrect syntax for DWN. Usage: DWN threadtitle filename")
                return
                
            thread_title = parts[1]
            filename = parts[2]
            
            message = f"DWN {thread_title} {self.username} {filename}"
            self.udp_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            
            data, _ = self.udp_socket.recvfrom(1024)
            response = data.decode()
            
            if response.startswith("SUCCESS:"):
                
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_socket.connect((self.server_ip, self.server_port))
                
                # Receive and write file data
                file_data = b''
                while True:
                    packet = self.tcp_socket.recv(4096)
                    if not packet:
                        break
                    file_data += packet
                
                self.tcp_socket.close()
                self.tcp_socket = None
                
                with open(filename, 'wb') as file:
                    file.write(file_data)
                
                print(f"File {filename} downloaded successfully")
            else:
                print(response[7:])
        
        else:
            print("Invalid Command")
        

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python client.py server_port")
        sys.exit(1)
    
    server_port = int(sys.argv[1])
    client = ForumClient(server_port)
    client.start()