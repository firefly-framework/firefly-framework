{% macro attribute(c, ids, other_hand, field_types) %}
    {% set c_str = c | string %}
    {% if c_str in ids or c_str == 'version' %}
        {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
    {% elif other_hand is true or other_hand is false %}
        (document->>'{{ c_str | sqlsafe }}')::boolean
    {% elif field_types[c_str] == 'datetime' %}
        ff_datetime(document->>'{{ c_str | sqlsafe }}')
    {% elif field_types[c_str] == 'date' %}
        ff_date(document->>'{{ c_str | sqlsafe }}')
    {% else %}
        {% if c.has_modifiers() %}
            {% for modifier in c.get_modifiers() %}{{ modifier | sqlsafe }}({% endfor %}
        {% endif %}
        document->>'{{ c_str | sqlsafe }}'
        {% if c.has_modifiers() %}
            {% for modifier in c.get_modifiers() %}){% endfor %}
        {% endif %}
    {% endif %}
{% endmacro %}

{% macro value(v, ids, other_hand) %}
    {%  set other_hand_str = other_hand | string %}
    {{ v }}{% if other_hand_str in ids and v is uuid %}::uuid{% endif %}
{% endmacro %}