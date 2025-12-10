Cryptojacking Detection & Behavioral Fingerprinting
==================================================
This project simulates cryptomining behavior and demonstrates detection via behavioral fingerprints.

Quickstart:
1. Create a virtual environment & install requirements:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Run detector (alert-only):
   python main.py

3. In another shell, run the miner simulator:
   python miner_simulator.py --intensity 2.0

4. Observe alerts in detector. When ready, enable kill behavior in detection_engine.Detector(..., kill=True).
