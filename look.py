#!/usr/bin/env python3
"""
Wi-Fi Neural Packet Researcher - Advanced Edition
Enhanced ML-based Wi-Fi attack detection with real-time visualization
Optimized for Kali Linux with monitor mode support
"""

import os
import sys
import time
import threading
import signal
import subprocess
import numpy as np
import warnings
from collections import deque
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import json

# Scapy imports with fallback handling
try:
    from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11Deauth, RadioTap
    from scapy.layers.dot11 import Dot11QoS, Dot11Auth
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] Scapy not installed. Run: pip install scapy")

# ML imports
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Rich UI imports
try:
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[!] Rich not installed. Run: pip install rich")

warnings.filterwarnings("ignore")

# ==================== CONFIGURATION ====================

@dataclass
class Config:
    interface: str = "wlan1"
    monitor_interface: str = "wlan1mon"
    channels: List[int] = field(default_factory=lambda: [1, 6, 11, 2, 7, 3, 8, 4, 9, 5, 10])  # Full channel rotation
    channel_hop_interval: float = 1.5  # Seconds per channel
    buffer_size: int = 2000  # Packet buffer size
    training_interval: int = 3  # Retrain model every N seconds
    contamination: float = 0.08  # Expected anomaly rate (reduced for better detection)
    feature_count: int = 12  # Extended feature set
    anomaly_threshold_critical: float = 35.0  # Critical attack threshold %
    anomaly_threshold_high: float = 20.0  # High threat threshold %
    anomaly_threshold_suspicious: float = 10.0  # Suspicious threshold %
    deauth_threshold: int = 30  # Deauth packets per minute threshold
    beacon_flood_threshold: int = 500  # Beacon frames per minute threshold
    enable_channel_hopping: bool = True
    enable_visualization: bool = True
    enable_alerts: bool = True
    log_file: str = "/var/log/wifi_researcher.log"
    
config = Config()

# ==================== ENHANCED DATA STRUCTURES ====================

class PacketAnalyzer:
    """Enhanced packet analysis with extended features"""
    
    def __init__(self, buffer_size: int = 2000):
        self.packet_buffer = deque(maxlen=buffer_size)
        self.feature_matrix = np.zeros((0, config.feature_count))
        self.packet_types = defaultdict(int)
        self.deauth_counter = 0
        self.beacon_counter = 0
        self.probe_counter = 0
        self.auth_counter = 0
        self.rssi_history = deque(maxlen=100)
        self.bssid_set = set()
        self.station_set = set()
        self.anomaly_history = deque(maxlen=50)
        self.packet_rate_history = deque(maxlen=60)  # 60 seconds of packet rates
        self.last_stats_time = time.time()
        self.stats_lock = threading.Lock()
        
    def extract_enhanced_features(self, pkt) -> Optional[np.ndarray]:
        """Extract 12 enhanced features for better ML detection"""
        try:
            if not pkt.haslayer(Dot11):
                return None
                
            # Basic packet info
            pkt_type = pkt.type
            pkt_subtype = pkt.subtype
            
            # RSSI extraction (with fallbacks)
            rssi = self._extract_rssi(pkt)
            
            # Frame control flags
            fc_bytes = pkt.FCfield
            to_ds = 1 if (fc_bytes & 0x01) else 0
            from_ds = 1 if (fc_bytes & 0x02) else 0
            more_frag = 1 if (fc_bytes & 0x04) else 0
            retry = 1 if (fc_bytes & 0x08) else 0
            more_data = 1 if (fc_bytes & 0x10) else 0
            protected = 1 if (fc_bytes & 0x40) else 0
            order = 1 if (fc_bytes & 0x80) else 0
            
            # Duration
            duration = getattr(pkt, 'duration', 0)
            
            # Sequence number
            seq_num = getattr(pkt, 'SC', 0) >> 4 if hasattr(pkt, 'SC') else 0
            
            # Address extraction
            addr1 = pkt.addr1 if hasattr(pkt, 'addr1') else None
            addr2 = pkt.addr2 if hasattr(pkt, 'addr2') else None
            addr3 = pkt.addr3 if hasattr(pkt, 'addr3') else None
            
            # Update BSSID and station sets
            if addr2 and addr2 not in self.bssid_set:
                self.bssid_set.add(addr2)
            if addr1 and addr1 not in self.station_set:
                self.station_set.add(addr1)
            
            # Unique addresses count
            unique_bssids = len(self.bssid_set)
            unique_stations = len(self.station_set)
            
            # Time-based features
            current_time = time.time()
            time_components = [
                current_time % 86400 / 86400,  # Time of day normalized
                (current_time % 3600) / 3600,   # Minute of hour
                (current_time % 60) / 60        # Second of minute
            ]
            
            # Normalized features
            norm_rssi = max(0, min(1, (rssi + 100) / 60)) if rssi != -100 else 0.5
            
            # Extended feature vector (12 features)
            features = [
                norm_rssi,                         # 0: Signal strength
                pkt_type / 2.0,                    # 1: Packet type (0-2)
                pkt_subtype / 15.0,                # 2: Subtype (0-15)
                retry,                             # 3: Retry flag
                protected,                         # 4: Protected flag
                to_ds,                            # 5: To DS
                from_ds,                          # 6: From DS
                more_frag,                        # 7: More fragments
                duration / 32768.0,               # 8: Duration normalized
                seq_num / 4095.0,                 # 9: Sequence number normalized
                unique_bssids / 100.0,            # 10: Unique BSSIDs (capped)
                unique_stations / 200.0           # 11: Unique stations (capped)
            ]
            
            # Track packet types for attack detection
            self._track_packet_type(pkt_type, pkt_subtype)
            
            # Update packet rate
            self._update_packet_rate()
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None
    
    def _extract_rssi(self, pkt) -> int:
        """Extract RSSI from various possible locations"""
        # Try different RSSI locations
        if hasattr(pkt, 'dBm_AntSignal'):
            rssi = pkt.dBm_AntSignal
        elif hasattr(pkt, 'Signal'):
            rssi = pkt.Signal
        elif pkt.haslayer(RadioTap):
            rssi = pkt[RadioTap].dBm_AntSignal if hasattr(pkt[RadioTap], 'dBm_AntSignal') else -100
        else:
            rssi = -100
        
        # Sanitize RSSI
        if rssi == 0 or rssi > -20:
            rssi = -100
        return max(-100, min(-20, rssi))  # Clamp between -100 and -20
    
    def _track_packet_type(self, pkt_type: int, pkt_subtype: int):
        """Track specific packet types for attack detection"""
        with self.stats_lock:
            if pkt_type == 0:  # Management frames
                if pkt_subtype == 12:  # Deauth
                    self.deauth_counter += 1
                elif pkt_subtype == 8:  # Beacon
                    self.beacon_counter += 1
                elif pkt_subtype == 4:  # Probe Request
                    self.probe_counter += 1
                elif pkt_subtype == 11:  # Authentication
                    self.auth_counter += 1
    
    def _update_packet_rate(self):
        """Track packet rate over time"""
        current_time = time.time()
        self.packet_rate_history.append((current_time, 1))
        
        # Clean old entries
        while self.packet_rate_history and current_time - self.packet_rate_history[0][0] > 60:
            self.packet_rate_history.popleft()
    
    def get_packet_rate(self) -> float:
        """Calculate packets per second over last 60 seconds"""
        if not self.packet_rate_history:
            return 0
        current_time = time.time()
        recent = [(t, c) for t, c in self.packet_rate_history if current_time - t <= 60]
        total_packets = sum(c for _, c in recent)
        return total_packets / 60.0 if recent else 0
    
    def get_attack_indicators(self) -> Dict:
        """Get attack detection indicators"""
        with self.stats_lock:
            deauth_rate = self.deauth_counter / 60.0  # Per minute
            beacon_rate = self.beacon_counter / 60.0
            probe_rate = self.probe_counter / 60.0
            
            indicators = {
                'deauth_attack': deauth_rate > config.deauth_threshold,
                'beacon_flood': beacon_rate > config.beacon_flood_threshold,
                'deauth_rate': deauth_rate,
                'beacon_rate': beacon_rate,
                'probe_rate': probe_rate,
                'total_deauth': self.deauth_counter,
                'total_beacons': self.beacon_counter,
                'total_probes': self.probe_counter,
                'total_auth': self.auth_counter,
                'unique_bssids': len(self.bssid_set),
                'unique_stations': len(self.station_set)
            }
            
            # Reset counters periodically
            if time.time() - getattr(self, '_last_reset', time.time()) > 60:
                self.deauth_counter = 0
                self.beacon_counter = 0
                self.probe_counter = 0
                self.auth_counter = 0
                self._last_reset = time.time()
            
            return indicators
    
    def add_features(self, features: np.ndarray):
        """Add features to matrix with size management"""
        if features is not None and features.size > 0:
            self.feature_matrix = np.vstack([self.feature_matrix, features]) if self.feature_matrix.size else features
            # Keep only recent features
            if len(self.feature_matrix) > config.buffer_size:
                self.feature_matrix = self.feature_matrix[-config.buffer_size:]

# ==================== ENHANCED ML MODEL ====================

class AdaptiveMLModel:
    """Self-adapting ML model with online learning"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.last_training_time = 0
        self.training_lock = threading.Lock()
        self.is_training = False
        self.performance_history = deque(maxlen=100)
        self.best_model = None
        self.best_score = 0
        
    def train(self, feature_matrix: np.ndarray):
        """Train or update the ML model"""
        if len(feature_matrix) < 50 or self.is_training:
            return False
            
        with self.training_lock:
            self.is_training = True
            try:
                # Normalize features
                normalized = self._normalize_features(feature_matrix)
                
                # Train new model
                new_model = IsolationForest(
                    contamination=config.contamination,
                    random_state=42,
                    n_estimators=150,
                    max_samples='auto',
                    bootstrap=True,
                    n_jobs=-1
                )
                new_model.fit(normalized)
                
                # Evaluate model performance
                score = self._evaluate_model(new_model, normalized)
                self.performance_history.append(score)
                
                # Update best model if better
                if score > self.best_score:
                    self.best_score = score
                    self.best_model = new_model
                
                self.model = new_model
                self.last_training_time = time.time()
                return True
                
            except Exception as e:
                print(f"Training error: {e}")
                return False
            finally:
                self.is_training = False
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features for better ML performance"""
        try:
            if not hasattr(self.scaler, 'mean_'):
                self.scaler.fit(features)
            return self.scaler.transform(features)
        except:
            return features
    
    def _evaluate_model(self, model, features: np.ndarray) -> float:
        """Evaluate model performance (silhouette score approximation)"""
        try:
            predictions = model.predict(features)
            anomaly_ratio = np.count_nonzero(predictions == -1) / len(predictions)
            # Ideal is contamination rate, score based on closeness
            return 1.0 - abs(anomaly_ratio - config.contamination) / config.contamination
        except:
            return 0.5
    
    def predict(self, features: np.ndarray) -> Tuple[np.ndarray, float]:
        """Predict anomalies with confidence score"""
        if self.model is None or len(features) == 0:
            return np.array([]), 0.0
            
        try:
            normalized = self._normalize_features(features)
            predictions = self.model.predict(normalized)
            
            # Calculate anomaly percentage
            anomaly_count = np.count_nonzero(predictions == -1)
            anomaly_percent = (anomaly_count / len(predictions)) * 100 if len(predictions) > 0 else 0
            
            return predictions, anomaly_percent
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return np.array([]), 0.0
    
    def needs_retraining(self) -> bool:
        """Check if model needs retraining"""
        return (time.time() - self.last_training_time > config.training_interval and 
                not self.is_training)

# ==================== ATTACK DETECTOR ====================

class AttackDetector:
    """Multi-layer attack detection system"""
    
    @staticmethod
    def detect_attack(threat_level: float, ml_anomaly: float, indicators: Dict) -> Tuple[str, str, List[str]]:
        """Detect specific attack types based on multiple indicators"""
        
        status = "🟢 NORMAL"
        severity = "LOW"
        attacks = []
        
        # Check for deauth attack
        if indicators.get('deauth_attack', False):
            attacks.append("DEAUTHENTICATION FLOOD")
            severity = "CRITICAL"
            status = "🔴 CRITICAL ATTACK"
        
        # Check for beacon flood
        if indicators.get('beacon_flood', False):
            attacks.append("BEACON FLOOD")
            severity = "HIGH"
            if status == "🟢 NORMAL":
                status = "🟠 HIGH THREAT"
        
        # ML anomaly detection
        if ml_anomaly > config.anomaly_threshold_critical:
            attacks.append(f"ML-DETECTED ATTACK ({ml_anomaly:.1f}% anomaly)")
            status = "🔴 CRITICAL ATTACK"
            severity = "CRITICAL"
        elif ml_anomaly > config.anomaly_threshold_high:
            attacks.append(f"UNUSUAL PATTERN ({ml_anomaly:.1f}% anomaly)")
            if status == "🟢 NORMAL":
                status = "🟠 HIGH THREAT"
                severity = "HIGH"
        elif ml_anomaly > config.anomaly_threshold_suspicious:
            attacks.append(f"SUSPICIOUS ACTIVITY ({ml_anomaly:.1f}% anomaly)")
            if status == "🟢 NORMAL":
                status = "🟡 SUSPICIOUS"
                severity = "MEDIUM"
        
        # Check for probe flooding (reconnaissance)
        if indicators.get('probe_rate', 0) > 100:
            attacks.append("PROBE REQUEST FLOOD (RECONNAISSANCE)")
            if severity == "LOW":
                severity = "MEDIUM"
                status = "🟡 SUSPICIOUS"
        
        # High packet rate anomaly
        packet_rate = indicators.get('packet_rate', 0)
        if packet_rate > 1000:
            attacks.append(f"HIGH PACKET RATE ({packet_rate:.0f} pps)")
        
        return status, severity, attacks
    
    @staticmethod
    def get_mitigation_suggestions(attacks: List[str]) -> List[str]:
        """Provide mitigation suggestions based on detected attacks"""
        suggestions = []
        
        if any("DEAUTH" in a for a in attacks):
            suggestions.extend([
                "→ Enable 802.11w (Management Frame Protection)",
                "→ Use WPA3 instead of WPA2",
                "→ Implement rogue AP detection"
            ])
        
        if any("BEACON" in a for a in attacks):
            suggestions.extend([
                "→ Configure beacon interval monitoring",
                "→ Implement AP whitelisting",
                "→ Use wireless intrusion detection system (WIDS)"
            ])
        
        if any("PROBE" in a for a in attacks):
            suggestions.extend([
                "→ Disable SSID broadcast on sensitive networks",
                "→ Implement probe request rate limiting"
            ])
        
        if not suggestions:
            suggestions = ["→ Continue monitoring, no immediate action required"]
        
        return suggestions

# ==================== ENHANCED UI ====================

class EnhancedUI:
    """Advanced terminal UI with rich formatting"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.setup_layout()
        self.last_update = 0
        
    def setup_layout(self):
        """Setup the UI layout"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        self.layout["body"].split_row(
            Layout(name="left_panel", ratio=1),
            Layout(name="right_panel", ratio=1)
        )
        self.layout["left_panel"].split_column(
            Layout(name="stats", size=8),
            Layout(name="attacks", size=10),
            Layout(name="mitigation", size=8)
        )
        self.layout["right_panel"].split_column(
            Layout(name="neural_view", size=12),
            Layout(name="packet_analysis", size=14)
        )
    
    def update(self, stats: Dict, ml_status: Dict, attacks: List[str], 
               mitigation: List[str], indicators: Dict):
        """Update the UI with latest data"""
        
        # Header
        status = ml_status.get('status', 'UNKNOWN')
        anomaly = ml_status.get('anomaly_percent', 0)
        packet_rate = stats.get('packet_rate', 0)
        
        header_text = Text()
        header_text.append("🧠 Wi-Fi Neural Packet Researcher | ", style="bold green")
        header_text.append(f"{status} | ", style=ml_status.get('color', 'white'))
        header_text.append(f"PPS: {packet_rate:.1f} | ", style="cyan")
        header_text.append(f"Anomaly: {anomaly:.1f}% | ", style="yellow")
        header_text.append(f"Packets: {stats['total_packets']}", style="blue")
        
        self.layout["header"].update(Panel(Align.center(header_text), style="bold"))
        
        # Statistics Panel
        stats_table = Table(title="📊 System Statistics", box=None, style="cyan")
        stats_table.add_column("Metric", style="bold cyan")
        stats_table.add_column("Value", style="yellow")
        stats_table.add_row("Total Packets", str(stats['total_packets']))
        stats_table.add_row("Buffer Size", f"{stats['buffer_size']}/{config.buffer_size}")
        stats_table.add_row("Feature Matrix", f"{stats['feature_count']} samples")
        stats_table.add_row("ML Model", "Isolation Forest (Enhanced)")
        stats_table.add_row("Unique BSSIDs", str(indicators.get('unique_bssids', 0)))
        stats_table.add_row("Unique Stations", str(indicators.get('unique_stations', 0)))
        stats_table.add_row("Channel", str(stats.get('current_channel', 'N/A')))
        stats_table.add_row("Uptime", stats.get('uptime', 'N/A'))
        
        self.layout["stats"].update(Panel(stats_table, title="System Status", border_style="blue"))
        
        # Attack Panel
        if attacks:
            attack_table = Table(title="🚨 Detected Threats", box=None, style="red")
            attack_table.add_column("Attack Type", style="bold red")
            attack_table.add_column("Severity", style="bold yellow")
            for attack in attacks:
                if "CRITICAL" in attack or "DEAUTH" in attack:
                    severity = "🔴 CRITICAL"
                elif "HIGH" in attack or "FLOOD" in attack:
                    severity = "🟠 HIGH"
                elif "SUSPICIOUS" in attack:
                    severity = "🟡 MEDIUM"
                else:
                    severity = "🔵 LOW"
                attack_table.add_row(attack, severity)
        else:
            attack_table = Table(title="✅ Security Status", box=None)
            attack_table.add_row("No threats detected", style="green")
        
        self.layout["attacks"].update(Panel(attack_table, title="Threat Analysis", border_style="red"))
        
        # Mitigation Panel
        mit_table = Table(title="🛡️ Recommendations", box=None)
        mit_table.add_column("Action", style="cyan")
        for suggestion in mitigation[:5]:
            mit_table.add_row(suggestion)
        
        self.layout["mitigation"].update(Panel(mit_table, title="Mitigation", border_style="green"))
        
        # Neural Network View
        neural_table = Table(title="🧬 Neural Net Analysis", box=None)
        neural_table.add_column("Time", style="dim")
        neural_table.add_column("Event", style="cyan")
        
        # Recent events
        events = [
            (datetime.now().strftime("%H:%M:%S"), f"Model trained: {ml_status.get('trained', False)}"),
            (datetime.now().strftime("%H:%M:%S"), f"Anomaly score: {anomaly:.2f}%"),
        ]
        
        if ml_status.get('last_update', 0) > 0:
            events.append((datetime.now().strftime("%H:%M:%S"), 
                          f"Last update: {ml_status['last_update']:.1f}s ago"))
        
        for t, e in events:
            neural_table.add_row(t, e)
        
        self.layout["neural_view"].update(Panel(neural_table, title="ML Analysis", border_style="magenta"))
        
        # Packet Analysis
        packet_table = Table(title="📡 Traffic Analysis", box=None)
        packet_table.add_column("Type", style="cyan")
        packet_table.add_column("Rate (per min)", style="yellow")
        packet_table.add_column("Total", style="white")
        
        packet_types = [
            ("Deauth Frames", indicators.get('deauth_rate', 0), indicators.get('total_deauth', 0)),
            ("Beacon Frames", indicators.get('beacon_rate', 0), indicators.get('total_beacons', 0)),
            ("Probe Requests", indicators.get('probe_rate', 0), indicators.get('total_probes', 0)),
            ("Auth Frames", 0, indicators.get('total_auth', 0)),
        ]
        
        for ptype, rate, total in packet_types:
            color = "red" if rate > config.deauth_threshold else "yellow"
            packet_table.add_row(ptype, f"[{color}]{rate:.1f}[/{color}]", str(total))
        
        self.layout["packet_analysis"].update(Panel(packet_table, title="Packet Statistics", border_style="cyan"))
    
    def get_layout(self) -> Layout:
        return self.layout

# ==================== MAIN RESEARCHER CLASS ====================

class WiFiResearcher:
    """Main Wi-Fi researcher class with all functionality"""
    
    def __init__(self, interface: str = "wlan1"):
        self.interface = interface
        self.monitor_interface = f"{interface}mon"
        self.analyzer = PacketAnalyzer()
        self.ml_model = AdaptiveMLModel()
        self.detector = AttackDetector()
        self.ui = EnhancedUI() if config.enable_visualization else None
        self.running = True
        self.start_time = time.time()
        self.current_channel = 1
        self.stats_lock = threading.Lock()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\n[+] Shutting down researcher...")
        self.running = False
        
    def setup_monitor_mode(self) -> bool:
        """Setup monitor mode on the interface"""
        print("[+] Setting up monitor mode...")
        
        try:
            # Kill interfering processes
            subprocess.run(["airmon-ng", "check", "kill"], capture_output=True)
            
            # Start monitor mode
            result = subprocess.run(
                ["airmon-ng", "start", self.interface],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"[!] Failed to start monitor mode: {result.stderr}")
                return False
                
            # Verify interface exists
            if not os.path.exists(f"/sys/class/net/{self.monitor_interface}"):
                print(f"[!] Monitor interface {self.monitor_interface} not found")
                return False
                
            print(f"[+] Monitor mode active on {self.monitor_interface}")
            return True
            
        except Exception as e:
            print(f"[!] Error setting up monitor mode: {e}")
            return False
    
    def channel_hopper(self):
        """Continuous channel hopping for full spectrum monitoring"""
        channel_index = 0
        while self.running and config.enable_channel_hopping:
            try:
                channel = config.channels[channel_index % len(config.channels)]
                self.current_channel = channel
                
                # Set channel using iwconfig
                subprocess.run(
                    ["iwconfig", self.monitor_interface, "channel", str(channel)],
                    capture_output=True,
                    timeout=2
                )
                
                channel_index += 1
                time.sleep(config.channel_hop_interval)
                
            except Exception as e:
                print(f"[!] Channel hopping error: {e}")
                time.sleep(1)
    
    def packet_handler(self, pkt):
        """Process captured packets"""
        if not self.running:
            return
            
        try:
            # Extract features
            features = self.analyzer.extract_enhanced_features(pkt)
            
            if features is not None:
                self.analyzer.add_features(features)
                
                # Trigger ML training if needed
                if self.ml_model.needs_retraining() and len(self.analyzer.feature_matrix) >= 100:
                    threading.Thread(
                        target=self.ml_model.train,
                        args=(self.analyzer.feature_matrix,),
                        daemon=True
                    ).start()
                    
        except Exception as e:
            print(f"Packet handler error: {e}")
    
    def run_ml_analysis(self) -> Dict:
        """Run ML inference on collected data"""
        if len(self.analyzer.feature_matrix) < 50:
            return {
                'status': "🧠 Training...",
                'anomaly_percent': 0,
                'color': 'yellow',
                'trained': False,
                'last_update': 0
            }
        
        # Get predictions
        predictions, anomaly_percent = self.ml_model.predict(self.analyzer.feature_matrix)
        
        # Get attack indicators
        indicators = self.analyzer.get_attack_indicators()
        indicators['packet_rate'] = self.analyzer.get_packet_rate()
        
        # Detect attacks
        status, severity, attacks = self.detector.detect_attack(
            anomaly_percent, 
            anomaly_percent, 
            indicators
        )
        
        # Get mitigation suggestions
        mitigation = self.detector.get_mitigation_suggestions(attacks)
        
        # Update anomaly history
        self.analyzer.anomaly_history.append(anomaly_percent)
        
        return {
            'status': status,
            'anomaly_percent': anomaly_percent,
            'color': 'red' if severity == 'CRITICAL' else 'orange' if severity == 'HIGH' else 'yellow',
            'trained': self.ml_model.last_training_time > 0,
            'last_update': time.time() - self.ml_model.last_training_time if self.ml_model.last_training_time > 0 else 0,
            'attacks': attacks,
            'mitigation': mitigation,
            'indicators': indicators,
            'severity': severity
        }
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            'total_packets': len(self.analyzer.feature_matrix),
            'buffer_size': len(self.analyzer.packet_buffer),
            'feature_count': len(self.analyzer.feature_matrix),
            'packet_rate': self.analyzer.get_packet_rate(),
            'uptime': self._format_uptime(),
            'current_channel': self.current_channel
        }
    
    def _format_uptime(self) -> str:
        """Format uptime string"""
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def run(self):
        """Main execution loop"""
        print_header()
        
        # Check requirements
        if not SCAPY_AVAILABLE:
            print("[!] Scapy not installed. Run: pip install scapy")
            return
            
        # Setup monitor mode
        if not self.setup_monitor_mode():
            print("[!] Failed to setup monitor mode. Make sure you have a compatible wireless adapter.")
            return
        
        # Start channel hopping thread
        if config.enable_channel_hopping:
            hopper_thread = threading.Thread(target=self.channel_hopper, daemon=True)
            hopper_thread.start()
            print(f"[+] Channel hopping enabled (interval: {config.channel_hop_interval}s)")
        
        # Start packet capture
        print(f"[+] Starting packet capture on {self.monitor_interface}")
        print("[+] Press Ctrl+C to stop\n")
        
        # Start capture in separate thread
        capture_thread = threading.Thread(
            target=lambda: sniff(
                iface=self.monitor_interface,
                prn=self.packet_handler,
                store=0,
                monitor=True,
                timeout=0
            ),
            daemon=True
        )
        capture_thread.start()
        
        # Main UI loop
        if self.ui and config.enable_visualization:
            with Live(self.ui.get_layout(), refresh_per_second=2, screen=True):
                while self.running:
                    try:
                        # Run ML analysis
                        ml_results = self.run_ml_analysis()
                        stats = self.get_stats()
                        
                        # Update UI
                        self.ui.update(
                            stats=stats,
                            ml_status=ml_results,
                            attacks=ml_results.get('attacks', []),
                            mitigation=ml_results.get('mitigation', []),
                            indicators=ml_results.get('indicators', {})
                        )
                        
                        # Log critical events
                        if ml_results.get('severity') == 'CRITICAL' and config.enable_alerts:
                            self._log_critical_event(ml_results)
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"UI update error: {e}")
                        time.sleep(1)
        else:
            # Console mode (no rich UI)
            while self.running:
                ml_results = self.run_ml_analysis()
                stats = self.get_stats()
                
                os.system('clear')
                print("=" * 70)
                print(f"🧠 Wi-Fi Neural Packet Researcher")
                print("=" * 70)
                print(f"Status: {ml_results['status']}")
                print(f"Anomaly: {ml_results['anomaly_percent']:.1f}%")
                print(f"Packets: {stats['total_packets']}")
                print(f"Packet Rate: {stats['packet_rate']:.1f} pps")
                print(f"Channel: {stats['current_channel']}")
                print(f"Uptime: {stats['uptime']}")
                
                if ml_results.get('attacks'):
                    print(f"\n🚨 Detected: {', '.join(ml_results['attacks'])}")
                
                time.sleep(1)
    
    def _log_critical_event(self, ml_results: Dict):
        """Log critical security events"""
        try:
            with open(config.log_file, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] CRITICAL: {ml_results['status']} - ")
                f.write(f"Anomaly: {ml_results['anomaly_percent']:.1f}% - ")
                f.write(f"Attacks: {', '.join(ml_results.get('attacks', []))}\n")
        except:
            pass

# ==================== UTILITY FUNCTIONS ====================

def print_header():
    """Print application header"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║     🧠 Wi-Fi Neural Packet Researcher - Advanced Edition     ║
    ║          ML-Powered Attack Detection & Analysis             ║
    ║                    Kali Linux Optimized                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def check_dependencies():
    """Check and install missing dependencies"""
    missing = []
    
    if not SCAPY_AVAILABLE:
        missing.append("scapy")
    if not RICH_AVAILABLE:
        missing.append("rich")
    
    if missing:
        print(f"[!] Missing dependencies: {', '.join(missing)}")
        response = input("[?] Install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
            print("[+] Dependencies installed. Please restart the script.")
            sys.exit(0)
        else:
            print("[!] Continuing with limited functionality...")

def main():
    """Main entry point"""
    # Check for root privileges
    if os.geteuid() != 0:
        print("[!] This script must be run as root (sudo)")
        print("[!] Reason: Requires monitor mode and raw packet access")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Wi-Fi Neural Packet Researcher")
    parser.add_argument("-i", "--interface", default="wlan1", help="Wireless interface (default: wlan1)")
    parser.add_argument("-c", "--channels", type=str, help="Comma-separated channels (e.g., 1,6,11)")
    parser.add_argument("--no-hopping", action="store_true", help="Disable channel hopping")
    parser.add_argument("--no-visual", action="store_true", help="Disable rich visualization")
    parser.add_argument("--threshold", type=float, default=0.08, help="Anomaly threshold (default: 0.08)")
    
    args = parser.parse_args()
    
    # Update configuration
    config.interface = args.interface
    config.enable_channel_hopping = not args.no_hopping
    config.enable_visualization = not args.no_visual
    config.contamination = args.threshold
    
    if args.channels:
        config.channels = [int(ch.strip()) for ch in args.channels.split(',')]
    
    # Check dependencies
    check_dependencies()
    
    # Create and run researcher
    researcher = WiFiResearcher(interface=config.interface)
    
    try:
        researcher.run()
    except KeyboardInterrupt:
        print("\n[+] Shutting down...")
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup: stop monitor mode
        try:
            subprocess.run(["airmon-ng", "stop", researcher.monitor_interface], capture_output=True)
            subprocess.run(["service", "NetworkManager", "restart"], capture_output=True)
        except:
            pass
        print("[+] Cleanup complete")

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    main()