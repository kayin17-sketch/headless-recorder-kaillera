import socket
import asyncio
import struct
from typing import Optional, Callable, Dict, Any
from .kaillera_protocol import KailleraProtocol, MessageType, ServerStatus, KailleraMessage


class KailleraClient:
    def __init__(self):
        self.protocol = KailleraProtocol()
        self.socket: Optional[socket.socket] = None
        self.game_socket: Optional[socket.socket] = None
        self.connected = False
        self.game_port: Optional[int] = None
        self.username = "HeadlessRecorder"
        self.emulator = "HeadlessRecorder"
        self.connection_type = 3
        
        self.current_game_id: Optional[int] = None
        self.recording = False
        self.game_data_buffer = []
        
        self.on_status_update: Optional[Callable] = None
        self.on_game_data: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    async def connect(self, host: str, port: int = 27888) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            hello = self.protocol.create_hello_message()
            self.socket.sendto(hello, (host, port))
            
            data, _ = self.socket.recvfrom(1024)
            success, new_port = self.protocol.parse_hello_response(data)
            
            if not success:
                return False
            
            self.game_port = new_port
            self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.game_socket.settimeout(5.0)
            
            await self._perform_handshake(host)
            self.connected = True
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    async def _perform_handshake(self, host: str) -> None:
        login_msg = self.protocol.build_user_login(self.username, self.emulator, self.connection_type)
        packet = self.protocol.build_packet([login_msg])
        self.game_socket.sendto(packet, (host, self.game_port))
        
        for _ in range(4):
            await self._receive_and_ack(host)
    
    async def _receive_and_ack(self, host: str) -> None:
        data, _ = self.game_socket.recvfrom(4096)
        messages = self.protocol.parse_packet(data)
        
        for msg in messages:
            if msg.message_type == MessageType.SERVER_STATUS:
                status = self.protocol.parse_server_status(msg.data)
                if self.on_status_update:
                    self.on_status_update(status)
        
        ack_msg = self.protocol.build_client_ack()
        packet = self.protocol.build_packet([ack_msg])
        self.game_socket.sendto(packet, (host, self.game_port))
    
    async def update_status(self, host: str) -> Optional[ServerStatus]:
        if not self.connected:
            return None
        
        try:
            data, _ = self.game_socket.recvfrom(4096)
            messages = self.protocol.parse_packet(data)
            
            for msg in messages:
                if msg.message_type == MessageType.SERVER_STATUS:
                    status = self.protocol.parse_server_status(msg.data)
                    if self.on_status_update:
                        self.on_status_update(status)
                    return status
            
            ack_msg = self.protocol.build_client_ack()
            packet = self.protocol.build_packet([ack_msg])
            self.game_socket.sendto(packet, (host, self.game_port))
            
        except socket.timeout:
            pass
        
        return None
    
    async def join_game(self, host: str, game_id: int) -> bool:
        if not self.connected:
            return False
        
        try:
            join_msg = self.protocol.build_join_game(game_id, self.connection_type)
            packet = self.protocol.build_packet([join_msg])
            self.game_socket.sendto(packet, (host, self.game_port))
            
            self.current_game_id = game_id
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    async def start_game(self, host: str) -> bool:
        if not self.connected:
            return False
        
        try:
            start_msg = self.protocol.build_start_game()
            packet = self.protocol.build_packet([start_msg])
            self.game_socket.sendto(packet, (host, self.game_port))
            
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    async def ready_to_play(self, host: str) -> bool:
        if not self.connected:
            return False
        
        try:
            ready_msg = self.protocol.build_ready_to_play()
            packet = self.protocol.build_packet([ready_msg])
            self.game_socket.sendto(packet, (host, self.game_port))
            
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    async def send_game_data(self, host: str, data: bytes) -> bool:
        if not self.connected:
            return False
        
        try:
            game_data_msg = self.protocol.build_game_data(data)
            packet = self.protocol.build_packet([game_data_msg])
            self.game_socket.sendto(packet, (host, self.game_port))
            
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    async def receive_game_data(self, host: str) -> Optional[bytes]:
        if not self.connected:
            return None
        
        try:
            self.game_socket.settimeout(0.1)
            data, _ = self.game_socket.recvfrom(4096)
            messages = self.protocol.parse_packet(data)
            
            for msg in messages:
                if msg.message_type == MessageType.GAME_DATA:
                    game_data = self.protocol.parse_game_data(msg.data)
                    
                    if self.recording:
                        self.game_data_buffer.append({
                            'frame': len(self.game_data_buffer),
                            'timestamp': asyncio.get_event_loop().time(),
                            'data': game_data.frame_data.hex()
                        })
                    
                    if self.on_game_data:
                        self.on_game_data(game_data)
                    
                    return game_data.frame_data
            
            self.game_socket.settimeout(5.0)
            
        except socket.timeout:
            pass
        
        return None
    
    async def monitor_game(self, host: str, duration: int = 0) -> Dict[str, Any]:
        start_time = asyncio.get_event_loop().time()
        recording = []
        
        while True:
            data = await self.receive_game_data(host)
            if data:
                recording.append({
                    'timestamp': asyncio.get_event_loop().time(),
                    'data': data.hex()
                })
            
            if duration > 0 and asyncio.get_event_loop().time() - start_time >= duration:
                break
            
            await asyncio.sleep(0.001)
        
        return {
            'game_id': self.current_game_id,
            'duration': asyncio.get_event_loop().time() - start_time,
            'frames': len(recording),
            'data': recording
        }
    
    def start_recording(self) -> None:
        self.recording = True
        self.game_data_buffer = []
    
    def stop_recording(self) -> list:
        self.recording = False
        return self.game_data_buffer.copy()
    
    def disconnect(self) -> None:
        if self.game_socket:
            self.game_socket.close()
        if self.socket:
            self.socket.close()
        self.connected = False
        self.current_game_id = None
