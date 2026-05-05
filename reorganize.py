import os
import shutil

base_path = "/Users/mayur/Downloads/Automotive-Predictive-Maintenance-System-main-3"
os.chdir(base_path)

def move_safe(src, dst):
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")
    else:
        print(f"Skipping {src}, not found")

# Create directories
dirs = [
    "ml/training", "ml/inference", "ml/models", "ml/notebooks",
    "data/raw", "data/processed", "database", "scripts", "config", "tests", "docs",
    "backend/api", "backend/services", "backend/models", "backend/schemas",
    "backend/core", "backend/agents", "backend/templates"
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Moves
move_safe("enhanced_train_data.csv", "data/raw/enhanced_train_data.csv")
move_safe("enhanced_vehicle_data_v4.csv", "data/raw/enhanced_vehicle_data_v4.csv")
move_safe("synthetic_vehicle_data.csv", "data/raw/synthetic_vehicle_data.csv")
move_safe("maintenance.db", "database/maintenance.db")
move_safe("train_model_v3.py", "ml/training/train_model_v3.py")
move_safe("train_model_v4.py", "ml/training/train_model_v4.py")
move_safe("vehicle_failure_model_v3.pkl", "ml/models/vehicle_failure_model_v3.pkl")
move_safe("vehicle_failure_model_v4.pkl", "ml/models/vehicle_failure_model_v4.pkl")
move_safe("betterdataset.ipynb", "ml/notebooks/betterdataset.ipynb")
move_safe("seed_data.py", "scripts/seed_data.py")
move_safe("test_email.py", "scripts/test_email.py")
move_safe("trigger_alert.py", "scripts/trigger_alert.py")

# Frontend
if os.path.exists("frontend-vite"):
    shutil.move("frontend-vite", "frontend")
    print("Renamed frontend-vite to frontend")

# Backend (app folder)
if os.path.exists("app"):
    move_safe("app/main.py", "backend/main.py")
    
    for f in os.listdir("app/routers"):
        if f.endswith(".py"):
            move_safe(os.path.join("app/routers", f), os.path.join("backend/api", f))
            
    for f in os.listdir("app/services"):
        if f.endswith(".py"):
            move_safe(os.path.join("app/services", f), os.path.join("backend/services", f))
            
    for f in os.listdir("app/schemas"):
        if f.endswith(".py"):
            move_safe(os.path.join("app/schemas", f), os.path.join("backend/schemas", f))
            
    for f in os.listdir("app/models"):
        if f.endswith(".py"):
            move_safe(os.path.join("app/models", f), os.path.join("backend/models", f))

    # Other folders
    for d in ["core", "agents", "templates"]:
        src_dir = os.path.join("app", d)
        if os.path.exists(src_dir):
            for f in os.listdir(src_dir):
                src_file = os.path.join(src_dir, f)
                dst_file = os.path.join("backend", d, f)
                move_safe(src_file, dst_file)

# Cleanup
for f in ["test.db", "feature_importance_v4.png"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed {f}")

if os.path.exists(".pytest_cache"):
    shutil.rmtree(".pytest_cache")
    print("Removed .pytest_cache")

# Fix imports in backend
def fix_imports_in_dir(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    content = f.read()
                
                # Replace app. with backend.
                new_content = content.replace("from app.", "from backend.")
                new_content = new_content.replace("import app.", "import backend.")
                
                if new_content != content:
                    with open(path, "w") as f:
                        f.write(new_content)
                    print(f"Fixed imports in {path}")

fix_imports_in_dir("backend")
fix_imports_in_dir("scripts")

# Fix model paths in backend/services/ml_service.py
ml_service_path = "backend/services/ml_service.py"
if os.path.exists(ml_service_path):
    with open(ml_service_path, "r") as f:
        content = f.read()
    
    # Update paths to point to ml/models/
    new_content = content.replace("vehicle_failure_model_v4.pkl", "ml/models/vehicle_failure_model_v4.pkl")
    new_content = new_content.replace("../ml/models/", "ml/models/") # Adjust if needed
    
    with open(ml_service_path, "w") as f:
        f.write(new_content)
    print(f"Updated model paths in {ml_service_path}")
