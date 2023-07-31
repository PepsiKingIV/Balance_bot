if __name__ == '__main__':

    types1 = ['food', 'car', 'fun']
    types2 = ['car', 'fun', 'relax']
    
    def append_types(types1, types2):    
        
        
        if type(types2) == type([]):
            for i in types1:
                types2.append(i)
                    
            unique_types = set(types2)
            types2 = []
            for i in unique_types:
                types2.append(i)
            return types2

    print(append_types(types1, types2))
    msg = 'Рука блудца, нина, Очко, БЛЯДУН'
    
    msg2 = []
    msg = msg.lower()
    msg = msg.split(',')
    for i in msg:
        i = i.strip()
        i.replace
        msg2.append(i)
    
    print(msg2)

 