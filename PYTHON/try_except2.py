

def guvenli_bol(a,b):
    try: 
        return a/b
    except ZeroDivisionError:
        print("Sıfıra bölme yapılamaz!")
        return None



print(guvenli_bol(10,0))
    


