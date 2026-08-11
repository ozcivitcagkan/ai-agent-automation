sinif_A = [68, 70, 72, 70, 70]     
sinif_B = [20, 100, 45, 95, 90]     

def medyan(a):
   
   sirali = sorted(a)
   orta = len(sirali) // 2

   if len(sirali) % 2 == 1:
      return sirali[orta]
   else:
      return (sirali[orta] + sirali[orta - 1]) / 2


print(medyan([3, 1, 2]))       
print(medyan([4, 1, 3, 2]))    
print(medyan(sinif_A))
print(medyan(sinif_B))
