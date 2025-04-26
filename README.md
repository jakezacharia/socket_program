# Socket Transaction System

A Python-based client-server transaction system built with sockets that simulates a simple cryptocurrency exchange between predefined users.

## Features

- Client-server architecture using Python's socket library
- Multi-threaded server supporting concurrent client connections
- User authentication system
- Transaction processing between users with balance tracking
- Support for split payments to multiple recipients
- Transaction history tracking

## System Components

### Server (server.py)
- Handles user authentication
- Manages user balances
- Processes transaction requests
- Maintains transaction history
- Supports multiple concurrent connections

### Client (client.py)
- User login interface
- Transaction creation functionality
- Balance and transaction history display
- Split payment capabilities

## Getting Started

### Prerequisites
- Python 3.x

### Running the Application

1. Start the server:
   ```
   python server.py
   ```

2. In a separate terminal, start the client:
   ```
   python client.py
   ```

### Predefined Users

The system comes with the following predefined users (username and password are identical):
- Username: A, Password: A, Initial balance: 10 BTC
- Username: B, Password: B, Initial balance: 10 BTC
- Username: C, Password: C, Initial balance: 10 BTC
- Username: D, Password: D, Initial balance: 10 BTC

## Usage Flow

1. Log in with one of the predefined users
2. View your balance and transaction history
3. Make a transaction to one or two recipients
4. View updated balance and transaction history
5. Quit the program when done

## Transaction Types

- Single recipient: Transfer funds to one user
- Split payment: Transfer funds to two different users with customizable amounts

## Technical Implementation

The application uses:
- Socket programming for network communication
- Threading for concurrent client connections
- Pickle for object serialization
- Custom User and Transaction classes for data management
