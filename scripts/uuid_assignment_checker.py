import uuid

from astroid import nodes
from astroid.bases import Instance
from astroid.util import Uninferable
from pylint.checkers import BaseChecker
from pylint.checkers.utils import safe_infer
from pylint.interfaces import INFERENCE, HIGH


def register(linter):
    linter.register_checker(UUIDAssignmentChecker(linter))


class UUIDAssignmentChecker(BaseChecker):
    name = "uuid-assignment"
    msgs = {
        "E2400": (
            "Direct assignment of a stringified UUID to a UUIDField produces undefined behavior.",
            "stringified-uuid-assignment",
            "The ORM expects model attributes to be assigned correct types. Either "
            "assign a UUID, or call .clean_fields() or .full_clean() afterward. Info:\n"
            "https://code.djangoproject.com/ticket/35434",
        ),
    }

    @staticmethod
    def is_django_model(inferred):
        return (
            isinstance(inferred, Instance)
            and any(klass.name == "Model" for klass in inferred.mro())
        )

    @staticmethod
    def looks_like_id_assignment(string_in):
        return string_in.endswith("id") or string_in == "pk"

    def check_value(self, value):
        inferred_value = safe_infer(value)
        if inferred_value is Uninferable:
            self.add_message("stringified-uuid-assignment", node=value.parent, confidence=INFERENCE)
        if not isinstance(inferred_value, nodes.Const):
            return
        try:
            uuid.UUID(inferred_value.value)
        except:
            pass
        else:
            self.add_message("stringified-uuid-assignment", node=value.parent, confidence=HIGH)

    def visit_call(self, call):
        inferred_result = safe_infer(call)
        if not self.is_django_model(inferred_result):
            return

        for kwarg in call.keywords:
            if hasattr(kwarg, "name") and self.looks_like_id_assignment(kwarg.name):
                # keyword argument
                self.check_value(kwarg.value)
            elif hasattr(kwarg, "arg"):
                if kwarg.arg is None:
                    # **kwargs
                    inferred_args = kwarg.value.inferred()[0]
                    if isinstance(inferred_args, nodes.Dict):
                        for inner_arg, inner_val in inferred_args.items:
                            if (
                                isinstance(inner_arg, nodes.Const)
                                and isinstance(inner_arg.value, str)
                                and self.looks_like_id_assignment(inner_arg.value)
                            ):
                                self.check_value(inner_val)
                elif self.looks_like_id_assignment(kwarg.arg):
                    # positional args
                    self.check_value(kwarg.value)

    def visit_assignattr(self, assignattr):
        if (
            self.looks_like_id_assignment(assignattr.attrname)
            and (inferred := safe_infer(assignattr.expr))
            and self.is_django_model(inferred)
        ):
            self.check_value(assignattr.parent.value)
