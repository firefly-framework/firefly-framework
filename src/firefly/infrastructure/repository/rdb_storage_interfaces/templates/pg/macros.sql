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

{% macro document(relationships, counter) %}
    {% for k, v in relationships.items() %}
        {% set counter = counter | default(1) %}

        {% if loop.first %}
            jsonb_set(
                {% set remaining = relationships.copy() %}
                {% set _ = remaining.pop(k) %}
                {% if remaining.items()|length > 0 %}
                    {{ document(remaining, counter) }},
                {% else %}
                    document,
                {% endif %}

                '{ {{ k | sqlsafe }} }',

                {% if v['this_side'] == 'many' %}
                    (select json_agg(
                    {% if v['relationships'].keys()|length > 0 %}
                        {{ document(v['relationships'], counter + 1) }}
                    {% else %}
                        document
                    {% endif %}
                    )::jsonb from {{ v['fqtn'] | sqlsafe }} _{{ counter | sqlsafe }} where {{ v['target'].id_name() | sqlsafe }}::text in (select jsonb_array_elements_text(_{{ (counter - 1) | sqlsafe }}.document->'{{ k | sqlsafe }}')))
                {% else %}
                    (select document from {{ v['fqtn'] | sqlsafe }} _{{ counter | sqlsafe }} where {{ v['target'].id_name() | sqlsafe }} = (_{{ (counter - 1) | sqlsafe }}.document->>'{{ k | sqlsafe }}'){% if v['is_uuid'] %}::uuid{% endif %})
                {% endif %}
            )
        {% endif %}
    {% endfor %}
{% endmacro %}

{% macro value(v, ids, other_hand) %}
    {%  set other_hand_str = other_hand | string %}
    {{ v }}{% if other_hand_str in ids and v is uuid %}::uuid{% endif %}
{% endmacro %}