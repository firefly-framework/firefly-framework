{% macro where_clause(c, attribute_macro) %}
    {% set attribute_macro = attribute_macro | default(default_attribute_macro) %}
    {%- if c is criteria -%}
        {% if c.lhv is criteria %}({% endif %}{{ where_clause(c.lhv, attribute_macro) }}{% if c.lhv is criteria %}){% endif %}
    {%- endif -%}

    {% if c.op %}
        {% if c.op == '==' %}
            {{ "=" | sqlsafe }}
        {% elif c.op == 'startswith' %}
            like CONCAT({{ where_clause(c.rhv, attribute_macro) }}, "%")
        {% elif c.op == 'endswith' %}
            like CONCAT("%", {{ where_clause(c.rhv, attribute_macro) }})
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

    {%- if c.rhv and c.op not in ['startswith', 'endswith', 'is'] -%}
        {% if c.rhv is criteria %}({% endif %}{{ where_clause(c.rhv, attribute_macro) }}{% if c.rhv is criteria %}){% endif %}
    {%- endif -%}

    {% if c is not criteria %}
        {% if c is attribute %}
            {{ attribute_macro(c) }}
        {% elif c is iterable and c is not string %}
        (
            {% for i in c %}
            {{ i }}{% if not loop.last %},{% endif %}
            {% endfor %}
        )
        {%- else -%}
            {{ c }}
        {%- endif -%}
    {% endif %}
{% endmacro %}

{% macro default_attribute_macro(c) %}
    "{{ c | sqlsafe }}"
{% endmacro %}