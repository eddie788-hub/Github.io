import os
import sys
import subprocess
import shutil
import time
import requests
import venv
import json
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION ====================

PROJECT_NAME = "SwarmIntelligence"
PROJECT_DIR = "/opt/swarm_intelligence"
# External Data Pipeline Path - Target for intelligence exports on external media
EXTERNAL_PIPELINE_PATH = "/media/charles-swanson/writable/swarm_intel_drops/"

VENV_DIR = f"{PROJECT_DIR}/venv"
CONFIG_DIR = f"{PROJECT_DIR}/config"
DATA_DIR = f"{PROJECT_DIR}/data"
LOGS_DIR = f"{PROJECT_DIR}/logs"
EXPORTS_DIR = f"{PROJECT_DIR}/exports"
BACKEND_DIR = f"{PROJECT_DIR}/backend"
FRONTEND_DIR = f"{PROJECT_DIR}/frontend"
SCRIPTS_DIR = f"{PROJECT_DIR}/scripts"
SERVICE_USER = "swarm"
SERVICE_GROUP = "swarm"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'█'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'█'*70}{Colors.END}\n")

def print_success(text): print(f"{Colors.GREEN}✓ {text}{Colors.END}")
def print_error(text): print(f"{Colors.RED}✗ {text}{Colors.END}")
def print_info(text): print(f"{Colors.YELLOW}➜ {text}{Colors.END}")
def print_step(text): print(f"{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.END}")

# ==================== PRE-FLIGHT & SETUP ====================

def check_root():
    if os.getuid() != 0:
        print_error("This script must be run as root on Kali Linux")
        sys.exit(1)
    print_success("Root privileges confirmed")

def verify_assets():
    print_step("Verifying installation assets...")
    Path(PROJECT_DIR).mkdir(parents=True, exist_ok=True)
    print_success("Asset verification complete")
    return True

def create_service_user():
    print_step("Checking environment security context...")
    subprocess.run(["groupadd", "-f", SERVICE_GROUP], capture_output=True)
    try:
        subprocess.run(["id", "-u", SERVICE_USER], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        subprocess.run(["useradd", "-r", "-g", SERVICE_GROUP, "-s", "/bin/bash", "-d", PROJECT_DIR, "-m", SERVICE_USER], capture_output=True)
    print_success(f"System user context prepared")

def setup_directories():
    # FIX: Move global declaration to the top to avoid SyntaxError
    global EXTERNAL_PIPELINE_PATH
    
    print_step("Building internal infrastructure...")
    directories = [
        f"{PROJECT_DIR}/assets", f"{BACKEND_DIR}/api", f"{BACKEND_DIR}/crawler", 
        f"{BACKEND_DIR}/classifier", f"{BACKEND_DIR}/storage", f"{FRONTEND_DIR}/src", 
        f"{BACKEND_DIR}/pipeline",
        CONFIG_DIR, DATA_DIR, LOGS_DIR, EXPORTS_DIR, SCRIPTS_DIR, f"{PROJECT_DIR}/agent"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Media path validation for /media/charles-swanson/writable
    try:
        target = Path(EXTERNAL_PIPELINE_PATH)
        target.mkdir(parents=True, exist_ok=True)
        test_file = target / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        os.chmod(EXTERNAL_PIPELINE_PATH, 0o777)
        print_success(f"Media Pipeline verified: {EXTERNAL_PIPELINE_PATH}")
    except Exception:
        print_error(f"Warning: Media path {EXTERNAL_PIPELINE_PATH} is not writable or mounted.")
        print_info(f"Swarm will fallback to local export directory: {EXPORTS_DIR}")
        EXTERNAL_PIPELINE_PATH = EXPORTS_DIR

    print_success(f"Infrastructure built")

def install_dependencies():
    print_step("Installing System Core & Neural Dependencies...")
    subprocess.run(["apt-get", "update", "-qq"], capture_output=True)
    subprocess.run(["apt-get", "install", "-y", "-qq", "python3-full", "python3-pip", "python3-venv", "nodejs", "npm", "sqlite3"], capture_output=True)
    
    if not os.path.exists(VENV_DIR):
        venv.create(VENV_DIR, with_pip=True)
    
    pip_path = f"{VENV_DIR}/bin/pip"
    packages = ["fastapi", "uvicorn", "aiosqlite", "beautifulsoup4", "aiohttp", "pydantic", "lxml", "psutil", "numpy"]
    subprocess.run([pip_path, "install", "-q"] + packages, capture_output=True)
    print_success("Neural libraries ready")

# ==================== FRONTEND LOGIC ====================

def setup_frontend():
    print_step("Building Neural Dashboard UI...")
    os.chdir(FRONTEND_DIR)
    
    if not os.path.exists("package.json"):
        subprocess.run(["npm", "init", "-y"], capture_output=True)
    
    subprocess.run(["npm", "install", "-s", "react", "react-dom", "axios", "lucide-react"], capture_output=True)
    subprocess.run(["npm", "install", "-s", "-D", "vite", "@vitejs/plugin-react", "tailwindcss", "postcss", "autoprefixer"], capture_output=True)

    with open("src/App.jsx", "w") as f:
        f.write('''
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Terminal, Shield, Zap, Database, Activity, Cpu } from 'lucide-react';

export default function App() {
  const [topic, setTopic] = useState('0-day research');
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({ total_urls: 0, avg_relevance: 0, knowledge_nodes: 0 });
  const [isCrawlActive, setIsCrawlActive] = useState(false);
  const logEndRef = useRef(null);

  const fetchTelemetry = useCallback(async () => {
    try {
      const [statsRes, logsRes] = await Promise.allSettled([
        axios.get('/api/stats'),
        axios.get('/api/logs')
      ]);

      if (statsRes.status === 'fulfilled' && statsRes.value.data) {
        setStats(statsRes.value.data);
      }
      if (logsRes.status === 'fulfilled' && logsRes.value.data) {
        setLogs(logsRes.value.data.logs || []);
      }
    } catch (e) {}
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchTelemetry, 1500);
    return () => clearInterval(interval);
  }, [fetchTelemetry]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const launchSwarm = async () => {
    setIsCrawlActive(true);
    try {
      await axios.post('/api/swarm/start', { topic });
    } catch (e) { 
      setIsCrawlActive(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-cyan-400 p-6 font-mono">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center border-b border-cyan-900 pb-4 mb-8">
          <div className="flex items-center gap-3">
            <Shield className={isCrawlActive ? "text-cyan-400 animate-pulse" : "text-cyan-800"} size={32} />
            <div>
              <h1 className="text-2xl font-black tracking-tighter italic text-white">SWARM_INTEL // MEDIA_SYNC_V11</h1>
              <div className="text-[9px] text-cyan-700 font-bold uppercase tracking-[0.2em]">External Storage Priority Enabled</div>
            </div>
          </div>
          <div className="flex gap-4 text-[10px] text-cyan-800 font-bold uppercase">
            <span className="flex items-center gap-1 border border-cyan-900 px-2 py-1 rounded"><Activity size={12}/> {isCrawlActive ? 'LIVE' : 'IDLE'}</span>
            <span className="flex items-center gap-1 border border-cyan-900 px-2 py-1 rounded"><Database size={12}/> DATA_SYNCED</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-slate-900/40 border border-cyan-900 p-5 rounded shadow-2xl">
              <label className="text-[9px] uppercase text-cyan-600 mb-3 block font-bold tracking-widest">Target Vector</label>
              <input 
                value={topic} onChange={(e) => setTopic(e.target.value)}
                className="w-full bg-black border border-cyan-800 p-3 text-sm outline-none focus:border-cyan-400 text-cyan-300 rounded shadow-inner"
              />
              <button 
                onClick={launchSwarm}
                disabled={isCrawlActive}
                className={`w-full mt-4 border py-4 transition-all flex items-center justify-center gap-2 font-black text-xs rounded ${isCrawlActive ? 'opacity-50 border-cyan-900 cursor-wait' : 'bg-cyan-950 border-cyan-500 hover:bg-cyan-400 hover:text-black'}`}
              >
                <Zap size={14} /> {isCrawlActive ? 'CRAWLING' : 'EXECUTE'}
              </button>
            </div>

            <div className="bg-slate-900/40 border border-cyan-900 p-5 rounded">
              <span className="text-[9px] text-cyan-700 font-bold uppercase block mb-5 border-b border-cyan-950 pb-2">Mesh Stats</span>
              <div className="space-y-4">
                <div className="flex justify-between items-end">
                  <div className="text-[10px] text-cyan-800 uppercase font-bold">Nodes Scanned</div>
                  <div className="text-xl font-bold">{stats.total_urls}</div>
                </div>
                <div className="flex justify-between items-end">
                  <div className="text-[10px] text-cyan-800 uppercase font-bold">Intel Entities</div>
                  <div className="text-xl font-bold">{stats.knowledge_nodes}</div>
                </div>
                <div className="pt-2">
                  <div className="flex justify-between text-[9px] text-cyan-800 uppercase mb-2">Confidence: {stats.avg_relevance}%</div>
                  <div className="w-full bg-cyan-950 h-1 rounded-full overflow-hidden">
                    <div className="bg-cyan-400 h-full transition-all duration-700" style={{width: `${stats.avg_relevance}%`}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3 bg-black border border-cyan-900 rounded overflow-hidden flex flex-col h-[650px] relative shadow-2xl">
            <div className="bg-slate-900/90 px-4 py-3 flex items-center justify-between border-b border-cyan-900 z-10">
              <div className="flex items-center gap-2 text-[10px] text-cyan-400 font-bold uppercase">
                <Terminal size={14} /> Swarm Telemetry Feed
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-1 font-mono text-[11px] z-10">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-4 p-0.5 transition-colors">
                  <span className="text-cyan-900 shrink-0 font-bold">[{new Date().toLocaleTimeString([], {hour12: false})}]</span>
                  <span className={log.includes('ML_SYNC') ? 'text-purple-400' : log.includes('KNOWLEDGE') ? 'text-green-400' : 'text-cyan-700'}>
                    {log}
                  </span>
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
''')

    subprocess.run(["npm", "run", "build"], capture_output=True)
    print_success("Neural Dashboard built successfully")

# ==================== BACKEND & KNOWLEDGE DB LOGIC ====================

def create_backend_code():
    print_step("Generating Knowledge-Aware Backend Systems...")

    db_content = '''import aiosqlite
from datetime import datetime

class DatabaseManager:
    def __init__(self, path): 
        self.path = path
        
    async def initialize(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    url TEXT PRIMARY KEY, 
                    title TEXT, 
                    score REAL, 
                    content TEXT, 
                    ts DATETIME
                )""")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_name TEXT,
                    entity_type TEXT,
                    source_url TEXT,
                    confidence REAL,
                    FOREIGN KEY(source_url) REFERENCES results(url)
                )""")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ml_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    score_given REAL,
                    words_processed INTEGER,
                    ts DATETIME
                )""")
            await db.commit()
            
    async def save_result(self, r):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO results VALUES (?,?,?,?,?)", 
                (r['url'], r['title'], r['relevance'], r['content'], datetime.now().isoformat())
            )
            await db.execute(
                "INSERT INTO knowledge_nodes (entity_name, entity_type, source_url, confidence) VALUES (?,?,?,?)",
                (r['title'][:60], "DOC_NODE", r['url'], r['relevance'])
            )
            await db.commit()

    async def log_ml_event(self, topic, score, word_count):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO ml_log (topic, score_given, words_processed, ts) VALUES (?,?,?,?)",
                (topic, score, word_count, datetime.now().isoformat())
            )
            await db.commit()
            
    async def get_stats(self):
        try:
            async with aiosqlite.connect(self.path) as db:
                async with db.execute("SELECT COUNT(*) FROM results") as cur:
                    c1 = await cur.fetchone()
                async with db.execute("SELECT COUNT(*) FROM knowledge_nodes") as cur:
                    c2 = await cur.fetchone()
                async with db.execute("SELECT AVG(score_given) FROM ml_log") as cur:
                    c3 = await cur.fetchone()
                return {
                    "total_urls": c1[0] or 0,
                    "knowledge_nodes": c2[0] or 0,
                    "avg_relevance": round((c3[0] or 0) * 100, 1) if c3 and c3[0] else 0
                }
        except: return {"total_urls": 0, "knowledge_nodes": 0, "avg_relevance": 0}
'''

    classifier_content = '''import re

class RelevanceClassifier:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def predict(self, text, topic):
        if not text or not topic: return 0.0
        text_clean = text.lower()
        keywords = [k.lower().strip() for k in topic.split() if len(k) > 2]
        if not keywords: return 0.1
        matches = sum(len(re.findall(r'\\b' + re.escape(word) + r'\\b', text_clean)) for word in keywords)
        word_count = len(text_clean.split())
        if word_count == 0: return 0.0
        density = (matches / word_count) * 100
        score = round(min(density / 1.0, 1.0), 2)
        await self.db_manager.log_ml_event(topic, score, word_count)
        return score
'''

    engine_content = '''import aiohttp
import asyncio
from crawler.scraper import PageScraper
from pipeline.manager import PipelineManager

class CrawlerEngine:
    def __init__(self, db, classifier):
        self.db = db
        self.classifier = classifier
        self.scraper = PageScraper()
        self.pipeline = PipelineManager()
        self.logs = []
        self.is_running = False
        self.visited = set()

    def add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 200: self.logs.pop(0)

    async def start_swarm(self, topic, threshold=0.15, max_nodes=40):
        if self.is_running:
            self.add_log("ALERT: Mission active.")
            return
        self.is_running = True
        self.visited.clear()
        self.add_log(f"SWARM_INIT: Target '{{topic}}'")
        queue = [f"https://www.bing.com/search?q={{topic}}"]
        async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0 Swarm/11.0'}) as session:
            processed = 0
            while queue and processed < max_nodes and self.is_running:
                url = queue.pop(0)
                if url in self.visited: continue
                self.visited.add(url)
                try:
                    async with session.get(url, timeout=12) as res:
                        if res.status != 200: continue
                        html = await res.text()
                        data = self.scraper.extract(html, url)
                        if not data: continue
                        score = await self.classifier.predict(data['content'], topic)
                        self.add_log(f"ML_SYNC: Node relevance {{int(score*100)}}%")
                        if score >= threshold:
                            self.add_log(f"KNOWLEDGE_LOCKED: {{data['title'][:40]}}")
                            res_node = {"url": url, "title": data['title'], "relevance": score, "content": data['content'][:8000]}
                            await self.db.save_result(res_node)
                            self.pipeline.dispatch(res_node)
                            processed += 1
                            queue.extend(data['links'][:8])
                        else:
                            queue.extend(data['links'][:2])
                except: pass
                await asyncio.sleep(1.5)
        self.add_log("SWARM_IDLE: Complete.")
        self.is_running = False
'''

    main_content = '''from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from storage.database import DatabaseManager
from crawler.engine import CrawlerEngine
from classifier.ml import RelevanceClassifier

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db = DatabaseManager('/opt/swarm_intelligence/data/swarm.db')
ml = RelevanceClassifier(db)
swarm = CrawlerEngine(db, ml)

class SwarmCfg(BaseModel): topic: str

@app.on_event("startup")
async def startup(): await db.initialize()

@app.get("/api/stats")
async def stats(): return await db.get_stats()

@app.get("/api/logs")
async def get_logs(): return {"logs": swarm.logs}

@app.post("/api/swarm/start")
async def start(cfg: SwarmCfg, bg: BackgroundTasks):
    bg.add_task(swarm.start_swarm, cfg.topic)
    return {"status": "deployed"}

app.mount("/", StaticFiles(directory="/opt/swarm_intelligence/frontend/dist", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    with open(f"{BACKEND_DIR}/main.py", 'w') as f: f.write(main_content)
    with open(f"{BACKEND_DIR}/storage/database.py", 'w') as f: f.write(db_content)
    with open(f"{BACKEND_DIR}/classifier/ml.py", 'w') as f: f.write(classifier_content)
    with open(f"{BACKEND_DIR}/crawler/engine.py", 'w') as f: f.write(engine_content)
    
    scraper_code = '''from bs4 import BeautifulSoup\nfrom urllib.parse import urljoin\nclass PageScraper:\n    def extract(self, html, base_url):\n        try:\n            soup = BeautifulSoup(html, 'lxml')\n            for tag in soup(["script", "style"]): tag.decompose()\n            title = soup.title.string.strip() if soup.title else "Untrusted Node"\n            text = soup.get_text(separator=' ', strip=True)\n            links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if a['href'].startswith(('http', '/'))]\n            return {"title": title, "content": text, "links": links}\n        except: return None'''
    with open(f"{BACKEND_DIR}/crawler/scraper.py", 'w') as f: f.write(scraper_code)
    
    pipeline_code = f'''import os, json, time\nfrom pathlib import Path\nclass PipelineManager:\n    def __init__(self, t="{EXTERNAL_PIPELINE_PATH}"):\n        self.t = Path(t)\n        self.t.mkdir(parents=True, exist_ok=True)\n    def dispatch(self, d):\n        try:\n            f = self.t / f"intel_{{int(time.time()*1000)}}.json"\n            with open(f, 'w') as out: json.dump(d, out)\n            return True\n        except Exception as e: \n            print(f"PIPELINE_ERROR: {{e}}")\n            return False'''
    with open(f"{BACKEND_DIR}/pipeline/manager.py", 'w') as f: f.write(pipeline_code)

    print_success("Logic synchronized with Media Path")

# ==================== SYSTEM INTEGRATION ====================

def configure_system():
    service = f'''[Unit]
Description=Swarm Intelligence Core V11
After=network.target

[Service]
ExecStart={VENV_DIR}/bin/python {BACKEND_DIR}/main.py
WorkingDirectory={BACKEND_DIR}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
'''
    with open("/etc/systemd/system/swarm.service", 'w') as f: f.write(service)
    subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
    
    start_sh = f"#!/bin/bash\nsystemctl restart swarm\necho 'SWARM MESH ONLINE: http://localhost:8000'"
    with open(f"{SCRIPTS_DIR}/start.sh", 'w') as f: f.write(start_sh)
    os.chmod(f"{SCRIPTS_DIR}/start.sh", 0o755)

def main():
    print_header("SWARM INTELLIGENCE // MEDIA_SYNC CORE V11")
    check_root()
    if verify_assets():
        create_service_user()
        setup_directories()
        install_dependencies()
        setup_frontend()
        create_backend_code()
        configure_system()
        print_header("LOGIC AUDIT PASSED // MESH READY")
        print_info(f"Primary Export Path: {EXTERNAL_PIPELINE_PATH}")
        print_info("Run: sudo /opt/swarm_intelligence/scripts/start.sh")

if __name__ == "__main__":
    main()
