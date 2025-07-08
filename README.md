# Master_camp_project

This is a full stack project with a **Front End** built using modern JavaScript frameworks and a **Back End** powered by **FastAPI**. The project includes a **high-performance C extension** for fast pathfinding algorithms.

---

## � Quick Start

### Option 1: Automated Installation
```bash
python install.py
```

### Option 2: Manual Installation (see below)

---

## ⚡ Performance Features

This project includes a **fast C implementation** of Yen's K-shortest paths algorithm for optimal performance:

- **With C extension**: Metro pathfinding in ~1-5ms per query
- **Without C extension**: Same operations 100-1000x slower

**Important**: For full performance, you need to build the C extension. See [YEN_INSTALLATION.md](YEN_INSTALLATION.md) for detailed instructions.

---

## �🖥️ Front End

📁 Navigate to the `front_end` directory:

```bash
cd front_end
```

🔧 Install dependencies:

```bash
npm install
```

🚀 Start the development server:

```bash
npm run dev
```

---

## 🧠 Back End

📁 Navigate to the `fastapi-backend` directory:

```bash
cd fastapi-backend
```

🐍 Install Python dependencies:

```bash
pip install -r requirements.txt
```

🔧 **Build the C extension (recommended for performance):**

```bash
# From project root
python build_wheels.py
```

🔥 Run the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

---

## 🛠️ C Extension Setup

The project uses a C extension for fast pathfinding. If you encounter import errors:

1. **Quick build**: Run `python build_wheels.py`
2. **Detailed instructions**: See [YEN_INSTALLATION.md](YEN_INSTALLATION.md)
3. **No C compiler?** The app works without the extension (with reduced performance)

---
