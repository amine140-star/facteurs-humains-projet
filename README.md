# StressEcho

**StressEcho** est un projet Python qui mesure et affiche le niveau de stress d’un·e utilisateur·rice en temps réel via une interface Pygame.

## Prérequis

* **Python 3.10+** (idéalement via Conda ou venv)
* **BITalino (r)evolution Plugged Kit BLE/BT** avec capteurs ECG, ACC, EDA
* Bibliothèques Python :

  * pygame
  * pyserial (si communication série)
  * numpy
  * scipy (pour le traitement du signal)

## Installation

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/amine140-star/StressEcho-projet-.git
   cd StressEcho-projet-
   ```

2. **Créer et activer un environnement virtuel**
   Avec Conda :

   ```bash
   conda create -n stressecho python=3.10
   conda activate stressecho
   ```

   Ou avec venv :

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\\Scripts\\activate   # Windows
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration BITalino

1. Allumer le module BITalino en mode Bluetooth.
2. Vérifier le port série où il est connecté :

   * Sur Windows, consultez le **Gestionnaire de périphériques**.
   * Sur Linux/macOS, utilisez `ls /dev/tty.*` ou `dmesg | grep tty`.
3. Modifier le script `config.py` (ou `ACC.py`) pour indiquer le port (ex. `COM3` ou `/dev/tty.BITalino-XX`).

## Lancement du projet

1. **Démarrer l’application**

   ```bash
   python ACC.py
   ```

2. **Interagir avec l’interface**

   * Appuyer sur `S` pour lancer la capture.
   * Appuyer sur `Q` pour quitter.

## Structure du projet

```text
StressEcho-projet-/
│
├─images/             # captures d’écran et logos
├─ACC.py              # test du capteur ACC
├─ECG.py              # test du capteur ECG
├─EDA.py              # test du capteur EDA
├─config.py           # configuration des ports et seuils
├─requirements.txt    # dépendances Python
└─README.md           # ce fichier
```

## Dépannage

* **Segmentation fault** lors du `import pygame` :

  * Assurez-vous que la version de Pygame (2.6.1) est compatible avec votre système.
  * Réinstallez via `pip uninstall pygame && pip install pygame`.
* **Erreur de port série** :

  * Vérifiez la valeur de `BITALINO_PORT` dans `config.py`.
  * Assurez-vous que l’appareil est bien appairé en Bluetooth.

## Collaborateurs

* Mohamed Amine SOUID
* Marcelin ADE

## Licence

Ce projet est libre d’utilisation sous licence MIT.
