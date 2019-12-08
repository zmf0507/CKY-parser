import nltk
from copy import deepcopy
from nltk.draw.tree import draw_trees
from nltk import tree, treetransforms
from nltk import Tree
from nltk.draw import TreeView, TreeWidget
from nltk.draw.util import CanvasFrame

grammarDict = {}

def loadGrammar():
	grammar = nltk.data.load("grammars/large_grammars/atis.cfg")
	# print(grammar)
	cnf = grammar.chomsky_normal_form(new_token_padding='@', flexible=False)
	# file = open("cnf.txt", "w")
	startSymbol = cnf.start()
	productions = cnf.productions()

	for production in productions:
		# file.write(str(production))
		prodRhs = ""
		for v in production.rhs():
			prodRhs+=str(v)+"," 
		if(prodRhs not in grammarDict):
			grammarDict[prodRhs] = []	
		grammarDict[prodRhs].append(str(production.lhs())) 
		grammarDict[prodRhs] = list(set(grammarDict[prodRhs]))
		# file.write("\n")

	return productions, startSymbol	


def getSingleTerminalProductions(word):
	# print(word)
	prods = grammar
	lhsList = []
	rProd = word + ","  
	if(rProd in grammarDict):
		lhsList = grammarDict[rProd]
	return lhsList		 

def getProductionsCombinations(lChildProductions, rChildProductions, i, k, j, backTrackList):
	lhsList = []
	backTrack = set()
	mainTuple = set()
	for lProd in lChildProductions:
		for rProd in rChildProductions:
			backTrack = set()
			rhsProd = lProd+","+rProd+","
			if(rhsProd in grammarDict):
				gList = grammarDict[rhsProd]
				lhsList += gList
				for nonTerminal in gList:
					if(nonTerminal not in backTrackList):
						backTrackList[nonTerminal] = set()
					backTrack.add((((i,k),(k+1,j),(lProd,rProd)))) 
					mainTuple = backTrackList[nonTerminal]
					mainTuple =  mainTuple.union(backTrack)
					backTrackList[nonTerminal] = mainTuple

	return list(set(lhsList)), backTrackList				

def getProductionsLHS(i, j,table):
	lhsList = []
	backTrackList = {}
	for k in range(i, j):
		lChildProductions = table[i][k]
		rChildProductions = table[k+1][j]
		prodList, backTrackList = getProductionsCombinations(lChildProductions, rChildProductions, i, k, j, backTrackList)
		lhsList = lhsList + prodList

	return list(set(lhsList)), backTrackList	


def getParseTreesCount(i, j, symbol):
	if(i==j):
		return 1, ["(" + symbol+"," +  sentence[0][i]+")"]
	count = 0
	trees = []
	children = backTrack[i][j][symbol]
	children = tuple(children)
	for child in children:
		childSymbols = child[2]
		lChild = child[0]
		rChild = child[1]
		LsubCount, LsubTree = getParseTreesCount(lChild[0], lChild[1], childSymbols[0])
		RsubCount, RsubTree = getParseTreesCount(rChild[0], rChild[1], childSymbols[1])
		# trees.append("")
		treeString = "("+symbol

		for lTree in  LsubTree:
			tSTring = ""
			for rTree in RsubTree:
				tSTring = "("+lTree+")" + "("+rTree+")"
				trees.append(treeString+tSTring+")")	

		# trees.append([symbol, LsubTree, RsubTree])
		count+= LsubCount*RsubCount
	return count, trees		

def performBackTrack(sentence):
	if (str(startSymbol) in table[0][len(sentence)-1]):
		print("PARSE-TREE EXISTS")
		# startIndex = table[0][len(sentence)-1].index(str(startSymbol))
		return getParseTreesCount(0,len(sentence)-1,'SIGMA')		
	else:
		return 0,[]	

def cyk(sentence):
	# print(sentence)
	size = len(sentence)
	table = [[[] for i in range(len(sentence))] for j in range(len(sentence))]
	backTrack = [[[] for i in range(len(sentence))] for j in range(len(sentence))]
	flag = 0
	for i in range(size):
		table[i][i] = getSingleTerminalProductions(sentence[i])
		if(len(table[i][i]) == 0):
			print("PARSE TABLE DOES NOT EXIST")
			flag = 1 
			break
		backTrack[i][i] = [sentence[i]]

	if(flag==1):
		return 0,0

	step = 1
	for i in range(size):
		for j in range(size-step):
			table[j][j+step], backTrack[j][j+step] = getProductionsLHS(j,j+step, table)	
		step+=1	
	return table, backTrack


grammar, startSymbol = loadGrammar()
sentences = nltk.data.load('grammars/large_grammars/atis_sentences.txt')
sentences = nltk.parse.util.extract_test_sentences(sentences)

count = 0
sentence = []
sentence.append([])
sentence[0].append(" ")

sentence[0] = "show availability ."

sentence[0] = sentence[0].split()
table, backTrack = cyk(sentence[0])
if(table==0):
	print("0")
else:	
	parseTreeCount , parseTree = performBackTrack(sentence[0])
	print(parseTreeCount)
	count = 0
	for tree in parseTree:
		count+=1
		cf = CanvasFrame()
		t = Tree.fromstring(tree)
		tc = TreeWidget(cf.canvas(),t)
		cf.add_widget(tc,10,10) # (10,10) offsets
		cf.print_to_file('tree'+str(count)+'.ps')	
		
# tree1 = ('SIGMA'('NP_NNS' ('ADJ_WPS', 'what'), ('NOUN_NNS', 'flights')), ('DECL_VB@NP_NNS' ('VERB_VB', 'leave'), ('DECL_VB@NP_NNS@VERB_VB', ('NP_NP' ('NP_NP' ('NOUN_NP' ('las', 'las') ('vegas', 'vegas')), ('PREP_IN', 'to']), ('NOUN_NP', 'oakland'), ('NP_NP' ('NOUN_NP' ('las', 'las') ('vegas', 'vegas']]], [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]]]], ['pt_char_per', '.']], ['DECL_VB@NP_NNS@VERB_VB', [['NP_NP', ['las', 'las'], ['vegas', 'vegas']]], [['DECL_VB@NP_NNS@VERB_VB@NP_NP', [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]], ['pt_char_per', '.']]]]]]]]]
# [['SIGMA', [['NP_NNS', ['ADJ_WPS', 'what'], ['NOUN_NNS', 'flights']]], [['DECL_VB@NP_NNS', ['VERB_VB', 'leave'], [['DECL_VB@NP_NNS@VERB_VB', [['NP_NP', [['NP_NP', [['NOUN_NP', ['las', 'las'], ['vegas', 'vegas']]], ['PREP_IN', 'to']]], ['NOUN_NP', 'oakland']], ['NP_NP', [['NOUN_NP', ['las', 'las'], ['vegas', 'vegas']]], [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]]]], ['pt_char_per', '.']], ['DECL_VB@NP_NNS@VERB_VB', [['NP_NP', ['las', 'las'], ['vegas', 'vegas']]], [['DECL_VB@NP_NNS@VERB_VB@NP_NP', [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]], ['pt_char_per', '.']]]]]]]]]
# [['SIGMA', [['NP_NNS', ['ADJ_WPS', 'what'], ['NOUN_NNS', 'flights']]], [['DECL_VB@NP_NNS', ['VERB_VB', 'leave'], [['DECL_VB@NP_NNS@VERB_VB', [['NP_NP', [['NP_NP', [['NOUN_NP', ['las', 'las'], ['vegas', 'vegas']]], ['PREP_IN', 'to']]], ['NOUN_NP', 'oakland']], ['NP_NP', [['NOUN_NP', ['las', 'las'], ['vegas', 'vegas']]], [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]]]], ['pt_char_per', '.']], ['DECL_VB@NP_NNS@VERB_VB', [['NP_NP', ['las', 'las'], ['vegas', 'vegas']]], [['DECL_VB@NP_NNS@VERB_VB@NP_NP', [['PP_NP', ['PREP_IN', 'to'], ['NOUN_NP', 'oakland']]], ['pt_char_per', '.']]]]]]]]]

# file = open("solutionParseTrees.txt", "w")
# for sentence in sentences:
# 	new = " "
# 	for x in sentence[0]: 
# 		new += x
# 		new+=" " 
# 		print(sentence[0])
# 		table, backTrack = cyk(sentence[0])
# 		parseTreeCount , parseTree = performBackTrack(sentence[0])
# 		print(parseTree)

		# file.write(new)
		# file.write("\t")
		# file.write(str(parseTreeCount))
		# file.write("\n")
	# count+=1
