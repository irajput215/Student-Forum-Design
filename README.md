# COMP9331 Assignment – Student Forum

This project is a simple client-server discussion forum system built as part of the COMP9331 assignment. It supports basic forum features like thread creation, messaging, and file uploads/downloads. The system uses a combination of **UDP** (for command communication) and **TCP** (for file transfers) protocols.

## 🛠 Features

- **User Authentication** (Login/Register)
- **Thread Management** (Create, Read, Delete)
- **Messaging** (Post, Edit, Delete messages)
- **File Transfer** (Upload/Download with TCP)
- Command-line interface for client interaction
- Custom Application Layer Protocol for networking

## 📁 Project Structure

- `ForumServer.py`: Server-side code
- `ForumClient.py`: Client-side code
- `credentials.txt`: Stores user credentials
- `thread_files/`: Stores all forum threads and files

## ⚙️ Protocol Summary

### Authentication

- `AUTH:{username}` ➝ Server checks and responds
- `PASSWORD:` or `NEWUSER:` ➝ Client sends password
- `SUCCESS:` or `ERROR:` based on validity

### Commands Supported

- `CRT`, `LST`, `MSG`, `DLT`, `EDT`, `RDT`, `RMV`, `XIT`
- `UPD` and `DWN` for file transfer over TCP

## 📄 Report

Read the full implementation and design details here:

📎 [COMP9331 Assignment Report](./report.pdf)

---

## 🔐 Known Limitations

- Passwords stored in plain text
- No encryption or session timeout
- No size limit for threads/messages/files
- Basic error handling for packet loss

## 📦 Tech Stack

- Python (Sockets, Threading)
- TCP/UDP
- File I/O

---

## 💡 Future Improvements

- Add encryption for credentials and network traffic
- Move storage to SQLite or JSON
- Better error handling and logging
- Introduce GUI for easier client use
