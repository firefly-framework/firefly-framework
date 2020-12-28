{% extends 'sql/insert.sql' %}
{% block insert_value %}
    {{ value }}{%- if column in ids and value is uuid -%}::uuid{% endif %}{% if column == 'document' %}::json{% endif %}
{% endblock %}
