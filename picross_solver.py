from numpy import full, count_nonzero

def format_cell(cellval:str|None) -> str:
    if cellval is None: return "*"
    return ("⬚", "■")[cellval=="1"] #"□"

def format_nums(nums:list[str]|str) -> str:
    return " ".join([format_cell(cell) for cell in nums])

def combine_known_nums(numsA:list[str|None], numsB:list[str|None]) -> list[str|None]:
    return [A or numsB[i] for i, A in enumerate(numsA)]

class PicrossBoard:
    """
    creates a picross board object from two lists of whitespace-separated integer strings, for the number hints at the top (left to right) and on the left (top to bottom) respectively

    example: `(["3", "1 2 1", "1 3"], ["3", "1", "3", "2", "1", "1"])`
    to describe the board with the solution
    ```
    ■ ■ ■
    ■ ⬚ ⬚
    ■ ■ ■
    ⬚ ■ ■
    ⬚ ⬚ ■
    ⬚ ■ ⬚
    ```"""
    def __init__(self, horlist:list[str], verlist:list[str]) -> None:
        self.verlist = [[int(num) for num in string.split(" ")] for string in verlist]
        self.horlist = [[int(num) for num in string.split(" ")] for string in horlist]
        self.height  = len(self.verlist)
        self.width   = len(self.horlist)
        self.board   = full((self.height, self.width), None)

    def get_numsposs(self, nums:list[int], remain_len:int) -> set[str]:
        """
        finds all possible permutations for an empty line given its blocks' sizes and the amount of available space using recursion
        example: ([3], 5) finds all ways to fit one block of 3 into a 5 long line and will return {"11100", "01110", "00111"}
        example: ([2, 1], 5) finds all ways to fit one block of 2 and one block of 1 into a 5 long line and will return {"11010", "11001", "01101"} 
        """
        if nums == [ ]: return {""}
        if nums == [0]: return {"0"*remain_len}
        deg_of_free = 1 + remain_len - sum(nums) - len(nums)
        line_poss = set()

        for i in range(deg_of_free+1):
            string  = "0"*i + "1"*nums[0]
            if len(nums) > 1:
                string      += "0"
                after_blocks = self.get_numsposs(nums[1:], remain_len-len(string))
                line_poss.update({string + end for end in after_blocks})
            else:
                string      += "0"*(remain_len-len(string))
                line_poss.add(string)
        return line_poss

    def poss_intersection(self, line_poss:set[str]) -> list[str|None]:
        """
        finds the intersection of a set of block placements and returns a list with a cell state in each position that is known, and None where it isn't

        example: `{"10110", "10011"}` -> `["1", "0", None, "1", None]`
        """
        if len(line_poss) == 1: return list(*line_poss)
        line_poss = tuple(line_poss)
        validate = list(line_poss[0])
        for i, char in enumerate(validate):
            for poss in line_poss[1:]:
                if char == poss[i]: continue
                validate[i] = None
                break
        return validate

    def initial_possibilities(self):
        """
        finds all initial possibilities, and at the same time fills in all cells that are immediately known for sure

        example:

        ```
        * * * ■ ■ ■ * * *
        * * * ⬚ * ⬚ * * *
        ■ ⬚ ■ ■ ⬚ ■ ■ ⬚ ■
        * * * ■ * ■ * * *
        ■ * * ■ * ■ * * ■
        ■ * * ■ * ■ * * ■
        * * * ■ * ■ * * *
        ■ ⬚ ■ ■ ⬚ ■ ■ ⬚ ■
        * * * ⬚ * ⬚ * * *
        * * * ■ ■ ■ * * *
        ```
        """
        self.verposs = []
        for i, nums in enumerate(self.verlist):
            line_poss = self.get_numsposs(nums, self.width)
            self.verposs.append(line_poss)
            intersection = self.poss_intersection(line_poss)
            self.board[i] = intersection
        
        self.horposs = []
        for i, nums in enumerate(self.horlist):
            line_poss = self.get_numsposs(nums, self.height)
            self.horposs.append(line_poss)
            intersection = self.poss_intersection(line_poss)
            self.board[:, i] = combine_known_nums(self.board[:, i], intersection)

    def ruleout_rows(self):
        """
        rules out block placements that have been invalidated by the previous ruleout_cols(), and fills in if only one placement is possible 
        """
        for y in range(self.height):
            nums = self.board[y,:]
            possible = self.verposs[y]
            if len(possible) == 1:
                self.board[y,:] = [*list(possible)[0]]
                continue
            for i, c in enumerate(nums):
                if c is None: continue
                for poss in frozenset(possible):
                    if poss[i] != c: possible.remove(poss)
            if len(possible) == 1: self.board[y,:] = [*list(possible)[0]]
            

    def ruleout_cols(self):
        """
        rules out block placements that have been invalidated by the previous ruleout_rows(), and fills in if only one placement is possible 
        """
        for x in range(self.width):
            nums = self.board[:,x]
            possible = self.horposs[x]
            if len(possible) == 1:
                self.board[:,x] = [*list(possible)[0]]
                continue
            for i, c in enumerate(nums):
                if c is None: continue
                for poss in frozenset(possible):
                    if poss[i] != c: possible.remove(poss)
            if len(possible) == 1: self.board[:,x] = [*list(possible)[0]]

    def __str__(self):
        return "\n".join([" ".join([format_cell(cell) for cell in row]) for row in self.board])

    def remaining_squares(self): return count_nonzero(self.board == None)

    def solve(self):
        self.initial_possibilities()
        while (stuckcheck := self.remaining_squares()):
            self.ruleout_rows()
            self.ruleout_cols()
            #no progress made, assume board is unsolvable
            if stuckcheck == self.remaining_squares(): return None
        return self



if __name__ == "__main__":
    from os.path import dirname
    DIR = dirname(__file__)
    
    if True:
        with open(f"{DIR}/ex_easy.txt") as f:
            board1 = [line.split("\t") for line in f.readlines()]
        solve1 = PicrossBoard(*board1).solve()
        print("board1", *board1, sep="\n")
        print("solve1", solve1, sep="\n")

    if True:
        with open(f"{DIR}/ex_hard.txt") as f:
            board2 = [line.split("\t") for line in f.readlines()]
        solve2 = PicrossBoard(*board2).solve()
        print("board2", *board2, sep="\n")
        print("solve2", solve2, sep="\n")
    
    if True:
        board3 = [["1","1"],["1","1"]]
        solve3 = PicrossBoard(*board3).solve()
        print("board3", *board3, sep="\n")
        print("solve3", solve3, sep="\n")