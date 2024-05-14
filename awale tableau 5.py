from enum import Enum
from typing import List
import pygame

pygame.init()
screen = pygame.display.set_mode((843, 596))
running = True

color = (255, 0, 0)
image = pygame.image.load("plateau.png").convert()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        screen.blit(image, (0, 0))
        pygame.display.flip()
        
pygame.quit()

class GameState:
    def __init__(self, p1pad: List[int], p2pad: List[int], p1points: int, p2points: int):
        self.p1pad = p1pad
        self.p2pad = p2pad
        self.p1points = p1points
        self.p2points = p2points
    def getWinner(self) -> 'GameState.GamePlayer':
        if sum(self.p1pad) == 0:
            return self.GamePlayer.p2
        elif sum(self.p2pad) == 0:
            return self.GamePlayer.p1
        elif self.p1points >= 25:  # Définissez ici votre condition de victoire pour le joueur 1
            return self.GamePlayer.p1
        elif self.p2points >= 25:  # Définissez ici votre condition de victoire pour le joueur 2
            return self.GamePlayer.p2
        else:
            return None
    class GamePlayer(Enum):
        p1 = 1
        p2 = 2

    def evaluate(self, mainPlayer: 'GameState.GamePlayer' = GamePlayer.p1) -> int:
        v1 = sum(1 for p in self.p1pad if p == 1 or p == 2)
        v2 = sum(1 for p in self.p2pad if p == 1 or p == 2)
        if mainPlayer == self.GamePlayer.p1:
            return (2 * self.p2points + v1) - (2 * self.p1points + v2)
        elif mainPlayer == self.GamePlayer.p2:
            return (2 * self.p1points + v2) - (2 * self.p2points + v1)

    class CircularMatrix:
        def __init__(self, buffer: List[int], rowLength: int):
            self.buffer = buffer
            self.rowLength = rowLength

        @classmethod
        def from2Rows(cls, row0: List[int], row1: List[int]):
            if len(row0) != len(row1):
                raise Exception("Les lignes n'ont pas pas la même taille")
            rowLength = len(row0)
            return cls(buffer=row1 + list(reversed(row0)), rowLength=rowLength)

        def getCircularIndex(self, row: int, index: int) -> int:
            if index < 0 or index >= self.rowLength:
                raise Exception("Indexation en dehors des limites")
            return index if row == 1 else 2 * self.rowLength - 1 - index

        def getMatrixIndex(self, circularIndex: int) -> List[int]:
            if 0 <= circularIndex < self.rowLength:
                return [1, circularIndex]
            else:
                return [0, 2 * self.rowLength - 1 - circularIndex]

        def getRow1(self) -> List[int]:
            return self.buffer[:self.rowLength]

        def getRow0(self) -> List[int]:
            return list(reversed(self.buffer[self.rowLength:]))

    def _distributeHand(self, circularMatrix: 'GameState.CircularMatrix', player: 'GameState.GamePlayer', cavityIndex: int) -> int:
        row = 0 if player == self.GamePlayer.p1 else 1
        startIndex = circularMatrix.getCircularIndex(row, cavityIndex)
        hand = circularMatrix.buffer[startIndex]
        if hand == 0:
            return startIndex  # If the chosen cavity is empty, return the same index
        circularMatrix.buffer[startIndex] = 0
        index = startIndex

        while hand != 0:
            index = (index + 1) % len(circularMatrix.buffer)
            if index != startIndex:
                circularMatrix.buffer[index] += 1
                hand -= 1
        return index

    def _computeGains(self, circularMatrix: 'GameState.CircularMatrix', player: 'GameState.GamePlayer', lastCircularIndex: int) -> List[int]:
        index = lastCircularIndex
        lastRow, _ = circularMatrix.getMatrixIndex(lastCircularIndex)
        gains = 0

        def isGaining(idx):
            return circularMatrix.buffer[idx] == 2 or circularMatrix.buffer[idx] == 3

        isPlayer1Jackpot = player == self.GamePlayer.p1 and lastRow == 1
        isPlayer2Jackpot = player == self.GamePlayer.p2 and lastRow == 0
        if not isPlayer1Jackpot and not isPlayer2Jackpot:
            return [0, 0]
        sameRow = True
        gaining = True
        while sameRow and gaining:
            row, _ = circularMatrix.getMatrixIndex(index)
            sameRow = row == lastRow
            gaining = isGaining(index)
            if sameRow and gaining:
                gains += circularMatrix.buffer[index]
                circularMatrix.buffer[index] = 0
                index -= 1
                if index < 0:
                    index = len(circularMatrix.buffer) - 1
        return [gains if isPlayer1Jackpot else 0, gains if isPlayer2Jackpot else 0]

    def simulate(self, player: 'GameState.GamePlayer', cavityIndex: int) -> 'GameState':
        circularMatrix = self.CircularMatrix.from2Rows(self.p1pad, self.p2pad)
        lastCircularIndex = self._distributeHand(circularMatrix, player, cavityIndex)
        p1gains, p2gains = self._computeGains(circularMatrix, player, lastCircularIndex)
        return GameState(
            p1pad=circularMatrix.getRow0(),
            p2pad=circularMatrix.getRow1(),
            p1points=self.p1points + p1gains,
            p2points=self.p2points + p2gains
        )

    _infinty = 0xFFFFFFFF
    _invalidMove = -100


class AlphaBetaContext:
    def __init__(self, currentState: GameState, mainPlayer: GameState.GamePlayer, maxDepth: int):
        self.currentState = currentState
        self.mainPlayer = mainPlayer
        self.maxDepth = maxDepth

    def getAvailableMoves(self, player: GameState.GamePlayer) -> List[int]:
        if player == GameState.GamePlayer.p1:
            return [i for i, v in enumerate(self.currentState.p1pad) if v > 0]
        else:
            return [i for i, v in enumerate(self.currentState.p2pad) if v > 0]

    def _min(self, state: GameState, depth: int, alpha: int, beta: int, moveNo: int, mainPlayer: GameState.GamePlayer) -> List[int]:
        bestMoveValue = state._infinty
        bestMoveId = state._invalidMove
        availableMoves = self.getAvailableMoves(mainPlayer)
        if depth == self.maxDepth or not availableMoves:
            return [moveNo, state.evaluate(mainPlayer)]
        for move in availableMoves:
            simulated = state.simulate(mainPlayer, move)
            _, moveValue = self._max(simulated, depth + 1, alpha, beta, move, mainPlayer)
            if moveValue < bestMoveValue:
                bestMoveValue = moveValue
                bestMoveId = move
            beta = min(beta, bestMoveValue)
            if beta <= alpha:
                break
        return [bestMoveId, bestMoveValue]

    def _max(self, state: GameState, depth: int, alpha: int, beta: int, moveNo: int, mainPlayer: GameState.GamePlayer) -> List[int]:
        bestMoveValue = -state._infinty
        bestMoveId = state._invalidMove
        oppositePlayer = GameState.GamePlayer.p2 if mainPlayer == GameState.GamePlayer.p1 else GameState.GamePlayer.p1
        availableMoves = self.getAvailableMoves(oppositePlayer)
        if depth == self.maxDepth or not availableMoves:
            return [moveNo, state.evaluate(mainPlayer)]
        for move in availableMoves:
            simulated = state.simulate(oppositePlayer, move)
            _, moveValue = self._min(simulated, depth + 1, alpha, beta, move, mainPlayer)
            if moveValue > bestMoveValue:
                bestMoveValue = moveValue
                bestMoveId = move
            alpha = max(alpha, bestMoveValue)
            if beta <= alpha:
                break
        return [bestMoveId, bestMoveValue]

    def guessBestMove(self) -> int:
        availableMoves = self.getAvailableMoves(self.mainPlayer)
        if not availableMoves:
            return self.currentState._invalidMove
        move, _ = self._min(self.currentState, 0, -self.currentState._infinty, self.currentState._infinty, self.currentState._invalidMove, self.mainPlayer)
        return move


def displayGameState(state: GameState):
    # état jeu console (voir tuto jeu à afficher sur console)
    print("╭─────────┬────────┬────────┬────────┬────────┬────────┬──────╮")
    print("│  (0)    │  (1)   │  (2)   │  (3)   │  (4)   │  (5)   │  P   │")
    print("├─────────┼────────┼────────┼────────┼────────┼────────┼──────┤")
    print(f"│  {state.p1pad[0]:^7}│{state.p1pad[1]:^7} │{state.p1pad[2]:^7} │{state.p1pad[3]:^7} │{state.p1pad[4]:^7} │{state.p1pad[5]:^7} │ IA   │")
    print(f"│  {state.p2pad[0]:^7}│{state.p2pad[1]:^7} │{state.p2pad[2]:^7} │{state.p2pad[3]:^7} │{state.p2pad[4]:^7} │{state.p2pad[5]:^7} │ p1   │")
    print("╰─────────┴────────┴────────┴────────┴────────┴────────┴──────╯")
    print("╭────────────┬──────────╮")
    print(f"│   Gains IA │ Gains p1 │")
    print("├────────────┼──────────┤")
    print(f"│  {state.p1points:^10}│{state.p2points:^10}│")
    print("╰────────────┴──────────╯")

def main():
    print("Simulateur de l'awalé")
    state = GameState([4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4], 0, 0)
    player = GameState.GamePlayer.p2
    opposite = GameState.GamePlayer.p1
    while True:
        displayGameState(state)
        while True:
            move = int(input(f"[{player.name}] Choisissez une case [0-{len(state.p1pad) - 1}] (-1 pour quitter) : "))
            if move == -1:
                break
            if player == GameState.GamePlayer.p1:
                if 0 <= move <= 5 and state.p1pad[move] != 0:
                    break
                else:
                    print("Veuillez choisir une case entre 0 et 5 contenant des graines.")
            else:
                if 0 <= move <= 5 and state.p2pad[move] != 0:
                    break
                else:
                    print("Veuillez choisir une case entre 0 et 5 contenant des graines.")
        if move == -1:
            break
        state = state.simulate(player, move)

        # Vérifier si un joueur n'a plus de graines
        if sum(state.p1pad) == 0 or sum(state.p2pad) == 0:
            winner = state.getWinner()
            if winner is not None:
                print(f"Le joueur {winner.name} a gagné !")
                break
            else:
                print("Match nul ! Les deux joueurs n'ont plus de graines.")
                break

        aiContext = AlphaBetaContext(currentState=state, mainPlayer=opposite, maxDepth=10)
        bestAIMove = aiContext.guessBestMove()
        if bestAIMove != -100:
            print(f"L'IA a joué la case N°{bestAIMove} !")
            state = state.simulate(opposite, bestAIMove)
        else:
            print("L'IA ne peut pas jouer.")

        # Vérifier si un joueur n'a plus de graines
        if sum(state.p1pad) == 0 or sum(state.p2pad) == 0:
            winner = state.getWinner()
            if winner is not None:
                print(f"Le joueur {winner.name} a gagné !")
                break
            else:
                print("Match nul ! Les deux joueurs n'ont plus de graines.")
                break


if __name__ == "__main__":
    main()
