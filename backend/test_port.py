#!/usr/bin/env python3
import socket
import sys

def test_port(host: str, port: int, timeout: int = 5):
    """Test if a UDP port is reachable"""
    print(f"Testing UDP connection to {host}:{port}")
    print("=" * 50)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Send a simple Kaillera HELLO message
        hello_msg = b"HELLO0.83"
        print(f"Sending HELLO message: {hello_msg}")
        
        print(f"Sending to {host}:{port}...")
        sock.sendto(hello_msg, (host, port))
        print("Message sent, waiting for response...")
        
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✓ Received {len(data)} bytes from {addr}")
            print(f"Response: {data[:50]}...")
            
            # Try to parse as Kaillera response
            if data.startswith(b"HELLO"):
                print(f"Response starts with: {data[:10]}")
                if data.startswith(b"HELLOD00D"):
                    port_bytes = data[9:13]
                    new_port = int.from_bytes(port_bytes, byteorder='little')
                    print(f"✓ Valid HELLOD00D response!")
                    print(f"  New game port: {new_port}")
                    return True
                elif data.startswith(b"TOO"):
                    print("✓ Server responded: TOO (server full)")
                    return True
                else:
                    print(f"? Unknown HELLO response format")
                    return False
            else:
                print(f"? Non-Kaillera response: {data[:30]}")
                return False
                
        except socket.timeout:
            print(f"✗ TIMEOUT: No response after {timeout} seconds")
            print("\nThis means:")
            print("  1. The server is NOT running on this port")
            print("  2. A firewall is blocking UDP port", port)
            print("  3. The server is not responding to Kaillera HELLO messages")
            return False
            
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass
    
    return False


def main():
    print("Kaillera Port Test Tool")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = input("Enter server host (default: kayinremix.duckdns.org): ").strip() or "kayinremix.duckdns.org"
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port_input = input("Enter server port (default: 27888): ").strip()
        port = int(port_input) if port_input else 27888
    
    success = test_port(host, port)
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Test PASSED - Server is responding to Kaillera!")
        print("  The headless recorder should be able to connect.")
    else:
        print("✗ Test FAILED - Server is NOT responding")
        print("\nTroubleshooting:")
        print("  1. Verify the Kaillera server is running")
        print("  2. Check the port is correct (usually 27888)")
        print("  3. Check firewall settings on both client and server")
        print("  4. Verify the server implements Kaillera protocol")
        print("  5. Try: ping", host, "to check DNS")
        print("  6. Try: netstat -an | findstr", port, "to check local listening ports")
    print("=" * 50)


if __name__ == '__main__':
    main()
