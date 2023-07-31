

class telegram_user:
    
    def __init__(self, name, chatID) -> None:
        self.name = name
        self.chatID = chatID
        self.data = {}
        self.types_credit = []
        self.types_debit = []
        
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def get_chat_id(self):
        return self.chatID

    def set_chat_id(self, chatID):
        self.chatID = chatID
        
    def get_types_credit(self):
        return self.types_credit
    
    def get_types_debit(self):
        return self.types_debit
        
    def append_types_credit(self, types):
        if type(types) == type([]):
            for i in types:
                self.types_credit.append(i)
                
            unique_types = set(self.types_credit)
            self.types = []
            for i in unique_types:
                if i != '':
                    self.types_credit.append(i)
        elif type(types) == type(''):
            if (types not in self.types_credit):
                if types != '':
                    self.types_credit.append(types)
        return self.types_credit
        
    def remove_types_credit(self, types):
        if type(types) == type([]):
            for i in types:
                if(i in self.types_credit):
                    self.types_credit.remove(i)
        elif type(types) == type(''):
            if(i in self.types_credit):
                self.types_credit.remove(types)
        return self.types_credit
    
    def append_types_debit(self, types):
        if type(types) == type([]):
            for i in types:
                self.types_debit.append(i)
                
            unique_types = set(self.types_debit)
            self.types = []
            for i in unique_types:
                if i != '':
                    self.types_debit.append(i)
        elif type(types) == type(''):
            if (types not in self.types_debit):
                if types != '':
                    self.types_debit.append(types)
        return self.types_debit
        
    def remove_types_debit(self, types):
        if type(types) == type([]):
            for i in types:
                if(i in self.types_debit):
                    self.types_debit.remove(i)
        elif type(types) == type(''):
            if(i in self.types_debit):
                self.types_debit.remove(types)
        return self.types_debit
    
    def get_data(self, index):
        return self.data[index]
    
    def set_data(self, index, value):
        self.data[index] = value
        
    def get_data_list(self):
        return self.data.values()
        
    def clear_data(self):
        self.data.clear()