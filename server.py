import socket
import os
import threading
import queue
class ForumServer:
    def __init__(self, server_port):
        self.server_port = server_port
        self.udp_socket = None
        self.tcp_socket = None
        self.credentials_file = "credentials.txt"
        self.active_users = set()  # For tracking currently logged in users
        self.threads = {}  # Dictionary to store active threads (title: creator)
        self.request_queue = queue.Queue()
        self.pending_auth = {}

    def start(self):
        # Set up UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', self.server_port))
        
        # Set up TCP socket for file transfers
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind(('', self.server_port))
        self.tcp_socket.listen(5)
        
        print(f"Python Server {self.server_port}")
        print("Waiting for clients")

        threading.Thread(target=self.process_queue, daemon=True).start() 

        while True:
            data, client_address = self.udp_socket.recvfrom(1024)
            message = data.decode()
            self.request_queue.put((message,client_address))       

#---------------------------------------------------------------------------------
    def process_queue(self):
        while True:
            message, client_address = self.request_queue.get()
            try:
                if client_address in self.pending_auth:
                    username = self.pending_auth.pop(client_address)
                    self.handle_authentication(f"{username}:{message}", client_address)
                elif message.startswith("AUTH:"):
                    self.handle_authentication(message[5:], client_address)
                elif message.startswith("CRT"):
                    self.handle_command(message, client_address)
                elif message.startswith("LST"):
                    self.handle_command(message, client_address)
                elif message.startswith("MSG"):
                    self.handle_command(message, client_address)
                elif message.startswith("DLT"):
                    self.handle_command(message, client_address)
                elif message.startswith("EDT"):
                    self.handle_command(message, client_address)
                elif message.startswith("RDT"):
                    self.handle_command(message, client_address)
                elif message.startswith("RMV"):
                    self.handle_command(message, client_address)
                elif message.startswith("XIT"):
                    self.handle_command(message, client_address)
                elif message.startswith("UPD"):
                    self.handle_command(message, client_address)
                elif message.startswith("DWN"):
                    self.handle_command(message, client_address)
            except Exception as e:
                print(f"Error processing request: {e}")

#-------------------------------------------------------------------------------------------------------

    def handle_authentication(self, input_data, client_address):
        if ':' in input_data:
            username, password = input_data.split(':', 1)
            user_found = False
            try:
                with open(self.credentials_file, 'r') as file:
                    for line in file:
                        stored_username, stored_pwd = line.strip().split()
                        if stored_username == username:
                            user_found = True
                            if stored_pwd == password:
                                self.active_users.add(username)
                                self.udp_socket.sendto("SUCCESS: Welcome to the forum".encode(), client_address)
                                print(f"{username} successful login")
                            else:
                                self.udp_socket.sendto("ERROR: Invalid password".encode(), client_address)
                            return
            except FileNotFoundError:
                pass
            if not user_found:
                # Create user
                with open(self.credentials_file, 'a') as file:
                    file.write(f"{username} {password}\n")
                self.active_users.add(username)
                self.udp_socket.sendto("SUCCESS: Account created. Welcome to the forum".encode(), client_address)
                print(f"New user {username} created")
        else:
            # First stage: only username provided
            print(f'Client Authenticating')
            username = input_data
            if username in self.active_users:
                print(f'{username} has already logged in')
                self.udp_socket.sendto(f"ERROR: {username} has already logged in".encode(), client_address)
                return

            try:
                with open(self.credentials_file, 'r') as file:
                    for line in file:
                        stored_username, _ = line.strip().split()
                        if stored_username == username:
                            self.pending_auth[client_address] = username
                            self.udp_socket.sendto("PASSWORD:".encode(), client_address)
                            return
            except FileNotFoundError:
                open(self.credentials_file, 'a').close()

            # New user
            self.pending_auth[client_address] = username
            self.udp_socket.sendto("NEWUSER:".encode(), client_address)

#-------------------------------------------------------------------------------------------------------
      
    def handle_command(self, message, client_address):
        
        parts = message.split(' ', 1) 
        command = parts[0]
        
        if command == "CRT":
            if len(parts) < 2:
                response = "ERROR: Incorrect syntax for CRT"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            # Parse the thread title and username
            args = parts[1].split(' ')
            if len(args) < 2:
                response = "ERROR: Missing arguments for CRT"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            thread_title = args[0]
            username = args[1]
            print(f'{username} issued CRT command')
            
            # Check if thread already exists in our active threads
            if thread_title in self.threads:
                response = f"ERROR: Thread {thread_title} exists"
                self.udp_socket.sendto(response.encode(), client_address)
                print(f"Thread {thread_title} exists")
                return
            

            # Create the thread file
            try:
                with open(thread_title, 'w') as file:
                    file.write(f"{username}\n")  # First line is the creator's username
                
                
                self.threads[thread_title] = username
                
                response = f"SUCCESS: Thread {thread_title} created"
                self.udp_socket.sendto(response.encode(), client_address)
                print(f"Thread {thread_title} created")
            except Exception as e:
                response = f"ERROR: Failed to create thread: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)    
        
        elif command == "LST":
            if len(parts) > 1:
                response = "ERROR: Incorrect syntax for LST"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            if self.threads:
                response = "SUCCESS:\n" + "\n".join(self.threads.keys())
            else:
                response = "SUCCESS: No threads to list"
            self.udp_socket.sendto(response.encode(), client_address)
            
        elif command == "MSG":
            args = parts[1].split(' ', 1)  
            if len(args) < 2:
                response = "ERROR: Incorrect syntax for MSG"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            thread_title = args[0]
            msg_and_username = args[1].split(' ', 1) 

            if len(msg_and_username) < 2:
                response = "ERROR: Incorrect syntax for MSG"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            msg = msg_and_username[1]
            username = msg_and_username[0]
            print(f'{username} issued MSG command')

            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            try:
                with open(thread_title, 'r') as file:
                    lines = file.readlines()
                    message_number = 1
                    for line in lines[1:]: 
                        if line.startswith(tuple(str(i) + " " for i in range(1, len(lines)))): 
                            try:
                                current_number = int(line.split(' ')[0])
                                message_number = max(message_number, current_number + 1)
                            except ValueError:
                                pass 
                with open(thread_title, 'a') as file:
                    file.write(f"{message_number} {username}: {msg}\n")
                response = "SUCCESS: Message posted"
                print(f'Message posted to {thread_title} thread')
                self.udp_socket.sendto(response.encode(), client_address)

            except Exception as e:
                response = f"ERROR: Failed to post message: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)
        
        elif command == "DLT":
            
            args = parts[1].split(' ',1) 

            thread_title = args[0]
            msg_no_username = args[1].split(' ',1)

            
            if len(msg_no_username)<2:
                response = f"ERROR: Incorrect Syntax for DLT"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            msgnumber = msg_no_username[1]
            username = msg_no_username[0]

            print(f'{username} issued DLT command')

            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            try:
                msgnumber = int(msgnumber)
            except ValueError:
                response = f"ERROR: Invalid message number"
                self.udp_socket.sendto(response.encode(),client_address)
                return

            try: 
                with open(thread_title, 'r') as file:
                    lines = file.readlines()
                    updated_lines = [lines[0]] 
                    deleted = False
                    for line in lines[1:]:
                        if line.startswith(f"{msgnumber} "):
                            message_username = line.split(' ')[1].replace(':', '')
                            if message_username == username:
                                deleted = True
                            else:
                                updated_lines.append(line)
                        else:
                            updated_lines.append(line) 

                    if deleted:
                        with open(thread_title, 'w') as file:
                            file.writelines(updated_lines)
                        response = f"SUCCESS: Message {msgnumber} deleted."
                        print(f'message deleted of Thread {thread_title} by {username}')
                    else:
                        response = f"ERROR: Message {msgnumber} not found or you are not the author."
                        print(f'message cannot be deleted')
                    self.udp_socket.sendto(response.encode(), client_address)

            except Exception as e:
                response = f"ERROR: Failed to delete message: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)

        elif command == "EDT":
            
            args = parts[1].split(' ',1) 

            if len(args) < 2:
                response = f"ERROR: Incorrect Syntax for EDT"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            thread_title = args[0]
            edit_args = args[1].split(' ',2)
            print('thread_title', thread_title)
            
            if len(edit_args) < 3:
                response = f"ERROR: Incorrect Syntax for EDT"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            username = edit_args[0]
            msgnumber = int(edit_args[1])
            msg = edit_args[2]
            if not msg:
                response = f"ERROR: Incorrect Syntax for EDT"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            print(f'{username} issued EDT command')

            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            try:
                msgnumber = int(msgnumber)
            except ValueError:
                response = f"ERROR: Invalid message number"
                self.udp_socket.sendto(response.encode(),client_address)
                return
            try: 
                with open(thread_title, 'r') as file:
                    lines = file.readlines()
                    updated_lines = [lines[0]] 
                    edited = False
                    for line in lines[1:]:
                        if line.startswith(f"{msgnumber} "):
                            message_username = line.split(' ')[1].replace(':', '')
                            if message_username == username:
                                updated_lines.append(f"{msgnumber} {username}: {msg}\n")
                                edited = True
                            else:
                                updated_lines.append(line)
                        else:
                            updated_lines.append(line) 

                    if edited:
                        with open(thread_title, 'w') as file:
                            file.writelines(updated_lines)
                        response = f"SUCCESS: Message {msgnumber} edited."
                        print(f'message edited in Thread {thread_title} by {username}')
                    else:
                        response = f"ERROR: Message {msgnumber} not found or you are not the author."
                        print(f'message cannot be edited')
                    self.udp_socket.sendto(response.encode(), client_address)

            except Exception as e:
                response = f"ERROR: Failed to edit the message: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)

        elif command == "RDT":
            if len(parts) < 2:
                response = "ERROR: Incorrect syntax for RDT. Usage: RDT thread_title"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            thread_title = parts[1]
            
            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            try:
                with open(thread_title, 'r') as file:
                    lines = file.readlines()
                    if len(lines) > 1:
                        content = "".join(lines[1:])  
                        response = f"SUCCESS:\n{content}"
                    else:
                        response = "SUCCESS: Thread is empty."
                    print(f'Thread {thread_title} read')
                    self.udp_socket.sendto(response.encode(), client_address)
            except Exception as e:
                response = f"ERROR: Failed to read thread: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)

        elif command == "RMV":
            if len(parts) < 2:
                response = "ERROR: Incorrect syntax for RMV. Usage: RMV thread_title"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            args = parts[1].split(' ',1)
            username = args[0]
            thread_title = args[1]
            
            print(f'{username} issued RMV command')

            if thread_title == self.credentials_file or thread_title=='credentials':
                response = "ERROR: you cannot remove this file"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            

            try:
                with open(thread_title, 'r') as file:
                    creator_username = file.readline().strip()
            except Exception as e:
                response = f"ERROR: Could not read thread creator: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)
                return

            if creator_username != username:
                response = f"ERROR: Only the creator ({creator_username}) can remove this thread."
                self.udp_socket.sendto(response.encode(), client_address)
                return

            try:
                os.remove(thread_title)
                if thread_title in self.threads:
                    del self.threads[thread_title]
                response = f"SUCCESS: Thread {thread_title} removed."
                self.udp_socket.sendto(response.encode(), client_address)
                print(f"Thread {thread_title} removed by {username}")
            except Exception as e:
                response = f"ERROR: Failed to remove thread: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)

        elif command == 'XIT':

            if len(parts) > 2:
                response = "ERROR: Incorrect syntax for XIT"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            username = parts[1]
            
            try:    
                self.active_users.remove(username)
                response = f"SUCCESS: {username} logged out"
                self.udp_socket.sendto(response.encode(), client_address)
                print(f'{username} exited')
            except Exception as e:
                response = f"ERROR: unable to logout"
                self.udp_socket.sendto(response.encode(), client_address)

        elif message.startswith("UPD"):
            
            parts = message.split(' ', 3) 
            if len(parts) < 4:
                response = "ERROR: Incorrect syntax for UPD"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            thread_title = parts[1]
            username = parts[2]
            filename = parts[3]
            
            print(f'{username} issued UPD command')


            if thread_title not in self.threads:
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            
                
            
            server_side_filename = f"{thread_title}-{filename}"
            if os.path.exists(server_side_filename):
                response = f"ERROR: File {filename} already exists in thread {thread_title}"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            
            response = f"SUCCESS: Ready to receive file {filename}"
            self.udp_socket.sendto(response.encode(), client_address)
            
            # Accept TCP connection for file transfer
            client_socket, _ = self.tcp_socket.accept()
            
            # Receive file data
            file_data = b''
            while True:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                file_data += packet
                
            # Close TCP connection
            client_socket.close()
            
            # Write file data to server-side file
            try:
                with open(server_side_filename, 'wb') as file:
                    file.write(file_data)
                    
                # Update thread file to include upload record
                with open(thread_title, 'a') as thread_file:
                    thread_file.write(f"{username} uploaded {filename}\n")
                
                response = f"SUCCESS: File {filename} uploaded to thread {thread_title}"
                self.udp_socket.sendto(response.encode(), client_address)
                print(f"File {filename} uploaded to thread {thread_title} by {username}")
            except Exception as e:
                response = f"ERROR: Failed to save file: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)
        
        elif message.startswith("DWN"):
            
            parts = message.split(' ', 3)  
            if len(parts) < 4:
                response = "ERROR: Incorrect syntax for DWN"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            thread_title = parts[1]
            username = parts[2]
            filename = parts[3]
            print(f'{username} issued DWN command')
            if not os.path.exists(thread_title):
                response = f"ERROR: Thread {thread_title} does not exist"
                self.udp_socket.sendto(response.encode(), client_address)
                return
            
            server_side_filename = f"{thread_title}-{filename}"
            if not os.path.exists(server_side_filename):
                response = f"ERROR: File {filename} not found in thread {thread_title}"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            file_was_uploaded = False
            try:
                with open(thread_title, 'r') as thread_file:
                    for line in thread_file:
                        if line.strip().endswith(f"uploaded {filename}"):
                            file_was_uploaded = True
                            break
            except Exception as e:
                response = f"ERROR: Failed to check file record: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            if not file_was_uploaded:
                response = f"ERROR: File {filename} not found in thread {thread_title}"
                self.udp_socket.sendto(response.encode(), client_address)
                return
                
            response = f"SUCCESS: Ready to send file {filename}"
            self.udp_socket.sendto(response.encode(), client_address)
            
            
            client_socket, _ = self.tcp_socket.accept()
            
            
            try:
                with open(server_side_filename, 'rb') as file:
                    file_data = file.read()
                    client_socket.sendall(file_data)
                
                client_socket.close()
                
                print(f"File {filename} downloaded from thread {thread_title} by {username}")
            except Exception as e:
                client_socket.close()
                response = f"ERROR: Failed to send file: {str(e)}"
                self.udp_socket.sendto(response.encode(), client_address)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 server.py server_port")
        sys.exit(1)
    
    server_port = int(sys.argv[1])
    server = ForumServer(server_port)
    server.start()