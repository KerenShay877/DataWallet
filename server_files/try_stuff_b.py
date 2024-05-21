import server_files
"""
list = [["a", 'b"b"', "0"],["c", 'bb"d"', "0"],["e", 'bb"f"', "0"]]
s0 = str(list)
print(s0)
s1 = s0[2:-2]
print(s1)
s2 = s1.split("], [")
print(s2)
for i in range(len(s2)):
    s2[i] = s2[i].split(", ")
    s2[i][0] = s2[i][0][1:-1]
    s2[i][1] = s2[i][1][1:-1]
    s2[i][2] = s2[i][2][1:-1]
print(s2)"""
a = None
print()
print((not isinstance(a, type(None))) == (type(a) != type(None)))
