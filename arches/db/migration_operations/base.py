from django.db.migrations.operations.base import Operation


class ArchesPackageMigration(Operation):
    reduces_to_sql = False
    reversible = True

    @staticmethod
    def localize_json(input, language_code):
        if isinstance(input, dict):
            if language_code in input:
                input = input[language_code]
            else:
                for key, value in input.items():
                    input[key] = ArchesPackageMigration.localize_json(value, language_code)
        elif isinstance(input, list):
            for item in input:
                ArchesPackageMigration.localize_json(item, language_code)
        return input

    def __init__(self, arg1, arg2):
        pass

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def describe(self):
        return "Custom Operation"

    @property
    def migration_name_fragment(self):
        return "custom_operation_%s_%s" % (self.arg1, self.arg2)
