# Master_camp_project

Ceci est notre projet sur le réseau de métro et RER parisien. Il s’agit d’une application full stack avec un Front End développé en Vue.js et un Back End propulsé par FastAPI.
---

## 🖥️ Front End

📁 Accédez au dossier `front_end` :

```bash
cd front_end
```

🔧 Installez les dépendances :

```bash
npm install
```

🚀 Lancez le serveur de développement :

```bash
npm run dev
```

---

## 🧠 Back End

📁 Accédez au dossier `fastapi-backend` :

```bash
cd fastapi-backend
```

🐍 Installez les dépendances Python :

```bash
pip install -r requirements.txt
```

🔥 Lancez le serveur FastAPI :

```bash
python -m uvicorn app.main:app --reload
```

---

## ⚙️ Pré-requis supplémentaires

🛠️ Pour pouvoir utiliser **Cython** et l’implémentation de **l’algorithme de Yen**, il est nécessaire d’avoir installé les **compilateurs C de Microsoft** (par exemple via l’installation de **Microsoft C++ Build Tools**).

📂 Placez tous les fichiers texte du GTFS **IDFM** fournis par l’**Efrei** dans le dossier suivant :

```bash
fastapi-backend/app/V2_text_files
```

Ces fichiers sont indispensables pour que le traitement des données de transport fonctionne correctement.

