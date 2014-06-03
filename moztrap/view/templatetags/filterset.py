import json

from django import template

register = template.Library()


@register.tag
def filterset_to_json(parser, token):
    tokens = token.split_contents()
    var_name = tokens[1]
    options = {}
    if len(tokens) >= 3 and tokens[2] == "with":
        for option in tokens[3:]:
            try:
                key, value = option.split("=")
                if value.isdigit():
                    value = int(value)
                else:
                    value = value[1:-1]
            except ValueError:
                key, value = option, None
            options[key] = value
    return FiltersetToJSONNode(var_name, **options)


class FiltersetToJSONNode(template.Node):
    """Convert a form filterset to a big JSON string"""

    def __init__(self, filterset, **options):
        self.filterset = template.Variable(filterset)
        self.options = options

    def render(self, context):
        filterset = self.filterset.resolve(context)
        fields = []
        for field in filterset:
            field_struct = {
                "name": field.name,
                "options": [],
            }
            # additional keys potentially assigned to the fields
            for key in ("key", "cls", "switchable", "is_default_and"):
                if hasattr(field, key):
                    field_struct[key] = getattr(field, key)
            for option in field:
                field_struct["options"].append([
                    option.label,
                    option.selected,
                    option.value
                ])

            fields.append(field_struct)
        data = {
            "options": self.options,
            "fields": fields,
        }
        # JSON permits but does not require forward slashes to be escaped.
        # This is useful when json data is emitted in a <script> tag
        # in HTML, as it prevents </script> tags from prematurely terminating
        # the javscript. Some json libraries do this escaping by default,
        # although python's standard library does not, so we do it here.
        # http://stackoverflow.com/q/1580647/205832
        return json.dumps(data).replace("</", "<\\/")
