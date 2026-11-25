"""CodeCity Academy: bounded interpreter for a documented subset of Python.

Python's AST parser supplies syntax; this evaluator never compiles or executes
student bytecode. Only explicit AST nodes and fictional lamp commands are allowed.
It cannot access imports, attributes, file handles, network or arbitrary calls.
"""
import ast
import json
import re
import sys
from pathlib import Path

MAX_SOURCE=4096
MAX_NODES=180
MAX_STEPS=500
MAX_INT=100000
MAX_OUTPUT=512
MAX_COMMANDS=16
IDENT=re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,31}\Z")
REQUEST_ID=re.compile(r"[a-f0-9]{32}\Z")


class LessonError(ValueError):
    pass


class ReturnValue(Exception):
    def __init__(self,value):self.value=value


class Interpreter:
    def __init__(self):
        self.env={}
        self.steps=0
        self.output=[]
        self.commands=[]
        self.lamps=[False,False]
        self.concepts=set()
        self.water=0
        self.functions={}
        self.in_function=False

    def tick(self):
        self.steps+=1
        if self.steps>MAX_STEPS:
            raise LessonError("Program exceeded the lesson step limit.")

    def value(self,v):
        if type(v) is int and abs(v)<=MAX_INT: return v
        if type(v) is bool: return v
        if type(v) is str and len(v)<=128: return v
        if type(v) is list and len(v)<=8 and all(type(x) in (int,bool,str) for x in v):
            return [self.value(x) for x in v]
        if type(v) is dict and len(v)<=8 and all(type(k) is str and len(k)<=32 and type(x) in (int,bool,str) for k,x in v.items()):
            return {k:self.value(x) for k,x in v.items()}
        raise LessonError("Use bounded scalar values, lists or dictionaries.")

    def expr(self,n):
        self.tick()
        if isinstance(n,ast.Constant): return self.value(n.value)
        if isinstance(n,ast.List):
            if len(n.elts)>8:raise LessonError("Use at most eight list items.")
            self.concepts.add("list")
            return self.value([self.expr(x) for x in n.elts])
        if isinstance(n,ast.Dict):
            if len(n.keys)>8 or any(k is None for k in n.keys):raise LessonError("Use at most eight dictionary entries.")
            keys=[self.expr(k) for k in n.keys]
            if any(type(k) is not str or len(k)>32 for k in keys):raise LessonError("Dictionary keys must be short strings.")
            self.concepts.add("dict")
            return self.value({k:self.expr(v) for k,v in zip(keys,n.values)})
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and not n.keywords:
            if n.func.id=="water_level" and not n.args:
                self.concepts.add("sensor")
                return self.water
            if n.func.id in self.functions:
                return self.call_function(n.func.id,[self.expr(a) for a in n.args])
        if isinstance(n,ast.Subscript):
            seq,index=self.expr(n.value),self.expr(n.slice)
            if type(seq) is dict:
                if type(index) is not str or index not in seq:raise LessonError("Unknown dictionary key.")
                self.concepts.add("key")
                return seq[index]
            if type(seq) is not list or type(index) is not int or not -len(seq)<=index<len(seq):
                raise LessonError("Use a valid integer list index.")
            self.concepts.add("index")
            return seq[index]
        if isinstance(n,ast.Name):
            if n.id not in self.env: raise LessonError("Unknown variable: "+n.id)
            return self.env[n.id]
        if isinstance(n,ast.UnaryOp):
            v=self.expr(n.operand)
            if isinstance(n.op,ast.Not): return not v
            if type(v) is int and isinstance(n.op,(ast.UAdd,ast.USub)):
                return self.value(-v if isinstance(n.op,ast.USub) else v)
        if isinstance(n,ast.BinOp):
            self.concepts.add("arithmetic")
            a,b=self.expr(n.left),self.expr(n.right)
            if isinstance(n.op,ast.Add) and type(a) is str and type(b) is str:
                return self.value(a+b)
            if type(a) is not int or type(b) is not int:
                raise LessonError("Arithmetic requires integers.")
            if isinstance(n.op,ast.Add):return self.value(a+b)
            if isinstance(n.op,ast.Sub):return self.value(a-b)
            if isinstance(n.op,ast.Mult):return self.value(a*b)
            if isinstance(n.op,ast.FloorDiv):return self.value(a//b)
            if isinstance(n.op,ast.Mod):return self.value(a%b)
        if isinstance(n,ast.Compare) and len(n.ops)==1:
            a,b=self.expr(n.left),self.expr(n.comparators[0])
            op=n.ops[0]
            if isinstance(op,ast.Eq):return a==b
            if isinstance(op,ast.NotEq):return a!=b
            if type(a) is int and type(b) is int:
                if isinstance(op,ast.Lt):return a<b
                if isinstance(op,ast.LtE):return a<=b
                if isinstance(op,ast.Gt):return a>b
                if isinstance(op,ast.GtE):return a>=b
        if isinstance(n,ast.BoolOp):
            self.concepts.add("boolean")
            if isinstance(n.op,ast.And):
                for item in n.values:
                    v=self.expr(item)
                    if not v:return v
                return v
            if isinstance(n.op,ast.Or):
                for item in n.values:
                    v=self.expr(item)
                    if v:return v
                return v
        raise LessonError("Expression not supported in this lesson.")

    def assign(self,target,value):
        if not isinstance(target,ast.Name) or not IDENT.fullmatch(target.id) or target.id in ("print","range","set_lamp","pump","water_level") or target.id in self.functions:
            raise LessonError("Choose a simple variable name.")
        if len(self.env)>=24 and target.id not in self.env:
            raise LessonError("Too many variables.")
        self.env[target.id]=self.value(value)

    def call_function(self,name,args):
        if self.in_function:raise LessonError("Nested or recursive function calls are not supported.")
        node=self.functions[name]
        if len(args)!=len(node.args.args):raise LessonError("Incorrect number of function arguments.")
        original=self.env
        self.env={param.arg:self.value(v) for param,v in zip(node.args.args,args)}
        self.in_function=True
        self.concepts.add("function")
        try:
            self.block(node.body)
        except ReturnValue as result:
            self.concepts.add("return")
            return result.value
        finally:
            self.env=original
            self.in_function=False
        raise LessonError("Functions must return a value.")

    def block(self,body):
        for n in body:
            self.tick()
            if isinstance(n,ast.FunctionDef):
                if self.in_function or n.name in self.functions or n.name in self.env:raise LessonError("Define each function once at top level.")
                self.functions[n.name]=n
            elif isinstance(n,ast.Return):
                if not self.in_function or n.value is None:raise LessonError("Return a value inside a function.")
                raise ReturnValue(self.expr(n.value))
            elif isinstance(n,ast.Assign) and len(n.targets)==1:
                self.assign(n.targets[0],self.expr(n.value))
                self.concepts.add("assignment")
            elif isinstance(n,ast.If):
                self.concepts.add("if")
                self.block(n.body if self.expr(n.test) else n.orelse)
            elif isinstance(n,ast.While) and not n.orelse:
                iterations=0
                while self.expr(n.test):
                    self.tick()
                    iterations+=1
                    if iterations>32:raise LessonError("Use at most 32 while iterations.")
                    self.concepts.add("while")
                    self.block(n.body)
            elif isinstance(n,ast.For) and not n.orelse:
                c=n.iter
                if not isinstance(c,ast.Call) or not isinstance(c.func,ast.Name) or c.func.id!="range" or c.keywords or not 1<=len(c.args)<=3:
                    raise LessonError("Use a for loop with range().")
                args=[self.expr(a) for a in c.args]
                if any(type(a) is not int for a in args):
                    raise LessonError("range() requires integers.")
                seq=range(*args)
                if len(seq)>32:raise LessonError("Use at most 32 loop iterations.")
                for value in seq:
                    self.concepts.add("for")
                    self.tick()
                    self.assign(n.target,value)
                    self.block(n.body)
            elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
                c=n.value
                if not isinstance(c.func,ast.Name) or c.keywords:
                    raise LessonError("Only lesson commands are allowed.")
                args=[self.expr(a) for a in c.args]
                if c.func.id=="print" and 1<=len(args)<=4:
                    line=" ".join(str(a) for a in args)
                    if len("\n".join(self.output+[line]))>MAX_OUTPUT:
                        raise LessonError("Output limit reached.")
                    self.output.append(line)
                    self.concepts.add("print")
                elif c.func.id=="set_lamp" and len(args)==2:
                    index,on=args
                    if type(index) is not int or index not in (0,1) or type(on) is not bool:
                        raise LessonError("set_lamp needs lamp 0 or 1 and True or False.")
                    if len(self.commands)>=MAX_COMMANDS:raise LessonError("Too many lamp commands.")
                    self.lamps[index]=on
                    self.commands.append({"lamp":index,"on":on})
                elif c.func.id=="pump" and len(args)==1:
                    units=args[0]
                    if type(units) is not int or not 1<=units<=20 or self.water+units>100:
                        raise LessonError("Pump 1 to 20 litres without exceeding 100.")
                    if len(self.commands)>=MAX_COMMANDS:raise LessonError("Too many equipment commands.")
                    self.water+=units
                    self.commands.append({"pump":units})
                    self.concepts.add("pump")
                else:raise LessonError("Only print(), set_lamp() and pump() are statement commands.")
            else:
                raise LessonError("Statement not supported in this lesson.")

    def run(self,source):
        if type(source) is not str or not 0<len(source.encode("utf-8"))<=MAX_SOURCE:
            raise LessonError("Enter up to 4096 bytes of Python.")
        try:tree=ast.parse(source,mode="exec")
        except (SyntaxError,ValueError,RecursionError) as e:raise LessonError("Python syntax error: "+str(e)[:160]) from None
        nodes=list(ast.walk(tree))
        if len(nodes)>MAX_NODES:raise LessonError("Program is too large.")
        # Fail closed even for unreachable statements. No attributes, imports,
        # functions, comprehensions, arbitrary calls or unbounded loops.
        allowed=(ast.Module,ast.Assign,ast.Name,ast.Store,ast.Load,ast.Constant,
                 ast.If,ast.For,ast.While,ast.List,ast.Dict,ast.Subscript,ast.FunctionDef,ast.arguments,ast.arg,ast.Return,ast.Expr,ast.Call,ast.BinOp,ast.UnaryOp,ast.Compare,
                 ast.BoolOp,ast.Add,ast.Sub,ast.Mult,ast.FloorDiv,ast.Mod,ast.UAdd,
                 ast.USub,ast.Not,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,
                 ast.And,ast.Or)
        defs=[n for n in nodes if isinstance(n,ast.FunctionDef)]
        reserved={"print","set_lamp","range","pump","water_level"}
        names={n.name for n in defs}
        if len(defs)>4 or len(names)!=len(defs):raise LessonError("Use at most four uniquely named functions.")
        for n in defs:
            a=n.args
            params=[p.arg for p in a.args]
            if n not in tree.body or not IDENT.fullmatch(n.name) or n.name in reserved or n.decorator_list or n.returns or getattr(n,"type_params",[]) or a.posonlyargs or a.kwonlyargs or a.vararg or a.kwarg or a.defaults or a.kw_defaults or len(params)>4 or len(set(params))!=len(params) or any(not IDENT.fullmatch(p.arg) or p.arg in reserved or p.annotation for p in a.args):
                raise LessonError("Use top-level functions with up to four simple parameters.")
        for n in nodes:
            if not isinstance(n,allowed):raise LessonError("Unsupported Python feature: "+type(n).__name__)
            if isinstance(n,ast.Call) and (not isinstance(n.func,ast.Name) or n.func.id not in reserved|names or n.keywords):
                raise LessonError("Only lesson commands and defined functions are available.")
        try:self.block(tree.body)
        except (ArithmeticError,ValueError,RecursionError) as e:raise LessonError(str(e)[:120]) from None
        return {"ok":True,"output":"\n".join(self.output),"commands":self.commands,
                "completed":all(self.lamps) and bool(self.output),"steps":self.steps,
                "concepts":sorted(self.concepts)}


def handle(request):
    if type(request) is not dict or set(request)!={"id","version","source"} or request["version"]!=1 or type(request["id"]) is not str or not REQUEST_ID.fullmatch(request["id"]):
        raise LessonError("Invalid lesson request.")
    try:result=Interpreter().run(request["source"])
    except (LessonError,UnicodeError) as exc:
        result={"ok":False,"output":str(exc)[:240],"commands":[],"completed":False,"steps":0,"concepts":[]}
    return {"id":request["id"],"version":1,**result}


def main():
    # Trusted launcher supplies exact two file paths; student source is data.
    if len(sys.argv)!=3:return 2
    source,dest=map(Path,sys.argv[1:])
    try:
        with source.open("rb") as stream:raw=stream.read(8193)
        if len(raw)>8192:raise LessonError("Request too large.")
        result=handle(json.loads(raw.decode("utf-8")))
        data=json.dumps(result,ensure_ascii=True,separators=(",",":"))
        if len(data)>4096:raise LessonError("Response too large.")
        temp=dest.with_suffix(".tmp")
        temp.write_text(data,encoding="utf-8")
        temp.replace(dest)
    except (OSError,ValueError,RecursionError):return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
