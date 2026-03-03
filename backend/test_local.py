import socket

def test_connection(host: str, port: int = 27888, timeout: int = 10) -> bool:
    """Test UDP connection to Kaillera server"""
    print(f"\n{'='*60}")
    print(f"Testing Kaillera Server")
    print(f"{'='*60}")
    print(f"Server: {host}:{port}")
    print(f"Timeout: {timeout}s")
    print(f"{'='*60}\n")
    
    try:
        print("[1] Creating UDP socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        print("    ✓ Socket created")
        
        print(f"[2] Sending HELLO message to {host}:{port}...")
        hello_msg = b"HELLO0.83"
        sock.sendto(hello_msg, (host, port))
        print(f"    ✓ Sent: {hello_msg}")
        print(f"    Size: {len(hello_msg)} bytes")
        
        print(f"[3] Waiting for response (timeout: {timeout}s)...")
        
        try:
            data, addr = sock.recvfrom(1024)
            received_from = addr[0]
            received_port = addr[1]
            
            print(f"    ✓ Received {len(data)} bytes")
            print(f"    ✓ From: {received_from}:{received_port}")
            
            # Parse response
            response = data.decode('latin-1', errors='ignore')
            print(f"[4] Parsing response...")
            print(f"    Raw response: {response}")
            
            if response.startswith("HELLOD00D"):
                port_bytes = response[9:13]
                new_port = int(port_bytes)
                print(f"    ✓ HELLOD00D detected")
                print(f"    ✓ New game port: {new_port}")
                print(f"\n{'='*60}")
                print(f"✓ TEST PASSED - Server is running Kaillera 0.83")
                print(f"✓ Connection to {new_port} port required for game data")
                print(f"{'='*60}\n")
                return True
            elif response.startswith("TOO"):
                print(f"    ✓ TOO detected")
                print(f"\n{'='*60}")
                print(f"✓ Server responded but is FULL or BUSY")
                print(f"{'='*60}\n")
                return False
            else:
                print(f"    ? Unknown response format")
                print(f"    First 20 chars: {response[:20]}")
                print(f"\n{'='*60}")
                print(f"✓ Server is responding but with unexpected format")
                print(f"{'='*60}\n")
                return False
                
        except socket.timeout:
            print(f"    ✗ TIMEOUT: No response after {timeout}s")
            print(f"\n{'='*60}")
            print(f"✗ TEST FAILED - TIMEOUT")
            print(f"{'='*60}")
            print(f"\nPOSSIBLE REASONS:")
            print(f"  1. Server is NOT running on {host}:{port}")
            print(f"  2. Firewall is blocking UDP port {port}")
            print(f"  3. Router/Network is blocking traffic")
            print(f"  4. Server is not responding to Kaillera HELLO")
            print(f"  5. Server is using different port than {port}")
            print(f"  6. Server is not a Kaillera server")
            print(f"\nTROUBLESHOOTING:")
            print(f"  - Verify server is running on {host}")
            print(f"  - Check Windows Firewall (UDP port {port})")
            print(f"  - Test with: ping {host}")
            print(f"  - Test with: netstat -an | findstr :{port}")
            print(f"  - Check if server port is {port} (not 8080)")
            print(f"{'='*60}\n")
            return False
            
    except socket.error as e:
        print(f"    ✗ SOCKET ERROR: {type(e).__name__}")
        print(f"    Error: {e}")
        print(f"\n{'='*60}")
        print(f"✗ TEST FAILED - SOCKET ERROR")
        print(f"{'='*60}")
        print(f"\nPOSSIBLE REASONS:")
        print(f"  - Cannot create UDP socket")
        print(f"  - Network interface issue")
        print(f"  - Socket permission denied")
        print(f"\nTROUBLESHOOTING:")
        print(f"  - Check if Python has network access")
        print(f"  - Try running as administrator")
        print(f"  - Disable VPN/proxy if active")
        print(f"{'='*60}\n")
        return False
            
    except Exception as e:
        print(f"    ✗ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"    Error: {e}")
        import traceback
        print(f"    Traceback:")
        traceback.print_exc()
        print(f"\n{'='*60}")
        print(f"✗ TEST FAILED - UNEXPECTED ERROR")
        print(f"{'='*60}\n")
        return False
            
    finally:
        try:
            sock.close()
        except:
            pass


if __name__ == "__main__":
    import sys
    
    host = "192.168.178.55"
    port = 27888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    print(f"\nLOCAL NETWORK SERVER DETECTED")
    print(f"Server IP: {host} (local network)")
    print(f"Server Port: {port}")
    print(f"\nMake sure:")
    print(f"  - Server is RUNNING on {host}:{port}")
    print(f"  - You can reach {host} (ping works)")
    print(f"  - Windows Firewall allows UDP on port {port}\n")
    
    success = test_connection(host, port)
    
    if success:
        print("\n✓ SUCCESS - Server is accessible!")
        print("  The headless recorder should be able to connect.")
        print("  Update server configuration to use 192.168.178.55:27888")
    else:
        print("\n✗ FAILED - Cannot connect to server")
        print("\nNEXT STEPS:")
        print("  1. Verify server is running on 192.168.178.55:27888")
        print("  2. Ping the server: ping 192.168.178.55")
        print("  3. Check firewall: netstat -an | findstr 27888")
        print("  4. Try disabling Windows Firewall temporarily")
        print("  5. Check router logs if needed")
