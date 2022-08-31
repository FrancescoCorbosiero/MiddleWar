import pygame
import pickle

from entities import *


# Stampa il player vincitore
def draw_winner(team: Team):
    pause_text = Env.PAUSE_FONT.render(f"Player {team.team} wins!", 1, Color.BLACK)
    Env.WIN.blit(pause_text, (Env.WIDTH / 2 - pause_text.get_width() / 2,
                              Env.HEIGHT / 2 - pause_text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(3000)


# Stampa tutte le entità di gioco presenti più le relative scritte
def draw_window(environment: [Box], player1: Team, player2: Team):
    for unit in environment + player1.buildings + player2.buildings + player1.dispatched + player2.dispatched:
        unit.draw()

    p1_offset = 0
    for msg in player1.errors + player1.logs:
        color = Color.RED if msg in player1.errors else Color.BLACK
        Env.WIN.blit(Env.FONT.render(msg, 1, color), (20, 20 + p1_offset))
        p1_offset += 10

    p2_offset = 0
    for msg in player2.errors + player2.logs:
        color = Color.RED if msg in player2.errors else Color.BLACK
        Env.WIN.blit(Env.FONT.render(msg, 1, color), (Env.WIDTH / 2 + 150, 20 + p2_offset))
        p2_offset += 10

    Env.WIN.blit(Env.FONT.render(f"GOLD: {player1.gold}", 1, Color.BLACK), (20, 130))
    Env.WIN.blit(Env.FONT.render(f"HP: {player1.get_hp()}", 1, Color.BLACK), (20, 140))

    Env.WIN.blit(Env.FONT.render(f"GOLD: {player2.gold}", 1, Color.BLACK), (Env.WIDTH / 2 + 150, 130))
    Env.WIN.blit(Env.FONT.render(f"HP: {player2.get_hp()}", 1, Color.BLACK), (Env.WIDTH / 2 + 150, 140))

    pygame.display.update()


def main():
    # Titolo della finestra di gioco
    pygame.display.set_caption("Castles War!")

    # Inizializzazione delle entità di gioco
    background = Background()
    ground = Ground()
    player1 = Team(Team.BLACK)
    player2 = Team(Team.RED)

    '''
    L'applicativo si basa su un ciclo while potenzialmente infinito.
    Ad ogni ciclo vengono controllati gli eventi presenti nel gioco.
    A seconda dell'evento vengono modificati gli stati delle entità di gioco.
    Alla fine di ogni ciclo la libreria grafica pygame permette di stampare a video le entità di gioco a 60 FPS.
    '''
    run = True
    pause = False
    clock = pygame.time.Clock()     # Scandisce i frame per second (FPS)
    slot = None
    while run:
        clock.tick(Env.FPS)         # 60 FPS

        # Controlla ogni evento presente nel gioco
        for event in pygame.event.get():

            # Se l'evento è QUIT allora il gioco si chiude (l'utente chiude la finestra)
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

            # L'utente ha premuto un tasto
            if event.type == pygame.KEYDOWN:
                # Evento per la scrittura del salvataggio
                if event.key == pygame.K_b:
                    if slot is not None:
                        with open('save.pickle', 'wb') as handle:
                            pickle.dump(slot, handle, protocol=pickle.HIGHEST_PROTOCOL)
                            print("===== SLOT OVERRIDDEN ========\n" + str(slot))

                # Evento per il caricamento del salvataggio
                # Se non è presente nessun salvataggio, ne effettua uno
                if event.key == pygame.K_v:
                    try:
                        with open('save.pickle', 'rb') as handle:
                            slot = pickle.load(handle)
                    except FileNotFoundError:
                        slot = {"player1": player1, "player2": player2}
                        with open('save.pickle', 'wb') as handle:
                            pickle.dump(slot, handle, protocol=pickle.HIGHEST_PROTOCOL)
                            print("===== SLOT SAVED ========\n" + str(slot))
                    else:
                        player1 = slot["player1"]
                        player2 = slot["player2"]

                # Evento per la pausa
                if event.key == pygame.K_SPACE:
                    pause = not pause
                    pause_text = Env.PAUSE_FONT.render("PAUSE - press Spacebar", 1, Color.BLACK)
                    Env.WIN.blit(pause_text, (Env.WIDTH/2 - pause_text.get_width() / 2,
                                              Env.HEIGHT/2 - pause_text.get_height()/2))
                    pygame.display.update()

                if not pause:
                    # Evento relativo allo spawn dei personaggi (utente preme Q,W,E ecc..)
                    player1.handle_key(event.key)
                    player2.handle_key(event.key)

            # Gestione degli eventi relativi allo stato delle entità
            player1.handle_events(event)
            player2.handle_events(event)

            # Controllo sul giocatore vincitore
            # if player1.gold < Worker.COST:
            #     if not player1.dispatched + player1.swordsman + player1.workers + player1.archers + player1.to_mine:
            #         player2.winner = True
            # if player2.gold < Worker.COST:
            #     if not player2.dispatched + player2.swordsman + player2.workers + player2.archers + player2.to_mine:
            #         player1.winner = True
            if player1.winner:
                draw_winner(player1)
                return True
            elif player2.winner:
                draw_winner(player2)
                return True

        if not pause:
            p1_dispatched = player1.dispatched
            p2_dispatched = player2.dispatched
            p1_buildings = player1.buildings
            p2_buildings = player2.buildings

            player1.play(p2_dispatched, p2_buildings)
            player2.play(p1_dispatched, p1_buildings)

            environment = [background, ground]
            # Stampa a schermo
            draw_window(environment, player1, player2)


if __name__ == "__main__":
    while True:
        main()
