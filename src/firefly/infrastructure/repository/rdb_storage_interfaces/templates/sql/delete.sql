{%- block delete -%}
    delete from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} where
    {% import "sql/macros.sql" as macros %}
    {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
{%- endblock -%}