import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class KailleraRecording:
    recording_id: str
    timestamp: str
    server_host: str
    server_port: int
    game_id: Optional[int]
    game_name: Optional[str]
    emulator: Optional[str]
    players: List[Dict[str, Any]]
    duration: float
    frames: int
    frame_data: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KailleraRecorder:
    def __init__(self, output_dir: str = "recordings"):
        self.output_dir = output_dir
        self.current_recording: Optional[KailleraRecording] = None
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_recording(self, server_host: str, server_port: int, 
                       game_id: Optional[int] = None,
                       game_name: Optional[str] = None,
                       emulator: Optional[str] = None,
                       players: Optional[List[Dict[str, Any]]] = None) -> str:
        recording_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_recording = KailleraRecording(
            recording_id=recording_id,
            timestamp=datetime.now().isoformat(),
            server_host=server_host,
            server_port=server_port,
            game_id=game_id,
            game_name=game_name,
            emulator=emulator,
            players=players or [],
            duration=0.0,
            frames=0,
            frame_data=[]
        )
        
        return recording_id
    
    def add_frame(self, frame_number: int, timestamp: float, data: bytes, 
                  player_number: Optional[int] = None) -> None:
        if not self.current_recording:
            return
        
        self.current_recording.frame_data.append({
            'frame': frame_number,
            'timestamp': timestamp,
            'player_number': player_number,
            'data': data.hex()
        })
        self.current_recording.frames = len(self.current_recording.frame_data)
    
    def stop_recording(self, duration: float) -> Optional[KailleraRecording]:
        if not self.current_recording:
            return None
        
        self.current_recording.duration = duration
        recording = self.current_recording
        self.current_recording = None
        
        return recording
    
    def save_recording(self, recording: KailleraRecording) -> str:
        filename = os.path.join(self.output_dir, f"{recording.recording_id}.json")
        
        with open(filename, 'w') as f:
            json.dump(recording.to_dict(), f, indent=2)
        
        return filename
    
    def save_kaillera_format(self, recording: KailleraRecording) -> str:
        filename = os.path.join(self.output_dir, f"{recording.recording_id}.kr")
        
        with open(filename, 'wb') as f:
            f.write(b'KAI')
            f.write(bytes([0x01]))
            
            game_name_bytes = (recording.game_name or "Unknown").encode('latin-1')[:32]
            f.write(game_name_bytes.ljust(32, b'\x00'))
            
            emulator_bytes = (recording.emulator or "Unknown").encode('latin-1')[:32]
            f.write(emulator_bytes.ljust(32, b'\x00'))
            
            timestamp_bytes = recording.timestamp.encode('utf-8')[:64]
            f.write(timestamp_bytes.ljust(64, b'\x00'))
            
            f.write(recording.game_id.to_bytes(4, 'little') if recording.game_id else b'\x00\x00\x00\x00')
            f.write(int(recording.duration).to_bytes(4, 'little'))
            f.write(recording.frames.to_bytes(4, 'little'))
            f.write(len(recording.players).to_bytes(4, 'little'))
            
            for player in recording.players:
                username_bytes = player.get('username', 'Unknown').encode('latin-1')[:32]
                f.write(username_bytes.ljust(32, b'\x00'))
                ping = player.get('ping', 0)
                f.write(ping.to_bytes(4, 'little'))
                conn_type = player.get('connection_type', 3)
                f.write(bytes([conn_type]))
            
            for frame in recording.frame_data:
                f.write(frame['frame'].to_bytes(4, 'little'))
                data = bytes.fromhex(frame['data'])
                f.write(len(data).to_bytes(2, 'little'))
                f.write(data)
        
        return filename
    
    def load_recording(self, filename: str) -> Optional[KailleraRecording]:
        if not os.path.exists(filename):
            return None
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return KailleraRecording(**data)
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        recordings = []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.json'):
                path = os.path.join(self.output_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                recordings.append(data)
        
        return sorted(recordings, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def delete_recording(self, recording_id: str) -> bool:
        json_file = os.path.join(self.output_dir, f"{recording_id}.json")
        kr_file = os.path.join(self.output_dir, f"{recording_id}.kr")
        
        deleted = False
        if os.path.exists(json_file):
            os.remove(json_file)
            deleted = True
        if os.path.exists(kr_file):
            os.remove(kr_file)
            deleted = True
        
        return deleted
