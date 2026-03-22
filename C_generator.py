from parser.node import Node
from parser.node_type import NodeType
from lexer.token.token_type import TokenType

class CGenerator: 
    def __init__(self):
        self.code_func = []
        self.global_vars = {}
        self.func = {}
        self.main_body = []
        self.indent = 0 

    def generate(self, raiz: Node) -> str: 
        self.visit(raiz)
        return self._mount_final_code() 
    

    def visit(self, node: Node):
        if node is None: 
            return " " 
        type_node = node.tipo.value
        method = getattr (self, f"visit_{type_node}", self.visit_default )
        return method(node) 
    
    def visit_default(self, node: Node): 
        result = [] 
        for son in node.filhos:
            r = self.visit(son)
            if r: 
                result.append(r)
        return "\n".join(result)
    
## "VISITORS"

    def visit_PROGRAM(self, node: Node) -> str: 
        for son in node.filhos: 
            codigo = self.visit(son)
            # Se retorna código e não é função, adiciona ao main
            if codigo and codigo.strip():
                self.main_body.append(codigo)
        return ""

    
    def visit_BLOCK(self, node: Node) -> str: 
        result = [] 
        self._increase_indent() 

        for son in node.filhos: 
            code = self.visit(son)
            if code: 
                result.append(f"{self._indent()}{code}")

        self._reduce_indent() 
        return "\n".join(result)
    
    def visit_VAR_DECL(self, node: Node) -> str: 
        ident = node.filhos[0] 
        type_node = node.filhos[1]
        expr = node.filhos[2]

        name_var = ident.valor.valor
        type_var = type_node.valor.valor
        val_expr = self.visit(expr)

        self.global_vars[name_var] = type_var
        c_type = self._map_type(type_var)
        return f"{c_type} {name_var} = {val_expr};"
    

        
    def visit_ASSIGN_STMT(self, node: Node) -> str: 
        ident = node.filhos[0]
        expr = node.filhos[1]

        var_name = ident.valor.valor
        val_expr = self.visit(expr) 

        return f"{var_name} = {val_expr};"
    
    def visit_PRINT_STMT(self, node: Node) -> str: 
        expr = node.filhos[0]
        val = self.visit(expr)
        
        if expr.tipo == NodeType.LITERAL and expr.valor.tipo == TokenType.STRING_LITERAL:
            return f'printf("{val}\\n");'
        
        else: 
            return f'printf("%d\\n", {val});'
        
    def visit_IF_STMT(self, node:Node) -> str: 
        cond = node.filhos[0] 
        block_if = node.filhos[1]

        cond_str = self.visit(cond)
        body_if = self.visit(block_if) 

        result = f"if ({cond_str}) {{\n{body_if}\n{self._indent()}}}"

        if len(node.filhos) > 2: 
            block_else = node.filhos[2]
            body_else = self.visit(block_else)
            result += f" else {{\n{body_else}\n{self._indent()}}}"

        return result
    
    def visit_WHILE_STMT(self, node: Node) -> str: 
        cond = node.filhos[0]
        block = node.filhos[1] 

        cond_str = self.visit(cond) 
        body = self.visit(block) 

        return f"while ({cond_str}) {{\n{body}\n{self._indent()}}}"
    
    def visit_FUNCTION_DECL(self, node: Node) -> str: 
        ident = node.filhos[0]
        name_func = ident.valor.valor

        type_node = node.filhos[-2] 
        type_return = type_node.valor.valor 

        block = node.filhos[-1] 

        self.func[name_func] = type_return
        c_type = self._map_type(type_return)

        params_str = ""

        if len(node.filhos) > 3: 
            param_list = node.filhos[1] 
            param_strs = []

            for param in param_list.filhos: 
                param_indent = param.filhos[0]
                param_type_node = param.filhos[1]

                param_name = param_indent.valor.valor
                param_type = param_type_node.valor.valor
                c_param_type = self._map_type(param_type)

                param_strs.append(f"{c_param_type} {param_name}")

            params_str = ", ".join(param_strs)

        body = self.visit(block) 
        func_c = f"\n{c_type} {name_func}({params_str}) {{\n{body}\n}} \n"
        self.code_func.append(func_c)

        return ""
    

    def visit_RETURN_STMT(self, node: Node) -> str: 
        expr = node.filhos[0]
        valor = self.visit(expr) 

        return f"return {valor};"
    
    def visit_FUNCTION_CALL(self, node: Node) -> str:
        ident = node.filhos[0]
        name_func = ident.valor.valor
        argument = ""
        if len(node.filhos) > 1: 
            arg_list = node.filhos[1]
            arg_strs = [] 
            for arg in arg_list.filhos: 
                arg_str = self.visit(arg)
                arg_strs.append(arg_str)
                
            argument = ", ".join(arg_strs)
        return f"{name_func}({argument})"
    

    def visit_BINARY_OP(self, node: Node) -> str: 
        left = node.filhos[0]
        right = node.filhos[1]
        op = node.valor.tipo

        left_str = self.visit(left)
        right_str = self.visit(right) 
        op_str = self._convert_operator(op)

        return f"({left_str} {op_str} {right_str})"
    
    def visit_UNARY_OP(self, node: Node) -> str: 
        expr = node.filhos[0]
        op = node.valor.tipo
        
        expr_str = self.visit(expr)
        op_str = self._convert_operator(op)

        return f"({op_str}{expr_str})"
    

    def visit_IDENTIFIER(self, node: Node) -> str: 
        return node.valor.valor 
    
    def visit_LITERAL(self, node: Node) -> str: 
        type_token = node.valor.tipo
        value = node.valor.valor 

        if type_token == TokenType.STRING_LITERAL: 
            return value 
        elif type_token == TokenType.BOOLEAN_LITERAL: 
            return "1" if value.lower() == "true" else "0"
        else: 
            return str(value)
        
    def visit_TYPE_STMT(self, node:Node) -> str: 
        return ""
    

    def _map_type(self, tipo_mini_lang: str) -> str: 
        mapa_tipos = {
            "int": "int",
            "real": "float",
            "bool": "int",
            "void": "void",
            "string": "char*"
        }

        return mapa_tipos.get(tipo_mini_lang, "int")

    def _convert_operator(self, op_token:str) -> str: 
        map_ops = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-", 
            TokenType.MULTIPLY: "*",
            TokenType.DIVIDE: "/",
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!=",
            TokenType.LESS: "<",
            TokenType.GREATER: ">",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER_EQUAL: ">=",
            TokenType.AND: "&&",
            TokenType.OR: "||",
            TokenType.NOT: "!"
        }

        return map_ops.get(op_token, "")
    
    def _indent(self) -> str: 
        return "    " * self.indent
    
    def _increase_indent(self): 
        self.indent += 1

    def _reduce_indent(self): 
        if self.indent > 0: 
            self.indent -= 1

    def _mount_final_code(self) -> str: 
        resultado = [] 

        #includes 
        resultado.append("#include <stdio.h>")
        resultado.append("#include <stdlib.h>")
        resultado.append("")

        #Func
        for nome, tipo_ret in self.func.items():
            c_type = self._map_type(tipo_ret)
            resultado.append(f"{c_type} {nome}(/*params */);") 

        if self.func: 
            resultado.append("")

        for nome, tipo in self.global_vars.items(): 
            c_type = self._map_type(tipo)
            resultado.append(f"{c_type} {nome};")


        if self.global_vars: 
            resultado.append("")
        
        resultado.extend(self.code_func)

        resultado.append("int main() {")
        for linha_codigo in self.main_body:
            self.indent = 1
            resultado.append(f"{self._indent()}{linha_codigo}")
        resultado.append("    return 0;")
        resultado.append("}")
        
        return "\n".join(resultado)
    