# Flyingohm
Code source de la télécommande FlyingOhm

## 1. Présentation générale de FlyingOhm
FlyingOhm est un projet de paramoteur électrique (ULM classe 1).
Le paramoteur est constitué : d'un chassis, d'un moteur (avec hélice), d'une batterie, d'un controleur moteur et d'une télécommande.

Lien vers la page facebook : https://www.facebook.com/FlyingOhm/
Lien vers la page youtube : https://youtube.com/@SebastienGOSSE

## 2. Présentation du projet FlyingOhm
Le projet concerne le code source de la télécommande qui permet :
-De controler le moteur

## 3. Fonctionnalités
### Etats et modes
Il existe 3 états : INIT, DISARMED, ARMED
Dans l'état Init, lo logo FlyingOhm s'affiche ainsi que la version du firmware.
Dans l'état Disarmed, la télécommande envoie un PWM de 1000us (moteur OFF)
Dans l'état Armed, la télécommande envoie au controleur la consigne retournée par le potentiomètre

Le passage de l'état Init à Disarmed se fait automatiquement au bout de quelques secondes.
Le passage de l'état Disarmed à Armed se fait lorsque le pilote a appuyer sur le bouton poussoir (séquence appui court + appui long)
Le passage de l'état Armed à Disaremd se fait lorsque le pilote appui de facon courte sur le bouton poussoir.

Un switch de sécurité est présent sous la télécommande. Si celui ci est actionné, la télécommande n'est plus alimentée et le controleur ne recoit plus de signal PWM => Le moteur s'arrête.

### Signal PWM
Le signal PWM est l'élément principal à envoyer au controleur du moteur.
Le PWM a une fréquence de 50Hz (durée du signal de 1000us = 0%, 2000us = 100%)
### Affichage écran
### Lecture des données du controleur
Le controleur envoie un signal UART contenant plusieurs informations intéressantes à exploiter, notamment :
-La tension totale de la batterie
-La température du controleur
-Le courant instantanée

Réference de la documentation du controleur : https://docs.powerdrives.net/products/hv_pro/uart-telemetry-output

## 4. BOM et Pinout
Le projet est constitué (entre autres) :
-d'un raspberry pico pi
-d'un écran ST7735R
-d'un potentiomètre connecté sur GP27
-d'un bouton poussoir lumineux connecté sur GP15 (GP14 pour l'éclairage du bouton)
-d'un buzzer connecté sur GP12

## 5. PCB
Deux PCB existent : le premier pour la poignée principale qui contient notamment la pico pi et le potentiometre.
<p align="center">
  <img src="PCB_POIGNEE_3D_RUN1.png" width="350" title="Représentation 3D du PCB principal">  
  <img src="PCB_POIGNEE_2D_RUN1.png" width="350" title="Routage du PCB principal">
</p>

Le second PCB intègre l'écran ainsi que le bouton poussoir. Ce deuxième PCB est soudé à la vertical sur le PCB principal.
<p align="center">
  <img src="PCB_ECRAN_3D_RUN1.png" width="350" title="Représentation 3D du PCB écran">  
</p>

## 6. Impression 3D de la télécommande
La télécommande est ensuite imprimée en 3D et intègre les PCB, ainsi que le cable électrique connecté au controleur.
<p align="center">
  <img src="IMPRESSION_TELECOMMANDE.jpg" width="350" title="Impression de la télcommande">  
  <img src="TELECOMMANDE_3D.png" width="350" title="Modélisation 3D de la télcommande">  
</p>

