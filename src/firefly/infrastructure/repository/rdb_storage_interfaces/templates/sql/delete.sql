{%- block delete -%}
    delete from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} where
    {% import "sql/macros.sql" as macros %}
    {% block where_clause scoped %}{{ macros.where_clause(criteria, macros.default_attribute_macro, macros.default_value_macro, ids, field_types) }}{% endblock %}
{%- endblock -%}