import struct
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import IntEnum


class MessageType(IntEnum):
    USER_QUIT = 0x01
    USER_JOINED = 0x02
    USER_LOGIN = 0x03
    SERVER_STATUS = 0x04
    SERVER_TO_CLIENT_ACK = 0x05
    CLIENT_TO_SERVER_ACK = 0x06
    GLOBAL_CHAT = 0x07
    GAME_CHAT = 0x08
    CLIENT_KEEP_ALIVE = 0x09
    CREATE_GAME = 0x0A
    QUIT_GAME = 0x0B
    JOIN_GAME = 0x0C
    PLAYER_INFO = 0x0D
    UPDATE_GAME_STATUS = 0x0E
    KICK_USER = 0x0F
    CLOSE_GAME = 0x10
    START_GAME = 0x11
    GAME_DATA = 0x12
    GAME_CACHE = 0x13
    DROP_GAME = 0x14
    READY_TO_PLAY = 0x15
    CONNECTION_REJECTED = 0x16
    SERVER_INFO = 0x17


@dataclass
class KailleraMessage:
    message_number: int
    message_type: MessageType
    data: bytes


@dataclass
class ServerStatus:
    users: int
    games: int
    user_list: List[dict]
    game_list: List[dict]


@dataclass
class GameData:
    player_number: int
    frame_data: bytes


class KailleraProtocol:
    def __init__(self):
        self.message_number = 0
        self.version = "0.83"
    
    def create_hello_message(self) -> bytes:
        return f"HELLO{self.version}".encode('latin-1')
    
    def parse_hello_response(self, data: bytes) -> Tuple[bool, Optional[int]]:
        data_str = data.decode('latin-1', errors='ignore')
        if data_str.startswith("TOO"):
            return False, None
        elif data_str.startswith("HELLOD00D"):
            try:
                port = int(data_str[9:])
                return True, port
            except ValueError:
                return False, None
        return False, None
    
    def build_packet(self, messages: List[KailleraMessage]) -> bytes:
        packet = bytearray()
        packet.append(len(messages))
        
        for msg in messages:
            header = struct.pack('<H', msg.message_number)
            header += struct.pack('<H', len(msg.data) + 1)
            header += bytes([msg.message_type])
            packet.extend(header)
            packet.extend(msg.data)
        
        return bytes(packet)
    
    def parse_packet(self, data: bytes) -> List[KailleraMessage]:
        if not data:
            return []
        
        messages = []
        offset = 0
        num_messages = data[0]
        offset += 1
        
        for _ in range(num_messages):
            if offset + 5 > len(data):
                break
            
            message_number = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            
            message_length = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            
            message_type = MessageType(data[offset])
            offset += 1
            
            message_data = bytes(data[offset:offset + message_length - 1])
            offset += message_length - 1
            
            messages.append(KailleraMessage(
                message_number=message_number,
                message_type=message_type,
                data=message_data
            ))
        
        return messages
    
    def build_user_login(self, username: str, emulator: str, connection_type: int = 3) -> KailleraMessage:
        data = username.encode('latin-1') + b'\x00'
        data += emulator.encode('latin-1') + b'\x00'
        data += bytes([connection_type])
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.USER_LOGIN,
            data=data
        )
    
    def build_client_ack(self) -> KailleraMessage:
        data = b'\x00'
        data += struct.pack('<I', 0)
        data += struct.pack('<I', 1)
        data += struct.pack('<I', 2)
        data += struct.pack('<I', 3)
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.CLIENT_TO_SERVER_ACK,
            data=data
        )
    
    def build_join_game(self, game_id: int, connection_type: int = 3) -> KailleraMessage:
        data = b'\x00'
        data += struct.pack('<I', game_id)
        data += b'\x00'
        data += struct.pack('<I', 0)
        data += struct.pack('<H', 0xFFFF)
        data += bytes([connection_type])
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.JOIN_GAME,
            data=data
        )
    
    def build_start_game(self) -> KailleraMessage:
        data = b'\x00'
        data += struct.pack('<H', 0xFFFF)
        data += b'\xFF'
        data += b'\xFF'
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.START_GAME,
            data=data
        )
    
    def build_ready_to_play(self) -> KailleraMessage:
        data = b'\x00'
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.READY_TO_PLAY,
            data=data
        )
    
    def build_game_data(self, game_data: bytes) -> KailleraMessage:
        data = b'\x00'
        data += struct.pack('<H', len(game_data))
        data += game_data
        
        self.message_number += 1
        return KailleraMessage(
            message_number=self.message_number,
            message_type=MessageType.GAME_DATA,
            data=data
        )
    
    def parse_server_status(self, data: bytes) -> ServerStatus:
        offset = 0
        
        if data[offset] != 0:
            offset += 1
        
        num_users = struct.unpack_from('<I', data, offset)[0]
        offset += 4
        
        num_games = struct.unpack_from('<I', data, offset)[0]
        offset += 4
        
        user_list = []
        for _ in range(num_users):
            username = self._read_null_string(data, offset)
            offset += len(username) + 1
            
            ping = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            
            connection_type = data[offset]
            offset += 1
            
            user_id = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            
            player_status = data[offset]
            offset += 1
            
            user_list.append({
                'username': username,
                'ping': ping,
                'connection_type': connection_type,
                'user_id': user_id,
                'status': player_status
            })
        
        game_list = []
        for _ in range(num_games):
            game_name = self._read_null_string(data, offset)
            offset += len(game_name) + 1
            
            game_id = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            
            emulator = self._read_null_string(data, offset)
            offset += len(emulator) + 1
            
            owner = self._read_null_string(data, offset)
            offset += len(owner) + 1
            
            players = self._read_null_string(data, offset)
            offset += len(players) + 1
            
            game_status = data[offset]
            offset += 1
            
            game_list.append({
                'name': game_name,
                'id': game_id,
                'emulator': emulator,
                'owner': owner,
                'players': players,
                'status': game_status
            })
        
        return ServerStatus(
            users=num_users,
            games=num_games,
            user_list=user_list,
            game_list=game_list
        )
    
    def _read_null_string(self, data: bytes, offset: int) -> str:
        end = data.find(b'\x00', offset)
        if end == -1:
            return data[offset:].decode('latin-1', errors='ignore')
        return data[offset:end].decode('latin-1', errors='ignore')
    
    def parse_game_data(self, data: bytes) -> GameData:
        offset = 0
        
        if data[offset] == 0:
            offset += 1
        
        length = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        
        frame_data = data[offset:offset + length]
        
        return GameData(
            player_number=0,
            frame_data=frame_data
        )
