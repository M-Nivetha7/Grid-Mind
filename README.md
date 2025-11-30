<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=45&duration=3000&pause=1000&color=00FF00&center=true&vCenter=true&width=1000&lines=GridMind%3A+Smart+Traffic+Control+Simulator" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/traffic-light-green-red-yellow.gif" width="200">
</p>

---

## 🚦 About GridMind

GridMind is a Python and Pygame based traffic intersection simulator. It observes vehicle queues on both directions and dynamically changes traffic signals to improve flow and reduce waiting times.

---

## 🎯 Features

* Real time queue monitoring  
* Adaptive green light switching  
* Starvation prevention logic  
* Visual simulation for experimentation  

---

## 🎮 How it Works

```mermaid
flowchart LR
A[Vehicle Detection] --> B[Queue Estimation]
B --> C[Adaptive Decision Controller]
C --> D[Signal Switching]
D --> E[Smoother Traffic Flow]
```

🚀 Run Locally
git clone https://github.com/your-username/GridMind.git
cd GridMind
pip install pygame
python main.py

