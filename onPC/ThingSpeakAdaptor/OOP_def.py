## OOP def

class Class(object):
	''' 
	Class is the class
	'''
	def __init__(self,cvar=3):
		'''
		__init__ is the construct to initialize the class Class;
		self is the implicit parameter of the Class and it must be always inserted;
		cvar is the class variable that has the same value in all the methods if not modified in the main.
		'''
		self.cvar=cvar # initialize the class variable in order to be used in all the methods


	def method(self, ivar):
		'''
		method is the method (the function);
		ivar is the instance variable and it takes the value given in the main;
		'''
		result=ivar+self.cvar
		return reusult

if __name__ == '__main__':
	x=Class()
	'''
	x is the instance - the object of the class Class create at run-time
	'''
	x.method(5)
	'''
	x.method is the calling method in the format object.methos(parameter)
	where the paramater is the instance variable
	'''