{% macro attribute(c, ids) %}
    {% if c in ids %}
        {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
    {% else %}
        document->>'{{ c | sqlsafe }}'
    {% endif %}
{% endmacro %}

{% macro value(v, ids) %}
    {{ v }}{% if v is uuid %}::uuid{% endif %}
{% endmacro %}