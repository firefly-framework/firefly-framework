{% extends 'sql/delete.sql' %}
{% import 'pg/macros.sql' as pg_macros %}
{% block where_clause %}{{ macros.where_clause(criteria, pg_macros.attribute, pg_macros.value, ids, field_types) }}{% endblock %}
