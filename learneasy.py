import random

class OmwesoBoard:
    def __init__(self):
        # 4 rows of 8 pits.
        # Rows 0-1 belong to Player 2 (Computer), Rows 2-3 belong to Player 1 (Human).
        self.board = [
            [4, 4, 4, 4, 4, 4, 4, 4],  # Row 0: P2 Outer
            [4, 4, 4, 4, 4, 4, 4, 4],  # Row 1: P2 Inner
            [4, 4, 4, 4, 4, 4, 4, 4],  # Row 2: P1 Inner
            [4, 4, 4, 4, 4, 4, 4, 4]   # Row 3: P1 Outer
        ]

    def display(self):
        print("\n" + "=" * 55)
        print("          COMPUTER (Player 2)")
        print("    Outer (Row 0): " + str(self.board[0]))
        print("    Inner (Row 1): " + str(self.board[1]))
        print("-" * 55)
        print("    Inner (Row 2): " + str(self.board[2]))
        print("    Outer (Row 3): " + str(self.board[3]))
        print("            YOU (Player 1)")
        print("=" * 55 + "\n")

    def custom_setup(self, player):
        """Allows strategic arrangement of 32 seeds across a player's 8 inner and outer pits."""
        print(f"\n--- Player {player} Strategic Setup ---")
        choice = input("Do you want to use the standard setup (4 seeds in each of the 8 pits)? (y/n): ").strip().lower()
        if choice == 'y':
            return
        
        try:
            print("Enter 8 numbers for your Inner Row (Row 2), summing up to 16:")
            inner = [int(x) for x in input("Inner row: ").split()]
            print("Enter 8 numbers for your Outer Row (Row 3), summing up to 16:")
            outer = [int(x) for x in input("Outer row: ").split()]
            
            if len(inner) == 8 and len(outer) == 8 and sum(inner) + sum(outer) == 32:
                self.board[2] = inner
                self.board[3] = outer
                print("Custom setup applied successfully!")
            else:
                print("Invalid totals. Must sum exactly to 32 seeds. Falling back to default 4-per-pit setup.")
        except Exception:
            print("Invalid input format. Falling back to default 4-per-pit setup.")

    def get_player_pits(self, player):
        if player == 1:
            return [2, 3]
        else:
            return [1, 0]

    def get_legal_moves(self, player):
        rows = self.get_player_pits(player)
        legal_moves = []
        for r in rows:
            for c in range(8):
                if self.board[r][c] >= 2:
                    legal_moves.append((r, c))
        return legal_moves

    def play_turn(self, player, row, col):
        rows = self.get_player_pits(player)
        
        if row not in rows:
            print("Invalid move: That row does not belong to you.")
            return False
        if not (0 <= col < 8):
            print("Invalid move: Column must be between 0 and 7.")
            return False
        if self.board[row][col] < 2:
            print("Invalid move: You can only play a pit with 2 or more seeds.")
            return False

        # Execute Sowing and Relays
        current_row, current_col = row, col
        seeds = self.board[row][col]
        self.board[row][col] = 0

        print(f"Player {player} sowing {seeds} seeds starting from row {row}, col {col}...")

        while seeds > 0:
            current_col = (current_col - 1) % 8
            if current_col == 7:
                current_row = rows[0] if current_row == rows[1] else rows[1]

            self.board[current_row][current_col] += 1
            seeds -= 1

            if seeds == 0 and self.board[current_row][current_col] > 1:
                seeds = self.board[current_row][current_col]
                self.board[current_row][current_col] = 0
                print(f"Relay triggered from row {current_row}, col {current_col}! Picking up {seeds} seeds.")

        # Check for capture (Only if landing on the player's INNER row)
        inner_row = rows[0]
        if current_row == inner_row and self.board[current_row][current_col] > 0:
            if player == 1:
                opp_inner, opp_outer = 1, 0
            else:
                opp_inner, opp_outer = 2, 3

            opp_seeds_total = self.board[opp_inner][current_col] + self.board[opp_outer][current_col]
            if opp_seeds_total > 0:
                print(f"*** CAPTURE! Player {player} captured {opp_seeds_total} seeds from column {current_col}! ***")
                # Clear opponent pits
                self.board[opp_inner][current_col] = 0
                self.board[opp_outer][current_col] = 0
                
                # True Omweso Rule: Re-sow captured seeds starting from the landing pit
                print(f"Re-sowing {opp_seeds_total} captured seeds from row {current_row}, col {current_col}...")
                resow_seeds = opp_seeds_total
                resow_row, resow_col = current_row, current_col
                
                while resow_seeds > 0:
                    resow_col = (resow_col - 1) % 8
                    if resow_col == 7:
                        resow_row = rows[0] if resow_row == rows[1] else rows[1]
                    self.board[resow_row][resow_col] += 1
                    resow_seeds -= 1
                    
                    if resow_seeds == 0 and self.board[resow_row][resow_col] > 1:
                        resow_seeds = self.board[resow_row][resow_col]
                        self.board[resow_row][resow_col] = 0
                        print(f"Relay triggered during re-sow from row {resow_row}, col {resow_col}!")

        return True

    def ai_turn(self):
        legal_moves = self.get_legal_moves(2)
        if not legal_moves:
            return False
        chosen_move = random.choice(legal_moves)
        print(f"Computer chooses row {chosen_move[0]}, column {chosen_move[1]}")
        return self.play_turn(2, chosen_move[0], chosen_move[1])

def main():
    game = OmwesoBoard()
    print("Welcome to Omweso (Full Feature Edition)!")
    
    # Optional custom setup phase
    game.custom_setup(1)
    
    current_player = 1
    while True:
        game.display()
        legal_moves = game.get_legal_moves(current_player)
        if not legal_moves:
            winner = 2 if current_player == 1 else 1
            print(f"Player {current_player} has no legal moves left! Player {winner} WINS!")
            break

        if current_player == 1:
            print("Your turn (Player 1).")
            try:
                row = int(input("Enter your row index (2 for Inner, 3 for Outer): "))
                col = int(input("Enter your column index (0-7): "))
            except ValueError:
                print("Please enter valid integer coordinates.")
                continue

            success = game.play_turn(1, row, col)
            if success:
                current_player = 2
        else:
            print("Computer's turn (Player 2)...")
            success = game.ai_turn()
            if success:
                current_player = 1

if __name__ == "__main__":
    main()
