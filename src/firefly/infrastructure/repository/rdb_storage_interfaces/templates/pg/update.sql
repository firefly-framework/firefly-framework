{% extends 'sql/update.sql' %}
{% import 'pg/macros.sql' as pg_macros %}
{% block where_clause %}{{ macros.where_clause(criteria, pg_macros.attribute, pg_macros.value, ids) }}{% endblock %}
{% block update_value %}
    {{ v }}{%- if k in ids -%}::uuid{% endif %}{% if k == 'document' %}::json{% endif %}
{% endblock %}
