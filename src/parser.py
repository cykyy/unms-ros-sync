class ParseString:
    # parsing password from client registration/adding to crm date
    # input example: 2020-08-14T00:00:00+0600
    # output: 1482020
    def parse_regdate(self, rg):
        x = rg
        lhs, rhs = x.split('T', 1)

        y = lhs
        temp = y.split('-')

        f = ''
        count = 0
        for xx in temp[1]:
            if xx == '0' and count == 0:
                continue
            else:
                f += xx
            count += 1

        g = ''
        count = 0
        for xy in temp[2]:
            if xy == '0' and count == 0:
                continue
            else:
                g += xy
            count += 1

        final = g + f + temp[0]
        return final