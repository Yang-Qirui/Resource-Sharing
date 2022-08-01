from math import inf


class Node:
    def __init__(self, loc, step, back=False):
        self.back = back
        self.step = step
        self.loc = loc


class Solution:
    def minimumJumps(self, forbidden, a: int, b: int, x: int) -> int:
        bfs = [Node(0, 0)]
        forbidden.sort()
        max_range = max(forbidden[-1] + a + b, x + b)
        while bfs:
            head = bfs.pop(0)
            if head.loc == x:
                return head.step
            if not head.back:
                if head.loc - b not in forbidden and head.loc - b >= 0:
                    if head.loc - b <= max_range:
                        bfs.append(Node(head.loc - b, head.step + 1, True))
            if head.loc + a not in forbidden:
                if head.loc + a <= max_range:
                    bfs.append(Node(head.loc + a, head.step + 1))
        return -1


if __name__ == "__main__":
    s = Solution()
    print(s.minimumJumps([162, 118, 178, 152, 167, 100, 40, 74, 199, 186, 26, 73, 200, 127, 30, 124, 193, 84, 184, 36, 103, 149, 153, 9, 54,
          154, 133, 95, 45, 198, 79, 157, 64, 122, 59, 71, 48, 177, 82, 35, 14, 176, 16, 108, 111, 6, 168, 31, 134, 164, 136, 72, 98], 29, 98, 80))
