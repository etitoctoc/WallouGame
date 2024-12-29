import random
import time
import sys

#### fonctions pour simuler l'environnement extérieur

terminal_animation = ["." * i for i in range(100)]

class Timer:
    def __init__(self, duration, waitinglist):
        self.time = float(duration)
        self.waitinglist = waitinglist
        self.waitinglist_nummer = 0
        self.positionnull = time.time()
        self.finished = False
        self.lasttimeframe = time.time()
        self.timeframe_limit = 0.01

    def tick(self):
        if time.time() - self.positionnull > self.time:
            print(" ;)")
            self.finished = True
            return True

        if self.finished:
            return False

        if time.time() - self.lasttimeframe > self.timeframe_limit:
            sys.stdout.write(f"\r{self.waitinglist[self.waitinglist_nummer]}")
            sys.stdout.flush()
            self.lasttimeframe = time.time()

            self.waitinglist_nummer = (self.waitinglist_nummer + 1) % len(self.waitinglist)

def timer(duration, anim=terminal_animation):
    timer = Timer(duration, anim)
    while not timer.tick():
        pass

def graphics(mylist):
    while True:
        print("______\n\nCHOIX : ")
        for idx, item in enumerate(mylist, start=1):
            print(f"   {idx}. {item}")

        res = input("\nVotre choix : ")
        try:
            res = int(res)
        except ValueError:
            print("Votre réponse n'est pas un chiffre !")
            continue

        if 1 <= res <= len(mylist):
            return mylist[res - 1]
        else:
            print("Réponse incorrecte !")

#### Jeu

class Wallou:
    dicelist = []
    rolled_dicelist = []

    class Player:
        def __init__(self, name, list_players):
            self.nom = name
            self.score = 0.0
            self.score_round = 0.0
            self.score_round_save = 0.0
            self.list_players = list_players
            self.list_players.append(self)

    class Dice:
        def __init__(self):
            self.result = None
            self.canberolled = True
            Wallou.dicelist.append(self)

        def roll(self):
            if self.canberolled:
                self.result = random.randint(1, 6)
                Wallou.rolled_dicelist.append(self)

    class GameRound:
        def __init__(self, player):
            self.player = player

        def check_redondancies(self, lst, limit):
            counts = {}
            for num in lst:
                counts[num] = counts.get(num, 0) + 1
                if counts[num] >= limit:
                    return num
            return False

        def evaluation_point(self):
            self.player.score_round = 0
            list_score = [i.result for i in Wallou.rolled_dicelist]
            test_3 = self.check_redondancies(list_score, 3)
            test_4 = self.check_redondancies(list_score, 4)
            test_5 = self.check_redondancies(list_score, 5)

            if list_score.count(1) == 5:
                self.player.score_round = 30
                print("Quintuple 1 !")
            elif list_score.count(1) == 4:
                self.player.score_round = 20
                print("Quadruple 1 !")
            elif list_score.count(1) == 3:
                self.player.score_round = 10
                print("Triple 1 !")
            elif sorted(list_score) in ([2, 3, 4, 5, 6], [1, 2, 3, 4, 5]):
                print("Suite !")
                for dice in Wallou.dicelist:
                    dice.canberolled = False
                self.player.score_round = 10
            elif test_5:
                print(f"QUINTUPLE {test_5} !")
                self.player.score_round += test_5 * 3
                for dice in Wallou.rolled_dicelist:
                    if dice.result == int(test_5):
                        dice.canberolled = False
            elif test_4:
                print(f"Quadruple {test_4}")
                self.player.score_round += test_4 * 2
                for dice in Wallou.rolled_dicelist:
                    if dice.result == int(test_4):
                        dice.canberolled = False
            elif test_3:
                print(f"Triple {test_3}")
                self.player.score_round += test_3
                for dice in Wallou.rolled_dicelist:
                    if dice.result == int(test_3):
                        dice.canberolled = False
            else:
                for dice in Wallou.rolled_dicelist:
                    if dice.result == 1:
                        self.player.score_round += 1
                        dice.canberolled = False
                    elif dice.result == 5:
                        self.player.score_round += 0.5
                        dice.canberolled = True

            self.player.score_round_save += self.player.score_round

            print(f"Score du round : {self.player.score_round_save}")

        def check_for_reroll(self):
            for dice in Wallou.dicelist:
                if dice.result == 1:
                    dice.canberolled = False

        def roll_all_once(self):
            Wallou.rolled_dicelist = []
            rollable_dice = [dice for dice in Wallou.dicelist if dice.canberolled]
            for dice in rollable_dice:
                dice.roll()
            timer(1)
            print(f"\n\n      o o o    {[dice.result for dice in Wallou.rolled_dicelist]}    o o o \n")

    def __init__(self):
        self.history = []
        self.list_players = []

        self.player = self.Player("Joueur", self.list_players)
        self.opponent = self.Player("Opposant véhément", self.list_players)

        self.currently_playing = self.opponent

        for _ in range(5):
            self.Dice()

        print(f"Joueurs : {len(self.list_players)}: {self.list_players[0].nom}, {self.list_players[1].nom}")

    def select_player(self):
        self.currently_playing = next(player for player in self.list_players if player != self.currently_playing)
        print(f"C'est au tour de {self.currently_playing.nom} de jouer !")

    def dice_reset(self):
        for dice in Wallou.dicelist:
            dice.canberolled = True
        Wallou.rolled_dicelist = []
        print("Dés remis à zéro.")

    def round_game(self):
        self.dice_reset()
        game = self.GameRound(self.currently_playing)
        self.currently_playing.score_round_save = 0

        if self.currently_playing == self.player:
            list_choice = ["Lancer les dés", "Quitter"]
            choice = graphics(list_choice)
            if choice == list_choice[1]:
                print("Vous quittez, lâche.")
                exit()
            else:
                print("Lancement des dés...")

        while True:
            previous_score = self.currently_playing.score_round_save
            game.roll_all_once()
            game.evaluation_point()
            game.check_for_reroll()

            rollable_dice = [dice for dice in Wallou.dicelist if dice.canberolled]
            if previous_score == self.currently_playing.score_round_save:
                print(random.choice(["CARAMBA ! C'EST LE WALLOU !", "Aie aie aie ! Wallou !!!", "WALLOU MON PAUVRE MILOU !", "COCOOOOOTTE ? Non... Wallou !", "ENFER ET DAMNATION, C'EST LE WALLOU !", "WALLOUSTROPHIE !"]))
                break
            else:
                print(f"{len(rollable_dice)} dés peuvent être relancés.")
                if not rollable_dice:
                    print("Tous les dés sont utilisés ! Tous doivent être relancés, et le joueur gagne 5 points supplémentaire.")
                    self.currently_playing.score_round_save += 5
                    self.dice_reset()

                if float(self.currently_playing.score_round_save).is_integer():
                    print("Score rond ! Le joueur peut s'arrêter là... ou suivre le lapin du gain et continuer !")
                    list_choice2 = ["Continuer", "Arrêter là."]
                    choice2 = random.choice(list_choice2) if self.currently_playing == self.opponent else graphics(list_choice2)
                    if choice2 == list_choice2[0]:
                        print("Dés disponibles relancés.")
                    else:
                        print("Score de round sauvé !")
                        self.currently_playing.score += self.currently_playing.score_round_save
                        break
                else:
                    print("Impossible de rester avec un score en 0.5 ! Les dés doivent être relancés !")
                    self.currently_playing.score_round_save -= 0.5
                    if self.currently_playing != self.opponent:
                        graphics(["Continuer"])
                    print("Dés disponibles relancés.")


    def game_main(self):
        while True:
            self.select_player()
            self.round_game()
            print(f"""\n\n     ==== TABLEAU DES SCORES  =========================\n     {[[p.nom, p.score] for p in self.list_players] }\n     ==================================================""")
            input("\n\n--- CHANGEMENT DE JOUEUR - Appuyez sur une touche ---\n\n")


            if self.currently_playing.score > 15:
                print(f"{self.currently_playing.nom} a gagné !!!")
                break

def wallou_launch():
    wallou = Wallou()
    wallou.game_main()

wallou_launch()
