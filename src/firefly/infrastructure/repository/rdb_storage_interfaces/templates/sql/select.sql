{%- block select -%}

    select {% for column in columns %}
        "{{ column | sqlsafe }}"{% if not loop.last %},{% endif %}
    {% endfor %}

    from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}

    {% if criteria %}
        where
        {% import "sql/macros.sql" as macros %}
        {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
    {% endif %}
{%- endblock -%}