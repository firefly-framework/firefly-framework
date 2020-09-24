{%- block update -%}
    update {% block fqtn %}{{ fqtn | sqlsafe }} {% endblock %} set

    {% block columns %}
        {%- for k, v in data.items() -%}
            {% if k not in ids %}
                {{ _q | sqlsafe }}{{ k | sqlsafe }}{{ _q | sqlsafe }}={% block update_value scoped %}{{ v }}{% endblock %}
                {% if not loop.last %},{% endif %}
            {% endif %}
        {%- endfor -%}
    {% endblock %}

    {% if criteria %}
        where
        {% import "sql/macros.sql" as macros %}
        {% block where_clause scoped %}{{ macros.where_clause(criteria, macros.default_attribute_macro, macros.default_value_macro, ids) }}{% endblock %}
    {% endif %}
{%- endblock -%}