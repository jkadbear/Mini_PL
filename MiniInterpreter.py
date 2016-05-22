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

	def show_AST(self):
		print('father: ' + str(self.kind))
		for child in self.child_nodes:
			print(child.kind)
		for child in self.child_nodes:
			child.show_AST()

class Activity_Record:
	"""docstring for Activity_Record"""
	def __init__(self, access_link):
		self.access_link = access_link
		self.vars        = []
		self.funcs       = []

	def add_vars(self, ident):
		self.vars.append({'name': ident, 'value': 0})

	def add_func(self, node):
		# Func Node
		self.funcs.append({'name': node.child_nodes[0].ident, 'node': node})

	def set_vars(self, ident, num):
		var = next((iter for iter in self.vars if iter['name'] == ident), None)
		if var != None:
			var['value'] = num
		elif self.access_link != None:
			self.access_link.set_vars(ident, num)

	def get_val(self, node):
		# Id Node
		if node.constr_kind == Id:
			var = next((iter for iter in self.vars if iter['name'] == \
						 node.child_nodes[0].ident), None)
			if var != None:
				return var['value']
			elif self.access_link != None:
				return self.access_link.get_val(node)
			else:
				return None
		# Num Node or Print Node or Return Node
		elif node.constr_kind == Num or node.constr_kind == Print:
			return node.child_nodes[0].num
		# Exp Node
		else:
			return node.num

	def get_func(self, node):
		# AppFun Node
		fun = next((iter for iter in self.funcs if iter['name'] == \
						 node.child_nodes[0].ident), None)
		if fun != None:
			return (fun['node'], self)
		elif self.access_link != None:
			return self.access_link.get_func(node)
		else:
			return (None, None)

class Interpreter:
	"""
	Mini Programming Language Interpreter
	"""
	def __init__(self, filepath):
		self.filepath = filepath
		self.reader   = self.get_read()
		self.root     = None
		self.output   = []
		self.AR_stk   = []
		self.cur_AR   = Activity_Record(None)
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

	def run_node(self, AppNode, FunctionNode):
		"""
		run a function
		"""
		for L, P in zip(AppNode.child_nodes[1].child_nodes, FunctionNode.child_nodes[1].child_nodes):
			self.add_vars(P.ident)
			self.set_vars(P.ident, L.num)
		self.interpret(FunctionNode.child_nodes[2])
		return self.ret_val

	def add_AR(self, access_link):
		"""
		add new activity record
		"""
		self.cur_AR = Activity_Record(access_link)
		self.AR_stk.append(self.cur_AR)

	def add_vars(self, ident):
		self.cur_AR.add_vars(ident)

	def set_vars(self, ident, num):
		self.cur_AR.set_vars(ident, num)

	def get_val(self, node):
		return self.cur_AR.get_val(node)

	def add_func(self, node):
		self.cur_AR.add_func(node)

	def get_func(self, node):
		return self.cur_AR.get_func(node)

	def interpret(self, node):
		"""
		interpret a procedure or a sentence
		"""
		self.ret_val = 0
		if node.kind == EXPR:
			if node.constr_kind == Id or node.constr_kind == Num:
				node.num = self.get_val(node)
			elif node.constr_kind == Plus:
				self.interpret(node.child_nodes[0])
				self.interpret(node.child_nodes[1])
				node.num = self.get_val(node.child_nodes[0]) + \
							self.get_val(node.child_nodes[1])
			elif node.constr_kind == Minus:
				self.interpret(node.child_nodes[0])
				self.interpret(node.child_nodes[1])
				node.num = self.get_val(node.child_nodes[0]) - \
							self.get_val(node.child_nodes[1])
			elif node.constr_kind == Mult:
				self.interpret(node.child_nodes[0])
				self.interpret(node.child_nodes[1])
				node.num = self.get_val(node.child_nodes[0]) * \
							self.get_val(node.child_nodes[1])
			elif node.constr_kind == AppFun or node.constr_kind == RunFun:
				for subnode in node.child_nodes[1].child_nodes:
					self.interpret(subnode)
				(function, access_link) = self.get_func(node)
				self.add_AR(access_link)
				node.num = self.run_node(node, function)
		elif node.constr_kind == Pro:
			for subnode in node.child_nodes:
				self.interpret(subnode)
				if subnode.constr_kind == Return:
					break
		elif node.constr_kind == Func:
			self.add_func(node)
		elif node.constr_kind == Decl:
			for subnode in node.child_nodes:
				self.add_vars(subnode.ident)
		elif node.constr_kind == LetBe:
			self.interpret(node.child_nodes[1])
			self.set_vars(node.child_nodes[0].ident, self.get_val(node.child_nodes[1]))
		elif node.constr_kind == Read:
			self.set_vars(node.child_nodes[0].ident, next(self.reader))
		elif node.constr_kind == Print:
			self.interpret(node.child_nodes[0])
			self.do_write(self.get_val(node))
		elif node.constr_kind == Return:
			self.interpret(node.child_nodes[0])
			self.ret_val = self.get_val(node.child_nodes[0])

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
	# my_interpreter.root.show_AST()
