'''
Program helps to find out cheapest rate of restaurant in city for the provided input items

'''
class Restaurants(object):
    def __init__(self):
        self.price = 0.0
        self.current_price = None
        self.sublist_price = 0.0 
        self.total_price = 0.0
        self.final_price = 0.0
        #These three variables are useful for final output
        self.feasible_solution = {}
        self.optimal_solution = False
        self.price_output = 0.0
    '''
    Create database from csv file.
    CAUTION: Make sure csv file is in current directory
    '''
    def create_database(self, filename):
        database = defaultdict(dict)
        with open(os.path.join(os.curdir, filename), 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                record = row[0].split(',')
                if record[0] not in database:
                    database[record[0]] = {}

                '''
                converting all items to tuple so can use items as dict key and price as
                value
                '''
                items = tuple([ i.strip() for i in record[2:]])
                record[1] = record[1].strip()
                database[record[0]][items] = record[1]
        return database
    
    def check_price(self, menu_dict=None, restaurant_id=None, input_data=None):
        self.best_price = None 
        backup = list(input_data)
        while backup : 
            if not sorted(list(set(input_data))) == sorted(list(input_data)): #if input contains repeated item
                if not backup.count(backup[0]) == len(backup): #if list not containing same repeated element
                    backup_input = set(backup)
                    '''
                    backup_input set should not be more than max size of item combo.
                    If it is, then remove individual costly item to reduce set length to max item combo size
                    In our case max combo size width is 3
                    '''
                    if len(list(set(backup_input)))>3: 
                        remove_element = self.excess_input(menu_dict, set(backup_input))
                        backup_input = list(set(backup_input))
                        backup_input.remove(remove_element[0])
     
                    self.final_price = self.best_option(menu_dict, set(backup_input))
                    
                    for item in set(backup_input):
                        backup.remove(item)
                    self.total_price = float(self.total_price) + float(self.final_price)
                   
                else:
                    '''
                    Here remaining list contains same element multiple times.
                    '''
                    count = backup.count(backup[0])
                    self.final_price = self.best_option(menu_dict, set(backup))
                    self.final_price = float(self.final_price)*float(count)
                    self.total_price = float(self.total_price) + float(self.final_price)
                   
                    break
            else:
                '''
                If input contains distinct item. No need to do extra processing. Just call best_option()
                to get optimum price
                '''
                self.total_price = 0.0
                self.final_price = self.best_option(menu_dict, backup)
                self.total_price = self.total_price + float(self.final_price)
                break

        return self.total_price

    '''
    Method responsible for finding best price for given input
    '''
    def best_option(self, menu_dict, input_data):
        self.best_price = None #Initialise best_price for current set of input
        if tuple(sorted(list((input_data)))) in menu_dict: #if exact input as key in menu_dict
            self.price = menu_dict[tuple(sorted(list((input_data))))]
            if not self.best_price:
                self.best_price = float(self.price)
            else:
                if float(self.best_price) > float(self.price):
                    self.best_price = float(self.price)

        if len(list(set(input_data))) > 1:
            for i in range(1, (len(menu_dict.keys())+1)):
                '''
                Apply brute force approch to calculate every possible combination of keys in menu_dict
                '''
                total_combination = list(itertools.combinations(menu_dict, i))
                
                for groups in total_combination:
                    current_members = set().union(*groups) # Finding unique element from the group through union
                    if sorted(list(input_data)) == sorted(list(current_members)): #If all input exist in union of groups
                        '''
                        Since this group has all the input element. Calculate its cost and compare with best_price
                        '''
                        self.current_price = sum(float(menu_dict[i]) for i in groups)
                        
                        if not self.best_price:
                            self.best_price = float(self.current_price)
                        else:
                            if float(self.best_price) > float(self.current_price):
                               self.best_price = float(self.current_price)
                    else:
                        '''
                        Now, since the Union of group element didn't exactly equal to input
                        (May be input has some extra element which is not in current group of combo)..
                        Therefore, find if our input is sublist of union of current group.
                        If it is, then calculate the cost
                        '''
                        sublist = self.is_sublist(list(input_data), list(current_members))
                        
                        if sublist:
                            for g in groups:
                                self.sublist_price = float(self.sublist_price) + float(menu_dict[g])

                            if not self.best_price:
                                self.best_price = float(self.sublist_price)
                            else:
                                if float(self.best_price) > float(self.sublist_price):
                                   self.best_price = float(self.sublist_price)
                                 
        else:
            '''
            In case, input is single element
            '''
            key = (input_data.pop(),)
            if key in menu_dict:
                return menu_dict[key]
        return self.best_price
    
    '''
    Method returns flag to indicate input_data is sublist of current combo items
    '''
    def is_sublist(self, input_list=None, currrent_group=None):
        flag = True
        for i in input_list:
            if i not in currrent_group:
                flag = False
        return flag
            
    '''
    Method responsible for filtering max cost individual element from
    set in case set has more element, than maximum item combo size.

    '''
    def excess_input(self, menu_dict=None, input_data=None):
        total_combination = list(itertools.combinations(menu_dict, 2))
        result_list = []
        value = None
        for groups in total_combination:
            current_members = set().union(*groups)
            largest_value = menu_dict[max(groups, key=len)]
            
            if sorted(list(input_data)) == sorted(list(current_members)): #If all input exist in union of groups
                if len(max(groups, key=len)) == 3 and len(min(groups, key=len)) == 1:
                    if not value:
                        value = largest_value
                        element = min(groups, key=len)
                    else:
                        if float(value) > float(largest_value):
                            value = float(largest_value)
                            element = min(groups, key=len)
        return element
    
    '''
    This method is only useful for helping to perform unittesting.
    '''
    def initialise_test1(self,filename,input_data):
        #call create_database to initialise restaurants data from csv file
        database = self.create_database(filename)
        for restaurant_id, items_dict in database.iteritems():
            process_data = database[restaurant_id]
            result = self.check_price(process_data, restaurant_id, input_data)
            self.feasible_solution.update({restaurant_id:result})
        if self.feasible_solution:
            self.optimal_solution = min(self.feasible_solution, key=self.feasible_solution.get)
            self.price_output = self.feasible_solution[self.optimal_solution]
        
        return (self.optimal_solution, self.price_output)

                
import unittest                
class InputTests(unittest.TestCase):
    def test_input1(self):
        input_data = ('i1',)
        obj1 = Restaurants()
        output = obj1.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',1.0))
    
    def test_input2(self):
        input_data = ('i2',)
        obj2 = Restaurants()
        output = obj2.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('2',1.9))

    def test_input3(self):
        input_data = ('i2','i3')
        obj3 = Restaurants()
        output = obj3.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',4.0))

    def test_input4(self):
        input_data = ('i1','i4')
        obj4 = Restaurants()
        output = obj4.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',5.0))

    def test_input5(self):
        input_data = ('i2','i4')
        obj5 = Restaurants()
        output = obj5.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('2',5.9))

    def test_input6(self):
        input_data = ('i3','i4')
        obj6 = Restaurants()
        output = obj6.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',6.5))

    def test_input7(self):
        input_data = ('i2','i3','i4')
        obj7 = Restaurants()
        output = obj7.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',8))

    def test_input8(self):
        input_data = ('i1','i2','i3','i4')
        obj8 = Restaurants()
        output = obj8.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('2',8.45))

    def test_input9(self):
        input_data = ('i1', 'i2', 'i2', 'i2', 'i3', 'i3', 'i3')
        obj9 = Restaurants()
        output = obj9.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',12.5))
     
    def test_input10(self):
        input_data = ('i1', 'i1', 'i1', 'i1', 'i1', 'i2', 'i3', 'i3', 'i3', 'i4', 'i4')
        obj10 = Restaurants()
        output = obj10.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',19.5))

    def test_input11(self):
        input_data = ('i1', 'i1', 'i1', 'i3', 'i4', 'i1', 'i3', 'i4', 'i4', 'i3', 'i4', 'i4', 'i4', 'i2', 'i3', 'i2', 'i3', 'i1', 'i2', 'i3', 'i1', 'i2', 'i3', 'i2', 'i2')
        obj11 = Restaurants()
        output = obj11.initialise_test1('input.csv', input_data)  
        self.assertEqual(output, ('1',54))

     
if __name__ == "__main__":
    import csv
    from collections import defaultdict
    import itertools
    import os
    
    suite = unittest.TestLoader().loadTestsFromTestCase(InputTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
