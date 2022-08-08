class Solution:

    def makeLargestSpecial(self, s: str) -> str:
        # print(s)
        if len(s) <= 2:
            return s
        cnt = left = 0
        specials = []
        for i, c in enumerate(s):
            if c == '1':
                cnt += 1
            else:
                cnt -= 1
            if cnt == 0:
                specials.append(f"1{self.makeLargestSpecial(s[left + 1:i])}0")
                left = i + 1
        specials.sort(reverse=True)
        return "".join(specials)


s = Solution()
print(s.makeLargestSpecial('11011000'))
