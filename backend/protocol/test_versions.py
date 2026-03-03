import socket
import struct
import asyncio
from typing import Optional, Callable

class KailleraProtocolVersion:
    """Kaillera protocol version to use"""
    V0_83 = 0
    V0_84 = 1
    V0_85 = 2


class KailleraClientSimple:
    """Simplified Kaillera client for debugging"""
    
    def __init__(self, version: KailleraProtocolVersion = KailleraProtocolVersion.V0_83):
        self.version = version
        self.username = "HeadlessRecorder"
        self.emulator = "HeadlessRecorder"
        self.connection_type = 3  # Good
        
        self.socket: Optional[socket.socket] = None
        self.game_socket: Optional[socket.socket] = None
        self.connected = False
        self.game_port: Optional[int] = None
        self.on_status_update: Optional[Callable] = None
        on_error: Optional[Callable] = None
    
    def get_hello_message(self) -> bytes:
        if self.version == KailleraProtocolVersion.V0_83:
            return b"HELLO0.83"
        elif self.version == KailleraProtocolVersion.V0_84:
            return b"HELLO0.84"
        elif self.version == KailleraProtocolVersion.V0_85:
            return b"HELLO0.85"
        else:
            return b"HELLO0.83"
    
    def parse_hello_response(self, data: bytes):
        if not data:
            return False, None
        
        data_str = data.decode('latin-1', errors='ignore')
        print(f"  [Protocol] Response: {data_str}")
        
        if data_str.startswith("HELLOD00D"):
            try:
                port_str = data_str[9:]
                port = int(port_str)
                print(f"  [Protocol] New game port: {port}")
                return True, port
            except ValueError as e:
                print(f"  [Protocol] Error parsing port: {e}")
                return False, None
        elif data_str.startswith("TOO"):
            print(f"  [Protocol] Server is full or too busy")
            return False, None
        else:
            print(f"  [Protocol] Unknown response: {data_str}")
            return False, None
    
    async def connect(self, host: str, port: int = 27888) -> bool:
        print(f"  [Client] Connecting to {host}:{port}")
        print(f"  [Client] Protocol version: {self.version}")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            print(f"  [Client] UDP socket created")
            
            # Send HELLO
            hello_msg = self.get_hello_message()
            print(f"  [Client] Sending HELLO: {hello_msg}")
            self.socket.sendto(hello_msg, (host, port))
            print(f"  [Client] HELLO sent")
            
            # Wait for response
            print(f"  [Client] Waiting for response (5s timeout)...")
            data, addr = self.socket.recvfrom(1024)
            print(f"  [Client] Received {len(data)} bytes from {addr}")
            print(f"  [Client] Response: {data}")
            
            success, new_port = self.parse_hello_response(data)
            
            if not success:
                print(f"  [Client] HELLO failed")
                return False
            
            self.game_port = new_port
            print(f"  [Client] HELLO successful, game port: {self.game_port}")
            
            # Connect to game port
            self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.game_socket.settimeout(5.0)
            print(f"  [Client] Game socket created on port {self.game_port}")
            
            self.connected = True
            return True
            
        except socket.timeout:
            print(f"  [Client] TIMEOUT: No response after 5 seconds")
            if self.on_error:
                self.on_error(f"Connection timeout - no response from {host}:{port}")
            return False
        except socket.error as e:
            print(f"  [Client] SOCKET ERROR: {type(e).__name__}: {e}")
            if self.on_error:
                self.on_error(f"Socket error: {e}")
            return False
        except Exception as e:
            print(f"  [Client] ERROR: {type(e).__name__}: {e}")
            import traceback
            print(f"  [Client] Traceback:")
            traceback.print_exc()
            if self.on_error:
                self.on_error(f"Unexpected error: {e}")
            return False
    
    def disconnect(self):
        if self.game_socket:
            self.game_socket.close()
        if self.socket:
            self.socket.close()
        self.connected = False
        print(f"  [Client] Disconnected")


async def test_versions(host: str, port: int = 27888):
    """Test all Kaillera protocol versions"""
    versions = [
        (KailleraProtocolVersion.V0_83, "0.83"),
        (KailleraProtocolVersion.V0_84, "0.84"),
        (KailleraProtocolVersion.V0_85, "0.85"),
    ]
    
    for version_num, version in versions:
        print("\n" + "=" * 60)
        print(f"Testing version {version_num}: {version}")
        print("=" * 60)
        
        client = KailleraClientSimple(version)
        
        # Setup callbacks
        def on_error(err):
            print(f"  [Error] {err}")
        
        client.on_error = on_error
        
        # Try to connect
        success = await client.connect(host, port)
        
        client.disconnect()
        
        if success:
            print(f"✓ Version {version} SUCCESS")
        else:
            print(f"✗ Version {version} FAILED")


async def main():
    import sys
    
    host = "kayinremix.duckdns.org"
    port = 27888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    print("=" * 60)
    print("Kaillera Protocol Version Tester")
    print("=" * 60)
    print()
    print(f"Testing: {host}:{port}")
    print(f"Testing all Kaillera protocol versions...")
    print()
    
    await test_versions(host, port)
    
    print()
    print("=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
