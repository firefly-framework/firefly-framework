{%- block delete -%}
    {% if not criteria %}
        truncate table {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}
    {% else %}
        delete from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} where
        {% import "sql/macros.sql" as macros %}
        {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
    {% endif %}
{%- endblock -%}