import socket

def test_kaillera_connection(host: str, port: int = 27888):
    """Simple test of Kaillera connection"""
    print("=" * 60)
    print(f"Testing Kaillera Connection to {host}:{port}")
    print("=" * 60)
    
    try:
        print("[1] Creating UDP socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10.0)
        print("    ✓ Socket created")
        
        print(f"[2] Sending HELLO message...")
        hello_msg = b"HELLO0.83"
        sock.sendto(hello_msg, (host, port))
        print(f"    ✓ Sent: {hello_msg}")
        
        print(f"[3] Waiting for response (10s timeout)...")
        
        try:
            data, addr = sock.recvfrom(1024)
            print(f"    ✓ Received {len(data)} bytes from {addr}")
            response = data.decode('latin-1', errors='ignore')
            print(f"    Response: {response}")
            
            if response.startswith("HELLOD00D"):
                new_port = int(response[9:13])
                print(f"    ✓ Server responded with new port: {new_port}")
                print(f"    ✓ Connection test PASSED!")
                print(f"    ✓ Server is running Kaillera 0.83")
                return True
            elif response.startswith("TOO"):
                print(f"    ✗ Server responded: TOO (server full or busy)")
                return False
            else:
                print(f"    ? Unknown response: {response}")
                return False
                
        except socket.timeout:
            print(f"    ✗ TIMEOUT: No response from server")
            print()
            print("POSSIBLE REASONS:")
            print("   1. Server is NOT running on this port")
            print("  2. Firewall is blocking UDP packets")
            print("   3. Server port is different from 27888")
            print("  4. Network issue (cannot reach server)")
            return False
            
        except socket.error as e:
            print(f"    ✗ SOCKET ERROR: {type(e).__name__}: {e}")
            print(f"    Error: {e}")
            return False
            
    finally:
        try:
            sock.close()
        except:
            pass
    
    print("=" * 60)
    return False


if __name__ == "__main__":
    import sys
    
    host = "kayinremix.duckdns.org"
    port = 27888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    success = test_kaillera_connection(host, port)
    
    print()
    if success:
        print("✓ TEST PASSED - You can connect to the Kaillera server!")
        print("  The headless recorder should work.")
    else:
        print("✗ TEST FAILED - Cannot connect to the Kaillera server")
        print()
        print("TROUBLESHOOTING TIPS:")
        print("  1. Verify the server is running on the same machine")
        print("  2. Check if the server port is 27888 (not 8080, 80, etc.)")
        print("  3. Disable Windows Firewall temporarily")
        print(" 4. Try pinging the server: ping kayinremix.duckdns.org")
        print("  5. Ask the server administrator about firewall settings")
    
    input("\n\nPress Enter to exit...")
