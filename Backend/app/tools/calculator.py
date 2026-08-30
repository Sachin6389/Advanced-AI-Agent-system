import ast
import operator as op

from langchain_core.tools import tool


ALLOWED_OPERATORS = {

    ast.Add: op.add,

    ast.Sub: op.sub,

    ast.Mult: op.mul,

    ast.Div: op.truediv,

    ast.Pow: op.pow,

    ast.Mod: op.mod,

    ast.USub: op.neg
}


def evaluate(node):

    if isinstance(
        node,
        ast.Constant
    ):

        if isinstance(
            node.value,
            (int, float)
        ):

            return node.value

    if isinstance(
        node,
        ast.BinOp
    ):

        operator = ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if not operator:

            raise ValueError(
                "Operator not allowed"
            )

        return operator(
            evaluate(node.left),
            evaluate(node.right)
        )

    if isinstance(
        node,
        ast.UnaryOp
    ):

        operator = ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if not operator:

            raise ValueError(
                "Operator not allowed"
            )

        return operator(
            evaluate(node.operand)
        )

    raise ValueError(
        "Invalid expression"
    )


@tool
def calculator(expression: str) -> str:
    """
    Safely calculate a mathematical expression.
    """

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = evaluate(
            tree.body
        )

        return str(result)

    except Exception as exc:

        return (
            f"Calculation failed: {exc}"
        )