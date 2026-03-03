#!/usr/bin/env python3
import socket
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol.kaillera_client import KailleraClient

def test_connection(host: str, port: int):
    """Test connection to a Kaillera server"""
    print(f"Testing connection to {host}:{port}")
    print("=" * 50)
    
    client = KailleraClient()
    
    def on_status_update(status):
        print(f"Status update received:")
        print(f"  Users: {status.users}")
        print(f"  Games: {status.games}")
        print(f"  User list: {len(status.user_list)} users")
        print(f"  Game list: {len(status.game_list)} games")
    
    def on_error(error):
        print(f"ERROR: {error}")
    
    client.on_status_update = on_status_update
    client.on_error = on_error
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("\n1. Attempting to connect...")
        success = loop.run_until_complete(client.connect(host, port))
        
        if success:
            print(f"✓ Connected successfully!")
            print(f"  Connected: {client.connected}")
            print(f"  Game port: {client.game_port}")
            
            print("\n2. Getting server status...")
            status = loop.run_until_complete(client.update_status(host))
            
            print("\n3. Disconnecting...")
            client.disconnect()
            print("✓ Disconnected")
        else:
            print("✗ Connection failed")
        
        loop.close()
        
        return success
        
    except Exception as e:
        print(f"✗ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("Kaillera Connection Test Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = input("Enter server host (default: 127.0.0.1): ").strip() or "127.0.0.1"
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port_input = input("Enter server port (default: 27888): ").strip()
        port = int(port_input) if port_input else 27888
    
    success = test_connection(host, port)
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Test PASSED - Connection successful!")
    else:
        print("✗ Test FAILED - Could not connect")
        print("\nTroubleshooting tips:")
        print("1. Verify the Kaillera server is running")
        print("2. Check the host and port are correct")
        print("3. Verify firewall settings")
        print("4. Try ping the server first")
    print("=" * 50)


if __name__ == '__main__':
    main()
