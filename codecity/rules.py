"""Validate a tiny finite grammar, then execute it using CPython.

No loops, attributes, imports, arbitrary names, mutation or access to builtins.
This is a restricted language, not an OS sandbox for general Python.
"""
import ast
from .model import Plant

class RuleError(ValueError):
    pass

def compile_rule(source):
    if not isinstance(source,str) or len(source)>2048:
        raise RuleError("Code is limited to 2048 characters.")
    try:
        tree=ast.parse(source,mode="exec")
    except (SyntaxError,ValueError,RecursionError) as exc:
        raise RuleError(str(exc)) from exc
    if sum(1 for _ in ast.walk(tree))>100:
        raise RuleError("Rule is too complex.")
    names={"moisture","light","temperature"}
    def operand(n):
        if isinstance(n,ast.Name) and n.id in names:
            return
        if isinstance(n,ast.Constant) and type(n.value) is int and 0<=n.value<=100:
            return
        raise RuleError("Use a sensor name or integer from 0 to 100.")
    def condition(n):
        if isinstance(n,ast.BoolOp) and isinstance(n.op,(ast.And,ast.Or)):
            for item in n.values: condition(item)
        elif isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.Not):
            condition(n.operand)
        elif isinstance(n,ast.Compare) and len(n.ops)==1 and isinstance(n.ops[0],(ast.Gt,ast.GtE,ast.Lt,ast.LtE,ast.Eq,ast.NotEq)):
            operand(n.left)
            operand(n.comparators[0])
        elif isinstance(n,ast.Constant) and type(n.value) is bool:
            return
        else:
            raise RuleError("Use comparisons joined by and, or, or not.")
    def block(nodes,depth=0):
        if depth>5 or len(nodes)!=1:
            raise RuleError("Each branch needs exactly one action or nested if.")
        n=nodes[0]
        if isinstance(n,ast.If):
            condition(n.test)
            block(n.body,depth+1)
            block(n.orelse,depth+1)
        elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
            c=n.value
            if not (isinstance(c.func,ast.Name) and c.func.id=="irrigate" and not c.keywords and len(c.args)==1 and isinstance(c.args[0],ast.Constant) and type(c.args[0].value) is bool):
                raise RuleError("Use irrigate(True) or irrigate(False).")
        else:
            raise RuleError("Only if/elif/else and irrigation actions are supported.")
    if len(tree.body)!=1 or not isinstance(tree.body[0],ast.If):
        raise RuleError("Start with an if statement and include an else.")
    block(tree.body)
    return compile(tree,"<greenhouse>","exec")

def evaluate(source,state:Plant):
    code=compile_rule(source)
    result=[]
    def irrigate(value):
        result.append(value)
    exec(code,{"__builtins__":{}},{"moisture":state.moisture,"light":state.light,"temperature":state.temperature,"irrigate":irrigate})
    return result[0]
