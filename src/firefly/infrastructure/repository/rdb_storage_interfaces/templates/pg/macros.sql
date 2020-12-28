{% macro attribute(c, ids) %}
    {% if c in ids %}
        {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
    {% else %}
        document->>'{{ c | sqlsafe }}'
    {% endif %}
{% endmacro %}

{% macro value(v, ids, other_hand) %}
    {{ v }}{% if other_hand in ids and v is uuid %}::uuid{% endif %}
{% endmacro %}