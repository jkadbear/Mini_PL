#!/usr/bin/env python3
"""MiniParser
Usage:
  MiniParser.py [PROGRAM]
  MiniParser.py -h | --help
  MiniParser.py --version

Options:
  -h --help     Show this screen
  --version     Show version
"""

from docopt import docopt

# node.kind, node type of AST
STR     = 0
DECL    = 1
PARA    = 2
EXPR    = 3
LIST    = 4
FUNC    = 5
STMT    = 6
PRO     = 7
NUM     = 8
ID      = 9
FUNNAME = 10
# node.constr_kind, branch node type of AST
Decl      = 11
Para      = 21
Num       = 31
Id        = 32
AppFun    = 33
Plus      = 34
Minus     = 35
Mult      = 36
List      = 41
Func      = 51
LetBe     = 61
RunFun    = 62
Return    = 63
Read      = 64
Print     = 65
Pro       = 71
FunName   = 101

term_kind = {'Decl': 11, 'Para': 21, 'Num': 31, 'Id': 32, 'AppFun': 33, 'Plus': 34, \
		'Minus': 35, 'Mult': 36, 'List': 41, 'Func': 51, 'LetBe': 61, 'RunFun': 62, \
		'Return': 63, 'Read': 64, 'Print': 65, 'Pro': 71, 'FunName': 101, 'End': None}


class Node:
	"""docstring for Node"""
	def __init__(self):
		self.kind        = None
		self.constr_kind = None
		self.num         = None
		self.ident       = None
		self.child_nodes = []
		self.closure     = None # used when constr_kind == FunName


class Closure:
	def __init__(self, access_link, func_node):
		self.access_link = access_link
		self.func_node   = func_node


class Activity_Record:
	"""docstring for Activity_Record"""
	def __init__(self, access_link):
		self.access_link = access_link
		self.vars        = []
		self.closures    = []

	def add_var(self, ident):
		self.vars.append({'name': ident, 'value': 0})

	def set_var(self, ident, num):
		var = next((iter for iter in self.vars if iter['name'] == ident), None)
		if var != None:
			var['value'] = num
		elif self.access_link != None:
			self.access_link.set_var(ident, num)

	def get_value(self, node):
		# Id Node
		if node.constr_kind == Id:
			var = next((iter for iter in self.vars if iter['name'] == \
						 node.child_nodes[0].ident), None)
			if var != None:
				return var['value']
			elif self.access_link != None:
				return self.access_link.get_value(node)
			else:
				return None
		# Num Node or Print Node or Return Node
		elif node.constr_kind == Num or node.constr_kind == Print \
				or node.constr_kind == Return:
			return node.child_nodes[0].num
		# Exp Node
		else:
			return node.num

	def add_closure(self, func_name, closure):
		# Func Node
		self.closures.append({'name': func_name, 'closure': closure})

	def get_closure(self, func_name):
		# AppFun Node or RunFun Node or FunName Node
		fun = next((iter for iter in self.closures if iter['name'] == \
						 func_name), None)
		if fun != None:
			return fun['closure']
		elif self.access_link != None:
			return self.access_link.get_closure(func_name)
		else:
			return None

	def set_closure(self, func_name, closure):
		# AppFun Node
		fun = next((iter for iter in self.closures if iter['name'] == \
						 func_name), None)
		if fun != None:
			fun['closure'] = closure
		else:
			self.closures.append({'name': func_name, 'closure': closure})


class Interpreter:
	"""
	Mini Programming Language Interpreter
	"""
	def __init__(self, filepath):
		self.filepath = filepath
		self.reader   = self.get_read()
		self.root     = None
		self.output   = []
		self.cur_AR   = Activity_Record(None)
		self.AR_stk   = [self.cur_AR]
		self.ret_val  = 0

	def get_item(self):
		with open(self.filepath) as f:
			for line in f:
				for item in line.split():
					yield item

	def get_read(self):
		with open('input.txt') as f:
			for line in f:
				for item in line.split():
					yield int(item)

	def do_write(self, value):
		self.output.append(value)

	def parse(self):
		term_stk = []
		for cur_term in self.get_item():
			node = Node()
			if cur_term == 'End':
				while term_stk[-1].kind > 0:
					node.child_nodes.insert(0, term_stk.pop())
				node.constr_kind = term_kind[term_stk.pop().ident]
				node.kind        = node.constr_kind // 10
				term_stk.append(node)
			else:
				if cur_term in term_kind.keys():
					node.kind  = STR
					node.ident = cur_term
					term_stk.append(node)
				elif cur_term.isdigit():
					node.kind = NUM
					node.num  = int(cur_term)
					term_stk.append(node)
				else:
					node.kind  = ID
					node.ident = cur_term
					term_stk.append(node)
		self.root = term_stk[-1]

	def add_AR(self, access_link):
		"""
		add new activity record
		"""
		self.cur_AR = Activity_Record(access_link)
		self.AR_stk.append(self.cur_AR)

	def add_var(self, ident):
		self.cur_AR.add_var(ident)

	def set_var(self, ident, num):
		self.cur_AR.set_var(ident, num)

	def get_value(self, node):
		return self.cur_AR.get_value(node)

	def add_closure(self, func_name, node):
		new_closure = Closure(self.cur_AR, node)
		self.cur_AR.add_closure(func_name, new_closure)

	def get_closure(self, func_name):
		return self.cur_AR.get_closure(func_name)

	def set_closure(self, func_name, closure):
		self.cur_AR.set_closure(func_name, closure)

	def run_node(self, appfun_node, func_node):
		"""
		run a function
		"""
		for L, P in zip(appfun_node.child_nodes[1].child_nodes, func_node.child_nodes[1].child_nodes):
			if P.constr_kind == FunName:
				self.set_closure(P.child_nodes[0].ident, L.closure)
			else:
				self.add_var(P.ident)
				self.set_var(P.ident, L.num)
		self.interpret(func_node.child_nodes[2])
		self.cur_AR = self.AR_stk[-2]
		self.AR_stk.pop()
		return self.ret_val

	def interpret(self, node):
		"""
		interpret a procedure or a sentence
		"""
		self.ret_val = 0
		if node.constr_kind == Id or node.constr_kind == Num:
			node.num = self.get_value(node)
		elif node.constr_kind == Plus:
			self.interpret(node.child_nodes[0])
			self.interpret(node.child_nodes[1])
			node.num = self.get_value(node.child_nodes[0]) + \
						self.get_value(node.child_nodes[1])
		elif node.constr_kind == Minus:
			self.interpret(node.child_nodes[0])
			self.interpret(node.child_nodes[1])
			node.num = self.get_value(node.child_nodes[0]) - \
						self.get_value(node.child_nodes[1])
		elif node.constr_kind == Mult:
			self.interpret(node.child_nodes[0])
			self.interpret(node.child_nodes[1])
			node.num = self.get_value(node.child_nodes[0]) * \
						self.get_value(node.child_nodes[1])
		elif node.constr_kind == AppFun or node.constr_kind == RunFun:
			for subnode in node.child_nodes[1].child_nodes:
				self.interpret(subnode)
			closure = self.get_closure(node.child_nodes[0].ident)
			self.add_AR(closure.access_link)
			node.num = self.run_node(node, closure.func_node)
		elif node.constr_kind == Pro:
			for subnode in node.child_nodes:
				self.interpret(subnode)
				if subnode.constr_kind == Return:
					break
		elif node.constr_kind == Func:
			self.add_closure(node.child_nodes[0].ident, node)
		elif node.constr_kind == Decl:
			for subnode in node.child_nodes:
				self.add_var(subnode.ident)
		elif node.constr_kind == LetBe:
			self.interpret(node.child_nodes[1])
			self.set_var(node.child_nodes[0].ident, self.get_value(node.child_nodes[1]))
		elif node.constr_kind == Read:
			self.set_var(node.child_nodes[0].ident, next(self.reader))
		elif node.constr_kind == Print:
			self.interpret(node.child_nodes[0])
			self.do_write(self.get_value(node))
		elif node.constr_kind == Return:
			self.interpret(node.child_nodes[0])
			self.ret_val = self.get_value(node)
		elif node.constr_kind == FunName:
			node.closure = self.get_closure(node.child_nodes[0].ident)

	def final_write(self):
		with open('output.txt', 'w') as f:
			for out in self.output:
				f.write(str(out) + ' ')


if __name__ == '__main__':
	args = docopt(__doc__, version='1.0')

	if(args['PROGRAM']):
		filepath = args['PROGRAM']
	else:
		filepath = 'program.txt'

	my_interpreter = Interpreter(filepath)
	my_interpreter.parse()
	my_interpreter.interpret(my_interpreter.root)
	my_interpreter.final_write()
