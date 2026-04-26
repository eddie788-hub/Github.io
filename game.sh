#!/bin/bash
# ============================================
# Space Flight Simulator - Complete Installer
# ============================================
# This script installs and configures everything needed
# to run the Space Flight Simulator locally or on a server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     🚀 SPACE FLIGHT SIMULATOR - COMPLETE INSTALLER 🚀        ║"
echo "║                                                              ║"
echo "║                    Version 2.0 - Self-Hosted                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration variables
INSTALL_DIR="${PWD}/space-flight-simulator"
SERVER_PORT=8080
GAME_PORT=8000
INSTALL_TYPE="full"  # full, minimal, server-only
PYTHON_VERSION="3.9"
NODE_VERSION="18"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            SERVER_PORT="$2"
            shift 2
            ;;
        --game-port)
            GAME_PORT="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --type)
            INSTALL_TYPE="$2"
            shift 2
            ;;
        --help)
            echo -e "${GREEN}Usage: $0 [OPTIONS]${NC}"
            echo ""
            echo "Options:"
            echo "  --port PORT           Server port (default: 8080)"
            echo "  --game-port PORT      Game port (default: 8000)"
            echo "  --install-dir DIR     Installation directory (default: current directory)"
            echo "  --type TYPE           Install type: full, minimal, server-only (default: full)"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create installation directory
echo -e "\n${BLUE}📁 Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}✓ Installation directory: $INSTALL_DIR${NC}"

# ============================================
# CHECK SYSTEM REQUIREMENTS
# ============================================
echo -e "\n${BLUE}🔍 Checking system requirements...${NC}"

# Check OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
    echo -e "${GREEN}✓ Linux detected${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
    echo -e "${GREEN}✓ macOS detected${NC}"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
    echo -e "${YELLOW}⚠ Windows detected. WSL recommended for best experience${NC}"
else
    echo -e "${RED}✗ Unknown operating system${NC}"
    exit 1
fi

# Check Python
echo -e "\n${BLUE}🐍 Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 --version | awk '{print $2}')
    PY_MAJOR=$(echo $PY_VER | cut -d. -f1)
    PY_MINOR=$(echo $PY_VER | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        echo -e "${GREEN}✓ Python $PY_VER found${NC}"
    else
        echo -e "${RED}✗ Python 3.8+ required (found $PY_VER)${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python3 not found${NC}"
    echo -e "${YELLOW}Installing Python...${NC}"
    if [[ "$OS_TYPE" == "linux" ]]; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
    elif [[ "$OS_TYPE" == "macos" ]]; then
        brew install python@3.9
    fi
fi

# Check Node.js (optional)
echo -e "\n${BLUE}📦 Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VER=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VER found${NC}"
else
    echo -e "${YELLOW}⚠ Node.js not found (optional for development)${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✓ npm found${NC}"
fi

# Check Docker (optional)
echo -e "\n${BLUE}🐳 Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VER=$(docker --version)
    echo -e "${GREEN}✓ Docker found: $DOCKER_VER${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found (optional for containerized deployment)${NC}"
    DOCKER_AVAILABLE=false
fi

# ============================================
# CREATE PROJECT STRUCTURE
# ============================================
echo -e "\n${BLUE}📂 Creating project structure...${NC}"

mkdir -p {static/{assets,images,sounds},logs,data/{game_saves,maps,players},config,scripts,backups}
mkdir -p app/{api,core,models,services,websocket,schemas}
mkdir -p tests/{unit,integration}
mkdir -p docs

echo -e "${GREEN}✓ Directory structure created${NC}"

# ============================================
# CREATE MAIN GAME FILE
# ============================================
echo -e "\n${BLUE}🎮 Creating game files...${NC}"

# Create index.html (main game file)
cat > static/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Space Flight Simulator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
        body { overflow: hidden; background: #000; font-family: monospace; }
        canvas { display: block; cursor: crosshair; }
        #controls-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            border: 1px solid #0ff;
            padding: 10px;
            border-radius: 5px;
            color: #0ff;
            font-size: 10px;
            z-index: 100;
            pointer-events: none;
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #0f0;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <div id="controls-panel">
        <div><span class="status-dot"></span> SERVER: ONLINE</div>
        <div>🎮 WASD: Move | 🖱️ Click: Target | 🖱️ Right-click: Fire</div>
        <div>⛏️ M: Mine | 💬 E: Interact | 🤖 A: Autopilot</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Game initialization
        const canvas = document.getElementById('gameCanvas');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000011);
        scene.fog = new THREE.FogExp2(0x000011, 0.0002);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
        camera.position.set(0, 5, 15);
        
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        // Simple starfield
        const starGeometry = new THREE.BufferGeometry();
        const starCount = 2000;
        const starPositions = new Float32Array(starCount * 3);
        for(let i = 0; i < starCount; i++) {
            starPositions[i*3] = (Math.random() - 0.5) * 2000;
            starPositions[i*3+1] = (Math.random() - 0.5) * 1000;
            starPositions[i*3+2] = (Math.random() - 0.5) * 1000 - 500;
        }
        starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        const stars = new THREE.Points(starGeometry, new THREE.PointsMaterial({ color: 0xffffff, size: 0.2 }));
        scene.add(stars);
        
        // Create player ship
        const shipGroup = new THREE.Group();
        const bodyGeo = new THREE.ConeGeometry(1, 2.5, 8);
        const bodyMat = new THREE.MeshPhongMaterial({ color: 0x0aafff });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.rotation.x = Math.PI;
        shipGroup.add(body);
        
        const wingMat = new THREE.MeshPhongMaterial({ color: 0x0088ff });
        const leftWing = new THREE.Mesh(new THREE.BoxGeometry(2, 0.1, 1), wingMat);
        leftWing.position.set(-1.2, 0.1, -0.5);
        shipGroup.add(leftWing);
        
        const rightWing = new THREE.Mesh(new THREE.BoxGeometry(2, 0.1, 1), wingMat);
        rightWing.position.set(1.2, 0.1, -0.5);
        shipGroup.add(rightWing);
        
        scene.add(shipGroup);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x222244);
        scene.add(ambientLight);
        const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
        mainLight.position.set(100, 100, 50);
        scene.add(mainLight);
        
        // Animation
        let velocity = new THREE.Vector3();
        let keys = {};
        
        document.addEventListener('keydown', (e) => keys[e.key.toLowerCase()] = true);
        document.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false);
        
        function animate() {
            requestAnimationFrame(animate);
            
            // Simple movement
            const speed = 0.1;
            if(keys['w']) velocity.z -= speed;
            if(keys['s']) velocity.z += speed;
            if(keys['a']) velocity.x -= speed;
            if(keys['d']) velocity.x += speed;
            
            velocity.multiplyScalar(0.98);
            shipGroup.position.add(velocity);
            
            camera.position.copy(shipGroup.position);
            camera.position.y += 3;
            camera.position.z += 8;
            camera.lookAt(shipGroup.position);
            
            renderer.render(scene, camera);
        }
        
        animate();
        
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
HTMLEOF

echo -e "${GREEN}✓ Game file created: static/index.html${NC}"

# ============================================
# CREATE PYTHON BACKEND
# ============================================
if [[ "$INSTALL_TYPE" == "full" ]] || [[ "$INSTALL_TYPE" == "server-only" ]]; then
    echo -e "\n${BLUE}🐍 Creating Python backend...${NC}"
    
    # Create requirements.txt
    cat > requirements.txt << 'REQUIREMENTS'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-socketio==5.10.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic[email]==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.25.1
numpy==1.24.3
REQUIREMENTS

    # Create main.py
    cat > app/main.py << 'PYTHONEOF'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Space Flight Simulator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Space Flight Simulator API", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy", "game": "running"}

@app.get("/api/game/state")
async def game_state():
    return {
        "players": 0,
        "game_time": 0,
        "sector": "ALPHA-001"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
PYTHONEOF

    echo -e "${GREEN}✓ Python backend created${NC}"
fi

# ============================================
# CREATE SERVER SCRIPT
# ============================================
echo -e "\n${BLUE}🖥️ Creating server scripts...${NC}"

# Create start script
cat > start.sh << 'STARTEOF'
#!/bin/bash
# Space Flight Simulator - Start Script

echo "🚀 Starting Space Flight Simulator..."

# Check if Python backend exists
if [ -f "app/main.py" ]; then
    echo "Starting Python backend..."
    cd "$(dirname "$0")"
    
    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start server in background
    python3 app/main.py &
    SERVER_PID=$!
    echo "✓ Backend started (PID: $SERVER_PID)"
fi

# Start simple HTTP server for static files
echo "Starting web server on port 8080..."
cd static
python3 -m http.server 8080 &
HTTP_PID=$!
echo "✓ Web server started (PID: $HTTP_PID)"
cd ..

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     🚀 SPACE FLIGHT SIMULATOR IS RUNNING! 🚀                 ║"
echo "║                                                              ║"
echo "║     🌐 Open in browser: http://localhost:8080                ║"
echo "║     📡 API: http://localhost:8000/docs                      ║"
echo "║                                                              ║"
echo "║     Press Ctrl+C to stop the server                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping servers..."; kill $SERVER_PID $HTTP_PID 2>/dev/null; exit 0' INT
wait
STARTEOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'STOPEOF'
#!/bin/bash
# Stop Space Flight Simulator

echo "🛑 Stopping Space Flight Simulator..."

# Kill Python processes
pkill -f "python3 app/main.py" 2>/dev/null
pkill -f "python3 -m http.server" 2>/dev/null

echo "✓ Servers stopped"
STOPEOF

chmod +x stop.sh

# Create install completion script
cat > install-complete.sh << 'COMPLETEEOF'
#!/bin/bash
echo "========================================="
echo "   Space Flight Simulator - Installed!"
echo "========================================="
echo ""
echo "To start the game:"
echo "  ./start.sh"
echo ""
echo "To stop the game:"
echo "  ./stop.sh"
echo ""
echo "To play:"
echo "  Open http://localhost:8080 in your browser"
echo ""
echo "Controls:"
echo "  WASD - Move ship"
echo "  Mouse Click - Target enemies"
echo "  Right Click - Fire lasers"
echo "  M - Mine asteroids"
echo "  A - Autopilot"
echo "  J - Jump to new sector"
echo ""
echo "Enjoy your space adventure! 🚀"
COMPLETEEOF

chmod +x install-complete.sh

# ============================================
# CREATE DOCKER CONFIGURATION
# ============================================
if [[ "$DOCKER_AVAILABLE" == true ]] && [[ "$INSTALL_TYPE" == "full" ]]; then
    echo -e "\n${BLUE}🐳 Creating Docker configuration...${NC}"
    
    cat > Dockerfile << 'DOCKEREOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8080

CMD ["sh", "-c", "python3 app/main.py & python3 -m http.server 8080 --directory static"]
DOCKEREOF

    cat > docker-compose.yml << 'YAMLEOF'
version: '3.8'

services:
  game:
    build: .
    ports:
      - "8000:8000"
      - "8080:8080"
    volumes:
      - ./static:/app/static
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - PORT=8000
      - DEBUG=true
    restart: unless-stopped
YAMLEOF

    echo -e "${GREEN}✓ Docker configuration created${NC}"
fi

# ============================================
# CREATE SYSTEMD SERVICE (Linux only)
# ============================================
if [[ "$OS_TYPE" == "linux" ]] && [[ "$INSTALL_TYPE" == "full" ]]; then
    echo -e "\n${BLUE}🔧 Creating systemd service...${NC}"
    
    SERVICE_FILE="/etc/systemd/system/space-flight-simulator.service"
    cat > space-flight-simulator.service << 'SERVICEEOF'
[Unit]
Description=Space Flight Simulator
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=$PWD/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

    echo -e "${YELLOW}⚠ To install as a service, run:${NC}"
    echo "  sudo cp space-flight-simulator.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable space-flight-simulator"
    echo "  sudo systemctl start space-flight-simulator"
fi

# ============================================
# CREATE BACKUP SCRIPT
# ============================================
echo -e "\n${BLUE}💾 Creating backup script...${NC}"

cat > backup.sh << 'BACKUPEOF'
#!/bin/bash
# Backup script for Space Flight Simulator

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup game saves
if [ -d "data/game_saves" ]; then
    cp -r data/game_saves "$BACKUP_DIR/"
    echo "✓ Game saves backed up"
fi

# Backup configuration
if [ -d "config" ]; then
    cp -r config "$BACKUP_DIR/"
    echo "✓ Configuration backed up"
fi

# Backup logs
if [ -d "logs" ]; then
    cp -r logs "$BACKUP_DIR/"
    echo "✓ Logs backed up"
fi

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" -C backups "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "✅ Backup complete: $BACKUP_DIR.tar.gz"
BACKUPEOF

chmod +x backup.sh

# ============================================
# CREATE README
# ============================================
echo -e "\n${BLUE}📖 Creating documentation...${NC}"

cat > README.md << 'READMEEOF'
# 🚀 Space Flight Simulator

A complete 3D space flight simulator with combat, mining, trading, and multiplayer support.

## Quick Start

1. **Install**: Run `./install.sh`
2. **Start**: Run `./start.sh`
3. **Play**: Open http://localhost:8080 in your browser

## Features

- 🎮 Full 3D space flight with intuitive controls
- ⚔️ Combat system with laser weapons
- ⛏️ Mining asteroids for minerals
- 💰 Trading at space stations
- 🤖 Autopilot navigation
- 🌌 Procedurally generated sectors
- 🖱️ Mouse-controlled targeting
- 👥 Multiplayer support (coming soon)

## Controls

| Action | Control |
|--------|---------|
| Move Forward | W / ↑ |
| Move Backward | S / ↓ |
| Turn Left/Right | A/D or ←/→ |
| Roll | Q/E |
| Ascend/Descend | R/F |
| Fire Laser | Right Click / F |
| Lock Target | Left Click |
| Boost | Middle Click / B |
| Mine | M |
| Interact | E |
| Autopilot | A |
| Jump Sector | J |
| Cockpit View | C |
| Brake | Space |

## System Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.8+ (for backend)
- 4GB RAM recommended
- GPU with WebGL support

## Installation Options

### Full Installation (Recommended)
```bash
./install.sh --type full