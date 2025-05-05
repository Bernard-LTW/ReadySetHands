# ReadySetHands 🖐️

A real-time virtual hand-raising system for classrooms and educational settings. This web application allows teachers to create sessions and students to join them, providing an organized way to manage student participation.

## Features

- **Session Management**
  - Teachers can create multiple sessions
  - Each session has a unique 6-character code
  - Real-time queue updates using WebSockets
  - Teachers can clear the queue or delete sessions

- **Student Features**
  - Easy session joining with session codes
  - Simple hand-raising interface
  - Real-time queue position updates
  - Visual feedback for hand-raised status

- **Real-time Updates**
  - Instant queue updates for all participants

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Bernard-LTW/ReadySetHands.git
cd ReadySetHands
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables (optional):
```bash
export HOST_PASSWORD="your_secure_password"  # Default: defaultpassword
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Usage

### For Teachers

1. Navigate to `/host` and enter the host password
2. Create a new session using the "Create New Session" button
3. Share the generated session code with your students
4. Monitor the queue of raised hands
5. Use "Clear Queue" to reset all raised hands
6. Delete sessions when they're no longer needed

### For Students

1. Navigate to the home page
2. Enter the session code provided by your teacher
3. Enter your name
4. Use the "Raise Hand" button to join the queue
5. Your position in the queue will be displayed and updated in real-time

## Technical Stack

- **Backend**: Flask + Flask-SocketIO
- **Database**: SQLite + SQLAlchemy
- **Frontend**: HTML, JavaScript, Bootstrap 5
- **Real-time Communication**: Socket.IO


