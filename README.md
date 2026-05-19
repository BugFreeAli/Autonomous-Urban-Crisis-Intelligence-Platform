<div align="center">
  <h1>🌍 CrisisOS</h1>
  <p><b>Autonomous Crisis Management & Predictive Resource Optimization Matrix</b></p>
  <p><i>Turning Chaos into Calculated Strategy During Real-World Crises.</i></p>
</div>

---

## 🚨 The Challenge
In the critical first hours of a natural disaster, conflict, or infrastructure collapse, the greatest enemy is **fog of war**. Emergency response systems are often fragmented, relying on manual data entry, human deduction, and delayed communication. This leads to inefficient resource allocation, overwhelmed dispatchers, and delayed critical care where it’s needed most.

## 💡 The Solution
**CrisisOS** is an autonomous, AI-driven command system designed as an antidote to emergency chaos. Powered by a swarm of **9 specialized AI Agents** (built on Gemini 2.0 Flash), a high-speed FastAPI backend, and a portable Next.js/Capacitor mobile architecture, CrisisOS acts as a central **"System Brain."** 

It continuously ingests complex crisis signals, predicts stress points, and autonomously routes resources—optimizing logistics on a live geographic map in real time. It answers the question: *Who needs what, and how fast can we get it to them?*

---

## ✨ Key Features
- **🧠 9-Agent Neural Network:** A dedicated swarm of AI agents (Strategic, Logistics, Medical, etc.) that analyze multi-modal signals and make instant, collective decisions.
- **🛰️ Live Spatial Mapping:** A high-performance Leaflet command map with a Z-index locked view, providing a live, uninterrupted feed of ground-zero events.
- **⚡ Real-Time WebSockets:** Zero-latency two-way communication between the Python AI Brain and the Mobile Dashboard.
- **📱 Mobile-First Native APK:** Shipped using Next.js static exports and Capacitor, allowing field commanders to manage logistics directly from their Android devices.
- **📊 Adaptive Load Balancing:** Calculates the precise burn-rate of resources (water, medical, personnel) and alerts command before exhaustion.

---

## 🛠️ Architecture & Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js, React, TailwindCSS, Framer Motion | High-fidelity, animated, responsive field dashboard. |
| **Mapping Engine** | Leaflet.js | Real-time geospatial tracking of units and crises. |
| **Mobile Core** | Capacitor.js, Android Studio | Wraps the web app into a native, deployable Android APK. |
| **System Brain** | FastAPI (Python), Uvicorn | High-speed async backend managing WebSocket streams. |
| **AI Intelligence**| Google Gemini 2.0 Flash | Powers the autonomous decision-making agents. |

---

## 🚀 Getting Started

Follow these steps to set up the localized network and run the application.

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)
- **Android Studio** (for compiling the APK)
- **Google Gemini API Key**

---

### Step 1: Configure the System Brain (Backend)
The backend requires your Gemini API key to operate the agents. **We take API security seriously.**

1. Rename the example environment file to activate it:
   ```bash
   mv .env.example .env
   ```
2. Open `.env` and insert your API key:
   ```env
   GEMINI_API_KEY="AIzaSy...your...key...here"
   ```
   *(Note: The `.gitignore` is pre-configured to ensure your `.env` file is **never** committed or leaked to GitHub).*
3. Install the Python dependencies:
   ```bash
   pip install fastapi uvicorn google-generativeai websockets
   ```
4. Start the Uvicorn server on your local network:
   ```bash
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```
   *The server is now listening for connections from the mobile app.*

---

### Step 2: Configure the Dashboard (Frontend)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the development server (for web browsers):
   ```bash
   npm run dev
   ```

---

### Step 3: Build the Android App (APK)
CrisisOS is designed to be deployed directly to Android devices for field usage.

1. Ensure the frontend is built statically (requires `output: 'export'` in `next.config.js`):
   ```bash
   cd frontend
   npm run build
   ```
2. Sync the compiled frontend into the Capacitor Android shell:
   ```bash
   npx cap sync android
   ```
3. Open the project in Android Studio to compile the APK:
   ```bash
   npx cap open android
   ```
4. **Android Configuration Notes:** 
   We have already pre-configured `networkSecurityConfig` and `AndroidManifest.xml` to allow `cleartextHttpTraffic`. This ensures the app can successfully communicate with local IP addresses (e.g., `http://192.168.x.x:8000`) without raising HTTPS security blocks during development on local networks.

---

## 🛡️ License
Distributed under the **MIT License**. See `LICENSE` for more information.

---
<p align="center"><i>"Logistics wins wars. AI wins time. Time saves lives."</i></p>