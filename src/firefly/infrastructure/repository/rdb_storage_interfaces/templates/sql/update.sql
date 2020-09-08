{%- block update -%}
    update {% block fqtn %}{{ fqtn | sqlsafe }} {% endblock %} set

    {% block columns %}
        {%- for k, v in data.items() -%}
            "{{ k | sqlsafe }}"={{ v }}{% if not loop.last %},{% endif %}
        {%- endfor -%}
    {% endblock %}

    {% if criteria %}
        where
        {% import "sql/macros.sql" as macros %}
        {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
    {% endif %}
{%- endblock -%}