{% macro where_clause(c, attribute_macro, value_macro, ids, field_types, other_hand) %}
    {% set attribute_macro = attribute_macro | default(default_attribute_macro) %}
    {% set value_macro = value_macro | default(default_value_macro) %}
    {% if (c is criteria and c.lhv == 1 and c.rhv == 1 and c.op == '==') %}
        1=1
    {% else %}
        {%- if c is criteria -%}
            {% if c.lhv is criteria %}({% endif %}{{ where_clause(c.lhv, attribute_macro, value_macro, ids, field_types, c.rhv) }}{% if c.lhv is criteria %}){% endif %}
        {%- endif -%}

        {% if c is criteria %}
            {% if c.op == '==' %}
                =
            {% elif c.op == 'startswith' %}
                like CONCAT({{ where_clause(c.rhv, attribute_macro, value_macro, ids, field_types, c.lhv) }}, "%")
            {% elif c.op == 'endswith' %}
                like CONCAT("%", {{ where_clause(c.rhv, attribute_macro, value_macro, ids, field_types, c.lhv) }})
            {% elif c.op == 'is' %}
                {% if c.rhv is none or c.rhv == 'null' %}
                    is null
                {% elif c.rhv is true or c.rhv is false %}
                    {% block is_op %}is{% endblock %}
                {% endif %}

                {% if c.rhv is true %}
                    {% block is_true %}true{% endblock %}
                {% elif c.rhv is false %}
                    {% block is_false %}false{% endblock %}
                {% endif %}
            {% else %}
                {{ c.op | sqlsafe }}
            {% endif %}
        {% endif %}

        {%- if c is criteria and c.op not in ['startswith', 'endswith', 'is'] -%}
            {% if c.rhv is criteria %}({% endif %}{{ where_clause(c.rhv, attribute_macro, value_macro, ids, field_types, c.lhv) }}{% if c.rhv is criteria %}){% endif %}
        {%- endif -%}

        {% if c is not criteria %}
            {% if c is attribute %}
                {{ attribute_macro(c, ids, other_hand, field_types) }}
            {% elif c is iterable and c is not string %}
            (
                {% for i in c %}
                {{ value_macro(i, ids, other_hand) }}{% if not loop.last %},{% endif %}
                {% endfor %}
            )
            {%- else -%}
                {{ value_macro(c, ids, other_hand) }}
            {%- endif -%}
        {% endif %}
    {% endif %}
{% endmacro %}

{% macro default_attribute_macro(c, ids, other_hand, field_types) %}
    {{ _q | sqlsafe }}{{ c | string | sqlsafe }}{{ _q | sqlsafe }}
{% endmacro %}

{% macro default_value_macro(v, ids, other_hand) %}
    {{ v }}
{% endmacro %}