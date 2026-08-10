
def nokta_carpim(a, b):
    toplam = 0

    for i in range(len(a)):
        toplam = toplam + (a[i] * b[i])

    return toplam
        


# [1,2,3] 4 14 32
# [4,5,6]

print(nokta_carpim([1,2,3],[4,5,6]))