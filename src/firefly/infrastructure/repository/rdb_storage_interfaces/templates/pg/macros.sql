{% macro attribute(c, ids, other_hand) %}
    {% if c in ids %}
        {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
    {% elif other_hand is true or other_hand is false %}
        (document->>'{{ c | sqlsafe }}')::boolean
    {% else %}
        document->>'{{ c | sqlsafe }}'
    {% endif %}
{% endmacro %}

{% macro value(v, ids, other_hand) %}
    {{ v }}{% if other_hand in ids %}::uuid{% endif %}
{% endmacro %}