import datetime

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
    print('datetime.date(2023, 7, 28)')
    fds = {'1' : 1, '2' : 2, '3' : 3}
 #datetime.date(2023, 7, 28), datetime.time(16, 32, 3), Decimal('23343.85'), True, 'инвестиции'
    for i, j in fds, range(3):
        print(i)
        print(j)