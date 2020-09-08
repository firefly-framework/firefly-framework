{% macro attribute(c) %}
    document->'{{ c | sqlsafe }}'
{% endmacro %}