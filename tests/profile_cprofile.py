import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import cProfile
import pstats
import os
import socket
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

PROFILES_DIR = Path(__file__).parent / "profiles"
PROFILES_DIR.mkdir(exist_ok=True)


def get_effective_db_url(url: str) -> str:
    if "@db:" in url:
        try:
            socket.gethostbyname("db")
        except socket.gaierror:
            return url.replace("@db:", "@localhost:")
    return url


os.environ["DATABASE_URL"] = get_effective_db_url(settings.DATABASE_URL)


def profile_endpoint(endpoint_name: str, request_func, iterations: int = 50):
    profiler = cProfile.Profile()
    profiler.enable()
    
    for _ in range(iterations):
        request_func()
        
    profiler.disable()
    
    prof_filename = PROFILES_DIR / f"{endpoint_name}.prof"
    profiler.dump_stats(prof_filename)
    print(f"Profile Stats saved for [{endpoint_name}] -> {prof_filename}")
    
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(15)


def run_all_profiles():
    client = TestClient(app)
    
    profile_endpoint("get_root", lambda: client.get("/"))
    profile_endpoint("get_health", lambda: client.get("/health"))
    profile_endpoint("get_ready", lambda: client.get("/ready"))
    
    def create_and_list():
        res = client.post("/tickets/", json={"title": "Profiling ticket", "priority": "high"})
        if res.status_code == 201:
            ticket_id = res.json()["id"]
            client.get(f"/tickets/{ticket_id}")
            client.delete(f"/tickets/{ticket_id}")
        client.get("/tickets/")

    profile_endpoint("tickets_crud_flow", create_and_list, iterations=20)


if __name__ == "__main__":
    print("Starting cProfile profiling session...")
    run_all_profiles()
    print("Profiling completed successfully!")
