import pygame
from src.game import Game
import sys
import os

if __name__ == "__main__":
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    print(r"""

______ _            _   ______                        
| ___ \ |          | |  | ___ \                       
| |_/ / | ___   ___| | _| |_/ / ___   ___  _ __ ___   
| ___ \ |/ _ \ / __| |/ / ___ \/ _ \ / _ \| '_ ` _ \  
| |_/ / | (_) | (__|   <| |_/ / (_) | (_) | | | | | | 
\____/|_|\___/ \___|_|\_\____/ \___/ \___/|_| |_| |_| 
                                                      
                                                    
                                                            
    """)
    pygame.init()
    pygame.mixer.init()
    game = Game()
    # Lance la musique seulement si le son est activé
    if game.sound_enabled:
        try:
            pygame.mixer.music.load("sounds/1.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print("Erreur lors de la lecture du son :", e)
    game.run()
    pygame.quit() 