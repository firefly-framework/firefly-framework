{% macro attribute(c, ids, other_hand) %}
    {% set c_str = c | string %}
    {% if c_str in ids %}
        {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
    {% elif other_hand is true or other_hand is false %}
        (document->>'{{ c_str | sqlsafe }}')::boolean
    {% else %}
        document->>'{{ c_str | sqlsafe }}'
    {% endif %}
{% endmacro %}

{% macro value(v, ids, other_hand) %}
    {{ v }}{% if other_hand in ids and v is uuid %}::uuid{% endif %}
{% endmacro %}